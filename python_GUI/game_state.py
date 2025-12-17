import pygame
import random
import sys
import os
from config import *

# Assumes ASSETS_DIR is defined in your main file or config, 
# otherwise define it here if needed:
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(CURRENT_DIR, 'asset')

class GameState:
    """
    Manages the game logic, state transitions, and hardware synchronization.
    This class acts as the 'Controller' in the MVC pattern.
    """
    def __init__(self, serial_manager):
        self.serial = serial_manager
        self.state = STATE_MENU
        self.previous_state = STATE_MENU 
        self.score = 0
        self.lives = 10
        self.difficulty = MODE_EASY
        
        # --- MULTIPLAYER VARIABLES ---
        self.is_multiplayer = False 
        self.current_player = 1
        self.p1_score = 0
        self.p2_score = 0
        self.start_time = 0  # Timestamp for tracking game duration
        # -----------------------------

        self.hit_delay_duration = 500
        
        # --- HAMMER ANIMATION STATE ---
        self.is_hammering = False       
        self.hammer_target_index = -1   
        self.hammer_start_time = 0      
        self.hammer_duration = HAMMER_SWING_DURATION
        
        # --- BONUS ---
        self.consecutive_hits = 0 
        
        # --- AUDIO INIT ---
        try:
            # Load background music and sound effects
            pygame.mixer.music.load(os.path.join(ASSETS_DIR, 'Menu.wav')) 
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1) # Loop indefinitely
            
            self.snd_hit = pygame.mixer.Sound(os.path.join(ASSETS_DIR, 'hit.wav'))
            self.snd_miss = pygame.mixer.Sound(os.path.join(ASSETS_DIR, 'miss.wav'))
            self.snd_over = pygame.mixer.Sound(os.path.join(ASSETS_DIR, 'game-over.wav'))
            self.snd_hit.set_volume(0.6)
            self.snd_miss.set_volume(0.4)
            self.snd_over.set_volume(0.5)
        except Exception as e:
            self.snd_hit = None
            self.snd_miss = None
            self.snd_over = None
            print(f"[AUDIO] Warning: {e}")

        # --- GAME LOGIC VARIABLES ---
        self.pot_value = 0
        self.last_stable_pot = 0 
        
        self.current_mole_index = -1
        self.whacked_mole_index = -1
        self.whacked_height_ratio = 1.0 
        
        self.is_hiding = False
        self.hide_duration = 300
        
        self.spawn_interval = 2000
        self.last_spawn_time = 0
        self.game_over_selection = 0 
        
        self.pause_selection = 0   
        self.pause_start_time = 0
        
        self.waiting_for_next_mole = False
        self.hit_time = 0

        # --- INIT HARDWARE ---
        # Sync initial state with PIC (Red LED, Score 0)
        self.serial.send('E') 
        self.serial.send('\nSCR:0\n')

    def get_speed(self):
        """
        Calculates the spawn speed based on difficulty and current score.
        """
        # Multiplayer uses a fixed fast speed
        if self.is_multiplayer: return 1500

        base_speed = 1500 
        if self.difficulty == MODE_EASY: return 1500 
        elif self.difficulty == MODE_MEDIUM:
            # Increase speed as score increases
            return max(800, base_speed - (self.score * 50))
        elif self.difficulty == MODE_HARD:
            return max(300, base_speed - (self.score * 80))
        return 1500

    def spawn_mole(self):
        """ Selects a random hole to spawn a mole. """
        self.current_mole_index = random.randint(0, 8)
        self.spawn_interval = self.get_speed()
        self.last_spawn_time = pygame.time.get_ticks()
        self.is_hiding = False
        self.whacked_height_ratio = 1.0 

    def stop_game(self):
        """ Stops the game logic and handles transition (GameOver or Next Player). """
        if self.is_multiplayer:
            self.handle_player_finish()
        else:
            self.state = STATE_GAMEOVER
            self._reset_game_state()
            if self.snd_over: self.snd_over.play()

    def _reset_game_state(self):
        """ Helper to reset temporary game variables without changing the screen. """
        self.current_mole_index = -1
        self.whacked_mole_index = -1
        self.is_hiding = False
        self.consecutive_hits = 0 
        self.serial.send('E') # Turn LED Red

    def handle_player_finish(self):
        """ Handles the transition between players in Multiplayer mode. """
        self._reset_game_state()
        
        if self.current_player == 1:
            self.p1_score = self.score
            self.state = STATE_WAITING_P2
            print(f"P1 Finished. Score: {self.p1_score}")
        else:
            self.p2_score = self.score
            self.state = STATE_WINNER
            print(f"P2 Finished. Score: {self.p2_score}")
            if self.snd_over: self.snd_over.play()

    def start_next_player(self):
        """ Prepares the game for Player 2. """
        self.current_player = 2
        self.score = 0
        self.lives = 3 
        self.start_time = pygame.time.get_ticks()
        self.state = STATE_PLAYING
        self.serial.send('G')     
        self.serial.send('\nSCR:0\n')
        self.spawn_mole()

    def cleanup(self):
        """ Sends exit signal to hardware before closing. """
        self.serial.send('X') 
        print("[SERIAL] Sent exit signal 'X'")
        
    def toggle_pause(self):
        """ Toggles between Playing and Paused states. """
        if self.state == STATE_PAUSED:
            self.state = self.previous_state
            self.serial.send('G')
            
            # Adjust timers so pause duration doesn't count towards spawn time
            pause_duration = pygame.time.get_ticks() - self.pause_start_time
            self.last_spawn_time += pause_duration
            self.hit_time += pause_duration
            self.start_time += pause_duration # Extend game timer
            
            self.last_stable_pot = self.pot_value
        else:
            if self.state == STATE_PLAYING:
                self.previous_state = self.state
                self.state = STATE_PAUSED
                self.serial.send('P') # Turn LED Yellow
                self.pause_selection = 0 
                self.pause_start_time = pygame.time.get_ticks()

    def handle_hit(self, hit_index):
        """ Logic when a button input is received. """
        if self.state != STATE_PLAYING: return
        if self.waiting_for_next_mole: return 

        current_time = pygame.time.get_ticks()

        # Trigger Hammer Animation
        self.is_hammering = True
        self.hammer_target_index = hit_index
        self.hammer_start_time = current_time
        
        if hit_index == self.current_mole_index:
            # --- HIT ---
            if self.snd_hit: self.snd_hit.play()
            self.score += 1
            self.serial.send(f"SCR:{self.score}\n") # Update Score on PIC

            # Bonus Life (Standard Rule)
            self.consecutive_hits += 1
            if self.consecutive_hits >= 10:
                self.lives += 1
                self.consecutive_hits = 0 
                print("[GAMEPLAY] Bonus Life!")

            # Check if hit while hiding (partial hit logic)
            time_elapsed = current_time - self.last_spawn_time
            retreat_start_time = self.spawn_interval - self.hide_duration
            
            if time_elapsed > retreat_start_time:
                time_into_retreat = time_elapsed - retreat_start_time
                retreat_progress = time_into_retreat / self.hide_duration
                self.whacked_height_ratio = max(0.0, 1.0 - retreat_progress)
            else:
                self.whacked_height_ratio = 1.0 

            self.whacked_mole_index = self.current_mole_index 
            self.current_mole_index = -1 
            self.waiting_for_next_mole = True
            self.hit_time = current_time
        else:
            # --- MISS ---
            if self.snd_miss: self.snd_miss.play()
            # Note: Lives logic can be added here if needed for Single Player
    
    def update(self):
        """ Main game loop update. """
        current_time = pygame.time.get_ticks()

        if self.state == STATE_PAUSED:
            self.pause_selection = 0 if self.pot_value < 512 else 1
            return 

        # --- MENU LOGIC (5 SECTIONS) ---
        if self.state == STATE_MENU:
            # Divide Potentiometer range (0-1023) into 5 sections
            if self.pot_value < 205: 
                self.difficulty = MODE_EASY
                self.is_multiplayer = False
            elif self.pot_value < 410: 
                self.difficulty = MODE_MEDIUM
                self.is_multiplayer = False
            elif self.pot_value < 615: 
                self.difficulty = MODE_HARD
                self.is_multiplayer = False
            elif self.pot_value < 820: 
                self.difficulty = MODE_MULTIPLAYER 
                self.is_multiplayer = True 
            else: 
                self.difficulty = MENU_QUIT 
                self.is_multiplayer = False

        elif self.state == STATE_PLAYING:
            
            # --- MULTIPLAYER TIMER CHECK ---
            if self.is_multiplayer:
                if current_time - self.start_time >= GAME_DURATION:
                    self.stop_game() 
                    return
            
            # --- MOLE SPAWN LOGIC ---
            if self.waiting_for_next_mole:
                if current_time - self.hit_time > self.hit_delay_duration:
                    self.waiting_for_next_mole = False
                    self.whacked_mole_index = -1 
                    self.spawn_mole()
            else:
                time_elapsed = current_time - self.last_spawn_time
                
                # 1. Timeout (Missed the mole)
                if time_elapsed > self.spawn_interval:
                    self.is_hiding = False
                    if self.current_mole_index != -1:
                        self.lives -= 1
                        self.consecutive_hits = 0 
                        
                        if self.lives <= 0: self.stop_game()
                        else: self.spawn_mole()

                # 2. Hiding Animation
                elif time_elapsed > (self.spawn_interval - self.hide_duration):
                    self.is_hiding = True
                else:
                    self.is_hiding = False

        elif self.state in [STATE_GAMEOVER, STATE_WINNER]:
            self.game_over_selection = 0 if self.pot_value < 512 else 1

    def process_input(self, line):
        """
        Parses commands received from the PIC Microcontroller.
        Example commands: "POT:512", "BTN:3", "BTN:CONFIRM"
        """
        if line.startswith("POT:"):
            try: 
                new_val = int(line.split(":")[1])
                # Feature: Auto-Pause if pot is moved rapidly during game
                if self.state == STATE_PLAYING:
                    if abs(new_val - self.last_stable_pot) > 30:
                        self.toggle_pause()
                
                self.pot_value = new_val
                
                # Update stable pot only if not in menu/intermission
                if self.state not in [STATE_MENU, STATE_GAMEOVER, STATE_WINNER, STATE_WAITING_P2]:
                    self.last_stable_pot = new_val
            except: pass

        elif "BTN:CONFIRM" in line:
            if self.state == STATE_MENU:
                if self.difficulty == MENU_QUIT:
                    self.serial.send('X') 
                    pygame.quit(); sys.exit()
                else:
                    # START NEW GAME
                    self.score = 0
                    self.lives = 3 # Reset lives
                    self.consecutive_hits = 0 
                    self.state = STATE_PLAYING
                    
                    if self.is_multiplayer:
                        self.current_player = 1
                        self.p1_score = 0
                        self.p2_score = 0
                        self.start_time = pygame.time.get_ticks()
                    
                    self.serial.send('G')     
                    self.serial.send('\nSCR:0\n')
                    self.last_stable_pot = self.pot_value
                    self.spawn_mole()
                
            elif self.state == STATE_PLAYING:
                self.toggle_pause()
                
            elif self.state == STATE_PAUSED:
                if self.pause_selection == 0:
                    self.toggle_pause() 
                else:
                    self.state = STATE_MENU
                    self._reset_game_state()
                    self.serial.send('\nSCR:0\n') 
                
            elif self.state == STATE_GAMEOVER:
                if self.game_over_selection == 0: 
                    self.state = STATE_MENU
                    self._reset_game_state()
                    self.serial.send('\nSCR:0\n') 
                else: 
                    self.serial.send('X') 
                    pygame.quit(); sys.exit()

            # --- NEW STATE HANDLING ---
            elif self.state == STATE_WAITING_P2:
                self.start_next_player()

            elif self.state == STATE_WINNER:
                if self.game_over_selection == 0: # Play Again
                    self.state = STATE_MENU
                    self._reset_game_state()
                    self.serial.send('\nSCR:0\n')
                else: # Quit
                    self.serial.send('X')
                    pygame.quit(); sys.exit()

        elif line.startswith("BTN:"):
            # Ignore buttons during Pause or Transitions
            if self.state == STATE_PAUSED: return
            if self.state in [STATE_WAITING_P2, STATE_WINNER]: return 
            
            try:
                idx = int(line.split(":")[1])
                if 0 <= idx <= 8:
                    self.handle_hit(idx)
            except: pass