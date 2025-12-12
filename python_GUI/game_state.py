import pygame
import random
import sys
from config import *

class GameState:
    def __init__(self, serial_manager):
        self.serial = serial_manager
        self.state = STATE_MENU
        self.previous_state = STATE_MENU 
        self.score = 0
        self.lives = 3
        self.difficulty = MODE_EASY
        
        self.pot_value = 0
        self.last_stable_pot = 0 
        
        self.current_mole_index = -1
        self.spawn_interval = 2000
        self.last_spawn_time = 0
        self.game_over_selection = 0 
        
        self.pause_selection = 0   
        self.pause_start_time = 0
        
        self.waiting_for_next_mole = False
        self.hit_time = 0
        self.hit_delay_duration = 500
        
        # --- INIT HARDWARE ---
        self.serial.send('E')       # Red LED (Menu Mode)
        self.serial.send('\nSCR:0\n') # Reset Score Display to 0

    def get_speed(self):
        base_speed = 1500 
        if self.difficulty == MODE_EASY: return 1500 
        elif self.difficulty == MODE_MEDIUM:
            return max(800, base_speed - (self.score * 50))
        elif self.difficulty == MODE_HARD:
            return max(300, base_speed - (self.score * 80))
        return 1500

    def spawn_mole(self):
        self.current_mole_index = random.randint(0, 8)
        self.spawn_interval = self.get_speed()
        self.last_spawn_time = pygame.time.get_ticks()

    def stop_game(self):
        self.state = STATE_GAMEOVER
        self.current_mole_index = -1
        self.serial.send('E') # Red LED (Game Over)
        # Note: We keep the final score displayed here so the user can see it.
        # We reset it only when they go back to the menu.

    def toggle_pause(self):
        if self.state == STATE_PAUSED:
            # UNPAUSE -> GREEN
            self.state = self.previous_state
            self.serial.send('G') # Green LED
            
            pause_duration = pygame.time.get_ticks() - self.pause_start_time
            self.last_spawn_time += pause_duration
            self.hit_time += pause_duration
            self.last_stable_pot = self.pot_value
            
        else:
            # PAUSE -> YELLOW
            if self.state == STATE_PLAYING:
                self.previous_state = self.state
                self.state = STATE_PAUSED
                self.serial.send('P') # Yellow LED
                self.pause_selection = 0 
                self.pause_start_time = pygame.time.get_ticks()

    def handle_hit(self, hit_index):
        if self.state != STATE_PLAYING: return
        if self.waiting_for_next_mole: return 

        if hit_index == self.current_mole_index:
            self.score += 1
            
            # UPDATE SCORE
            self.serial.send(f"SCR:{self.score}\n")

            self.current_mole_index = -1 
            self.waiting_for_next_mole = True
            self.hit_time = pygame.time.get_ticks()
        else:
            self.lives -= 1
            if self.lives <= 0: self.stop_game()

    def update(self):
        current_time = pygame.time.get_ticks()

        if self.state == STATE_PAUSED:
            self.pause_selection = 0 if self.pot_value < 512 else 1
            return 

        if self.state == STATE_MENU:
            if self.pot_value < 341: self.difficulty = MODE_EASY
            elif self.pot_value < 682: self.difficulty = MODE_MEDIUM
            else: self.difficulty = MODE_HARD

        elif self.state == STATE_PLAYING:
            if self.waiting_for_next_mole:
                if current_time - self.hit_time > self.hit_delay_duration:
                    self.waiting_for_next_mole = False
                    self.spawn_mole()
            else:
                if current_time - self.last_spawn_time > self.spawn_interval:
                    if self.current_mole_index != -1:
                        self.lives -= 1
                        if self.lives <= 0: self.stop_game()
                        else: self.spawn_mole()

        elif self.state == STATE_GAMEOVER:
            self.game_over_selection = 0 if self.pot_value < 512 else 1

    def process_input(self, line):
        
        # 1. POTENTIOMETER
        if line.startswith("POT:"):
            try: 
                new_val = int(line.split(":")[1])
                if self.state == STATE_PLAYING:
                    if abs(new_val - self.last_stable_pot) > 30:
                        self.toggle_pause()
                self.pot_value = new_val
                if self.state != STATE_PLAYING and self.state != STATE_PAUSED:
                    self.last_stable_pot = new_val
            except: pass

        # 2. CONFIRM BUTTON (RB0)
        elif "BTN:CONFIRM" in line:
            if self.state == STATE_MENU:
                self.score = 0; self.lives = 3
                self.state = STATE_PLAYING
                self.serial.send('G')     
                self.serial.send('\nSCR:0\n') # Ensure 0 on Start
                self.last_stable_pot = self.pot_value
                self.spawn_mole()
                
            elif self.state == STATE_PLAYING:
                self.toggle_pause()
                
            elif self.state == STATE_PAUSED:
                if self.pause_selection == 0:
                    self.toggle_pause() 
                else:
                    self.state = STATE_MENU
                    self.serial.send('E') 
                    self.serial.send('\nSCR:0\n') # Reset Score when quitting to menu
                    self.current_mole_index = -1
                
            elif self.state == STATE_GAMEOVER:
                if self.game_over_selection == 0: 
                    # RESTART SELECTED
                    self.state = STATE_MENU
                    self.serial.send('E') 
                    
                    # --- NEW: RESET SCORE DISPLAY ---
                    self.serial.send('\nSCR:0\n') 
                    # --------------------------------
                else: 
                    self.serial.send('X') 
                    pygame.quit(); sys.exit()

        # 3. GAME BUTTONS (0-8)
        elif line.startswith("BTN:"):
            if self.state == STATE_PAUSED: return
            try:
                idx = int(line.split(":")[1])
                if 0 <= idx <= 8:
                    self.handle_hit(idx)
            except: pass