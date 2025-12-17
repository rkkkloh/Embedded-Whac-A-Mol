import pygame
import os
import math
from config import *

# --- PATH SETTINGS ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(CURRENT_DIR, 'asset')

# --- ASSET CACHE ---
assets = {}
fonts = {}

def init_resources():
    """ Load images and fonts if not already loaded. """
    if 'initialized' in assets: return

    pygame.font.init()
    try:
        fonts['normal'] = pygame.font.SysFont("Chalkboard SE", 32, bold=True)
        fonts['large'] = pygame.font.SysFont("Chalkboard SE", 64, bold=True)
        fonts['ui'] = pygame.font.SysFont("Arial Rounded MT Bold", 24)
    except:
        fonts['normal'] = pygame.font.SysFont("Arial", 32)
        fonts['large'] = pygame.font.SysFont("Arial", 64)
        fonts['ui'] = pygame.font.SysFont("Arial", 24)

    def load_img(name, size=None):
        path = os.path.join(ASSETS_DIR, name)
        try:
            img = pygame.image.load(path).convert_alpha()
            if size:
                img = pygame.transform.scale(img, size)
            return img
        except FileNotFoundError:
            print(f"[UI Warning] Missing image: {name}")
            return None

    # --- IMAGE SIZES ---
    hole_w = int(MOLE_RADIUS * 1.8) 
    hole_h = int(MOLE_RADIUS * 1.8) 
    mole_w = int(MOLE_RADIUS * 1.1) 
    mole_h = int(MOLE_RADIUS * 1.3)
    hammer_w = int(MOLE_RADIUS * 1.5)
    hammer_h = int(MOLE_RADIUS * 1.5)

    assets['hammer_orig'] = load_img('hammer.png', (hammer_w, hammer_h))
    assets['bg'] = load_img('bg.png', (SCREEN_WIDTH, SCREEN_HEIGHT))
    assets['hole'] = load_img('hole.png', (hole_w, hole_h))
    assets['mole'] = load_img('mole.png', (mole_w, mole_h))
    assets['mole_whacked'] = load_img('mole_whacked.png', (mole_w, mole_h))
    
    assets['initialized'] = True

def draw_text_with_shadow(screen, text, font, color, pos, shadow_color=(0,0,0)):
    """ Draws text with a black shadow for better visibility. """
    shadow = font.render(text, True, shadow_color)
    main = font.render(text, True, color)
    screen.blit(shadow, (pos[0] + 2, pos[1] + 2))
    screen.blit(main, pos)

def draw_centered_text(screen, text, font, color, y, shadow_color=(0,0,0)):
    """ Draws text horizontally centered at a specific Y coordinate. """
    surf = font.render(text, True, color)
    x = SCREEN_WIDTH // 2 - surf.get_width() // 2
    draw_text_with_shadow(screen, text, font, color, (x, y), shadow_color)

# ==========================================
#  MAIN DRAW LOGIC
# ==========================================

def draw(screen, game):
    """ Main render function calling specific state draw methods. """
    init_resources()
    
    # Draw Background
    if assets['bg']:
        screen.blit(assets['bg'], (0, 0))
    else:
        screen.fill(COLOR_BG)

    # State Dispatcher
    if game.state == STATE_MENU:
        _draw_menu(screen, game)
    elif game.state == STATE_PLAYING:
        _draw_game(screen, game)
    elif game.state == STATE_GAMEOVER:
        _draw_gameover(screen, game)
    elif game.state == STATE_PAUSED:
        _draw_game(screen, game)
        _draw_pause_overlay(screen, game)
    
    # --- MULTIPLAYER SPECIFIC STATES ---
    elif game.state == STATE_WAITING_P2:
        _draw_waiting_p2(screen, game)
    elif game.state == STATE_WINNER:
        _draw_winner(screen, game)

def _draw_menu(screen, game):
    """ Draws the Main Menu with difficulty selection. """
    draw_centered_text(screen, "WHAC-A-MOLE", fonts['large'], (255, 220, 0), 100)

    start_y = 320 
    for i, name in enumerate(MODE_NAMES):
        color = (255, 215, 0) if i == game.difficulty else (200, 200, 200)
        draw_centered_text(screen, name, fonts['normal'], color, start_y + i * 60)

    draw_text_with_shadow(screen, "Use Potentiometer to Select", fonts['ui'], (255,255,255), (20, SCREEN_HEIGHT - 60))
    draw_text_with_shadow(screen, "Press Yellow Button Confirm", fonts['ui'], (255,255,255), (20, SCREEN_HEIGHT - 35))

def _draw_game(screen, game):
    """ Draws the main 3x3 game grid, moles, and UI. """
    cols = 3
    rows = 3
    start_x = SCREEN_WIDTH // 6
    start_y = SCREEN_HEIGHT // 4 + 140 
    gap_x = SCREEN_WIDTH // 3
    gap_y = SCREEN_HEIGHT // 5 - 10 
    
    positions = []
    for r in range(rows):
        for c in range(cols):
            x = start_x + (c * gap_x)
            y = start_y + (r * gap_y)
            positions.append((x, y))
            
    current_time = pygame.time.get_ticks() 
    is_multi = getattr(game, 'is_multiplayer', False)

    # --- MULTIPLAYER UI (Timer & Player Name) ---
    if is_multi:
        time_elapsed = current_time - getattr(game, 'start_time', current_time)
        time_left = max(0, GAME_DURATION - time_elapsed)
        seconds = math.ceil(time_left / 1000)
        
        timer_color = (255, 255, 255)
        if seconds <= 5: timer_color = (255, 50, 50)
        draw_centered_text(screen, f"Time: {seconds}", fonts['normal'], timer_color, 80)
        
        p_num = getattr(game, 'current_player', 1) 
        p_text = f"PLAYER {p_num}"
        p_color = (100, 255, 255) if p_num == 1 else (255, 100, 255)
        draw_text_with_shadow(screen, p_text, fonts['normal'], p_color, (30, 80))

    # --- DRAW HOLES AND MOLES ---
    for i, pos in enumerate(positions):
        # 1. Hole
        if assets['hole']:
            hole_w = assets['hole'].get_width()
            hole_h = assets['hole'].get_height()
            hole_x = pos[0] - hole_w // 2
            hole_y = pos[1] - hole_h // 2
            screen.blit(assets['hole'], (hole_x, hole_y))
        else:
            pygame.draw.circle(screen, COLOR_HOLE, pos, MOLE_RADIUS)
        
        # 2. Mole
        if assets['mole']:
            w = assets['mole'].get_width()
            h = assets['mole'].get_height()
            mole_x = pos[0] - w // 2
            mole_bottom_y = pos[1] + 10 
            
            if i == game.current_mole_index:
                # Alive Mole Logic (Hiding/Appearing)
                if game.is_hiding:
                    retreat_start_time = game.last_spawn_time + (game.spawn_interval - game.hide_duration)
                    time_into_retreat = current_time - retreat_start_time
                    progress = time_into_retreat / game.hide_duration
                    if progress > 1.0: progress = 1.0
                    if progress < 0.0: progress = 0.0
                    visible_h = int(h * (1.0 - progress))
                    if visible_h > 0:
                        crop_rect = pygame.Rect(0, 0, w, visible_h)
                        mole_cropped = assets['mole'].subsurface(crop_rect)
                        draw_y = mole_bottom_y - visible_h
                        screen.blit(mole_cropped, (mole_x, draw_y))
                else:
                    anim_duration = 150 
                    time_elapsed = current_time - game.last_spawn_time
                    progress = time_elapsed / anim_duration
                    if progress >= 1.0:
                        draw_y = mole_bottom_y - h
                        screen.blit(assets['mole'], (mole_x, draw_y))
                    else:
                        visible_h = int(h * progress)
                        if visible_h > 0:
                            crop_rect = pygame.Rect(0, 0, w, visible_h)
                            mole_cropped = assets['mole'].subsurface(crop_rect)
                            draw_y = mole_bottom_y - visible_h
                            screen.blit(mole_cropped, (mole_x, draw_y))
            
            elif i == game.whacked_mole_index:
                # Whacked Mole (Squashing Animation)
                if assets['mole_whacked']:
                    time_since_hit = current_time - game.hit_time
                    progress = time_since_hit / game.hit_delay_duration
                    if progress > 1.0: progress = 1.0
                    if progress < 0.0: progress = 0.0
                    current_visible_ratio = game.whacked_height_ratio * (1.0 - progress)
                    visible_h = int(h * current_visible_ratio)
                    if visible_h > 0:
                        crop_rect = pygame.Rect(0, 0, w, visible_h)
                        whacked_cropped = assets['mole_whacked'].subsurface(crop_rect)
                        draw_y = mole_bottom_y - visible_h
                        screen.blit(whacked_cropped, (mole_x, draw_y))

        # 3. Hammer Animation (With Rotation)
        if assets.get('hammer_orig') and getattr(game, 'is_hammering', False) and i == getattr(game, 'hammer_target_index', -1):
            duration = getattr(game, 'hammer_duration', 150) 
            time_elapsed = current_time - game.hammer_start_time
            progress = time_elapsed / duration
            
            if progress >= 1.0:
                game.is_hammering = False
                game.hammer_target_index = -1
            else:
                # Rotation: Start at 0 deg, End at 60 deg (Simple swing)
                start_angle = 0   
                end_angle = 60    
                current_angle = start_angle + (end_angle - start_angle) * progress
                
                rotated_hammer = pygame.transform.rotate(assets['hammer_orig'], current_angle)
                
                # Re-center logic
                new_rect = rotated_hammer.get_rect(center=pos)
                new_rect.centery -= int(MOLE_RADIUS * 0.8)
                new_rect.centerx += int(MOLE_RADIUS * 0.4) 
                
                screen.blit(rotated_hammer, new_rect)

    # Dashboard (Score & Lives)
    draw_text_with_shadow(screen, f"Score: {game.score}", fonts['normal'], (255, 255, 255), (30, 30), shadow_color=(50,50,50))
    lives_color = (255, 50, 50) if game.lives < 3 else (255, 100, 100)
    lives_surf = fonts['normal'].render(f"Lives: {game.lives}", True, lives_color)
    draw_text_with_shadow(screen, f"Lives: {game.lives}", fonts['normal'], lives_color, (SCREEN_WIDTH - 30 - lives_surf.get_width(), 30), shadow_color=(50,50,50))
    
    # Show Mode Name
    mode_str = f"Mode: {MODE_NAMES[game.difficulty]}"
    mode_surf = fonts['ui'].render(mode_str, True, (100, 255, 100))
    draw_text_with_shadow(screen, mode_str, fonts['ui'], (100, 255, 100), (SCREEN_WIDTH//2 - mode_surf.get_width()//2, 35), shadow_color=(50,50,50))

def _draw_gameover(screen, game):
    """ Draws Game Over screen with Restart/Quit options. """
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    draw_centered_text(screen, "GAME OVER", fonts['large'], (255, 50, 50), 150)
    draw_centered_text(screen, f"Final Score: {game.score}", fonts['normal'], (255, 255, 255), 250)
    
    opts = ["RESTART", "QUIT"]
    for i, opt in enumerate(opts):
        color = (255, 255, 0) if i == game.game_over_selection else (150, 150, 150)
        draw_centered_text(screen, opt, fonts['normal'], color, 400 + i*60)

def _draw_pause_overlay(screen, game):
    """ Draws semi-transparent pause menu. """
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(150) 
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    draw_centered_text(screen, "PAUSED", fonts['large'], (255, 255, 0), 150)
    opts = ["RESUME", "MAIN MENU"]
    for i, opt in enumerate(opts):
        color = (255, 255, 0) if i == game.pause_selection else (150, 150, 150)
        draw_centered_text(screen, opt, fonts['normal'], color, 300 + i*60)

# --- MULTIPLAYER INTERMISSION ---
def _draw_waiting_p2(screen, game):
    """ Draws the screen between Player 1 and Player 2 turns. """
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(240)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    draw_centered_text(screen, "PLAYER 1 FINISHED!", fonts['normal'], (100, 255, 255), 150)
    p1_score = getattr(game, 'p1_score', game.score)
    draw_centered_text(screen, f"Score: {p1_score}", fonts['large'], (255, 255, 255), 220)
    draw_centered_text(screen, "Player 2, Get Ready!", fonts['normal'], (255, 100, 255), 350)
    draw_centered_text(screen, "Press Button to Start", fonts['ui'], (200, 200, 200), 450)

# --- MULTIPLAYER WINNER ---
def _draw_winner(screen, game):
    """ Draws the final results for Multiplayer mode. """
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(240)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    s1 = getattr(game, 'p1_score', 0)
    s2 = getattr(game, 'p2_score', 0)

    if s1 > s2:
        title = "PLAYER 1 WINS!"
        color = (100, 255, 255)
    elif s2 > s1:
        title = "PLAYER 2 WINS!"
        color = (255, 100, 255)
    else:
        title = "IT'S A DRAW!"
        color = (255, 255, 255)

    draw_centered_text(screen, title, fonts['large'], color, 100)
    draw_centered_text(screen, f"P1 Score: {s1}", fonts['normal'], (100, 255, 255), 220)
    draw_centered_text(screen, f"P2 Score: {s2}", fonts['normal'], (255, 100, 255), 280)

    opts = ["PLAY AGAIN", "QUIT"]
    for i, opt in enumerate(opts):
        c = (255, 255, 0) if i == game.game_over_selection else (150, 150, 150)
        draw_centered_text(screen, opt, fonts['normal'], c, 400 + i*60)