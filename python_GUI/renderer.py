# renderer.py
import pygame
from config import *

pygame.font.init()
font = pygame.font.SysFont("Arial", 32)
large_font = pygame.font.SysFont("Arial", 64)

def draw(screen, game):
    if game.state == STATE_MENU:
        _draw_menu(screen, game)
    elif game.state == STATE_PLAYING:
        _draw_game(screen, game)
    elif game.state == STATE_GAMEOVER:
        _draw_gameover(screen, game)
    elif game.state == STATE_PAUSED:
        _draw_game(screen, game) 
        _draw_pause_overlay(screen, game)

def _draw_menu(screen, game):
    screen.fill(COLOR_BG)
    title = large_font.render("WHAC-A-MOLE", True, COLOR_TEXT)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
    
    for i, name in enumerate(MODE_NAMES):
        color = COLOR_SELECT if i == game.difficulty else (100, 100, 100)
        text = font.render(name, True, color)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 300 + i*60))

    info1 = font.render("Use Potentiometer to Select Mode", True, (200, 200, 200))
    info2 = font.render("Press RB0 (Confirm) to Start", True, (200, 200, 200))
    
    screen.blit(info1, (SCREEN_WIDTH//2 - info1.get_width()//2, 550))
    screen.blit(info2, (SCREEN_WIDTH//2 - info2.get_width()//2, 600))

def _draw_game(screen, game):
    screen.fill(COLOR_BG)
    
    # --- 3x3 GRID LAYOUT ---
    cols = 3
    rows = 3
    
    # Calculate spacing
    start_x = SCREEN_WIDTH // 6
    start_y = SCREEN_HEIGHT // 4 + 40
    gap_x = SCREEN_WIDTH // 3
    gap_y = SCREEN_HEIGHT // 5
    
    positions = []
    # 0 1 2
    # 3 4 5
    # 6 7 8
    for r in range(rows):
        for c in range(cols):
            x = start_x + (c * gap_x)
            y = start_y + (r * gap_y)
            positions.append((x, y))
            
    for i, pos in enumerate(positions):
        # Draw Hole
        pygame.draw.circle(screen, COLOR_HOLE, pos, MOLE_RADIUS)
        
        # Draw Number Label
        label = font.render(str(i), True, (100, 100, 100))
        screen.blit(label, (pos[0]-10, pos[1]+MOLE_RADIUS+5))
        
        # Draw Mole
        if i == game.current_mole_index:
            pygame.draw.circle(screen, COLOR_MOLE, pos, MOLE_RADIUS - 10)

    # UI Text
    score_text = font.render(f"Score: {game.score}", True, COLOR_TEXT)
    lives_text = font.render(f"Lives: {game.lives}", True, (255, 50, 50))
    mode_text = font.render(f"Mode: {MODE_NAMES[game.difficulty]}", True, (100, 255, 100))
    
    screen.blit(score_text, (20, 20))
    screen.blit(lives_text, (SCREEN_WIDTH - 150, 20))
    screen.blit(mode_text, (SCREEN_WIDTH//2 - mode_text.get_width()//2, 20))

def _draw_gameover(screen, game):
    screen.fill(COLOR_BG)
    msg = large_font.render("GAME OVER", True, (255, 50, 50))
    score = font.render(f"Final Score: {game.score}", True, COLOR_TEXT)
    screen.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, 150))
    screen.blit(score, (SCREEN_WIDTH//2 - score.get_width()//2, 250))
    
    opts = ["RESTART", "QUIT"]
    for i, opt in enumerate(opts):
        color = COLOR_SELECT if i == game.game_over_selection else (100, 100, 100)
        text = font.render(opt, True, color)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 400 + i*60))

def _draw_pause_overlay(screen, game):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180) 
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    text = large_font.render("PAUSED", True, COLOR_SELECT)
    screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 150))
    
    opts = ["RESUME", "MAIN MENU"]
    for i, opt in enumerate(opts):
        color = COLOR_SELECT if i == game.pause_selection else (100, 100, 100)
        text = font.render(opt, True, color)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 300 + i*60))
        
    subtext = font.render("Select with Potentiometer, Confirm with RB0", True, (150, 150, 150))
    screen.blit(subtext, (SCREEN_WIDTH//2 - subtext.get_width()//2, 500))