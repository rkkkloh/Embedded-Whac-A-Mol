import pygame
import serial
import threading
import os
import time
import math
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_SELECT, COLOR_TEXT

# --- RESOURCE PATHS ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(CURRENT_DIR, 'asset')

# --- GLOBAL RESOURCES ---
assets = {}
fonts = {}

def init_resources():
    """
    Lazily initializes fonts and loads images to improve startup performance.
    """
    if 'initialized' in assets: return

    pygame.font.init()
    try:
        # Use modern fonts if available, fallback to system default if not
        fonts['title'] = pygame.font.SysFont("Chalkboard SE", 60, bold=True)
        fonts['input'] = pygame.font.SysFont("Arial Rounded MT Bold", 48)
        fonts['status'] = pygame.font.SysFont("Arial", 28)
        fonts['hint'] = pygame.font.SysFont("Arial Rounded MT Bold", 20)
    except:
        # Fallback fonts
        fonts['title'] = pygame.font.SysFont("Arial", 60, bold=True)
        fonts['input'] = pygame.font.SysFont("Arial", 48)
        fonts['status'] = pygame.font.SysFont("Arial", 28)
        fonts['hint'] = pygame.font.SysFont("Arial", 20)

    def load_img(name, size=None):
        path = os.path.join(ASSETS_DIR, name)
        try:
            img = pygame.image.load(path).convert_alpha()
            if size: img = pygame.transform.scale(img, size)
            return img
        except: return None

    assets['bg'] = load_img('bg.png', (SCREEN_WIDTH, SCREEN_HEIGHT))
    assets['initialized'] = True

# --- GLOBAL VARIABLES FOR THREADING ---
connection_result = None
is_checking = False

def threaded_check_connection(port_name):
    """
    Background thread to check if the COM port is valid.
    This prevents the UI from freezing while waiting for a serial connection.
    """
    global connection_result, is_checking
    try:
        # Try to open the port with a timeout
        s = serial.Serial(port_name, 9600, timeout=2)
        s.close() # Close immediately if successful
        connection_result = (True, "Connection Successful")
    except serial.SerialException:
        connection_result = (False, f"Failed to open {port_name}")
    except Exception as e:
        connection_result = (False, f"Error: {str(e)}")
    
    is_checking = False 

def draw_text_centered(screen, text, font, color, center_y, shadow=True):
    """ Helper function to draw centered text with a drop shadow effect. """
    if shadow:
        shadow_surf = font.render(text, True, (0, 0, 0))
        shadow_rect = shadow_surf.get_rect(center=(SCREEN_WIDTH//2 + 2, center_y + 2))
        screen.blit(shadow_surf, shadow_rect)
    
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(SCREEN_WIDTH//2, center_y))
    screen.blit(surf, rect)

def get_port_from_user(screen):
    """
    Main loop for the Port Selection Screen.
    Allows user to type the COM port and validates it.
    """
    global connection_result, is_checking
    
    init_resources()
    
    input_text = "COM" # Default prefix
    status_text = "Enter Device Port"
    status_color = (200, 200, 200)
    
    clock = pygame.time.Clock()
    cursor_visible = True
    cursor_timer = 0
    pulse_timer = 0 # For breathing text effect

    while True:
        # --- 1. Draw Background ---
        if assets['bg']:
            screen.blit(assets['bg'], (0, 0))
        else:
            screen.fill(COLOR_BG)
            
        # Add a dark overlay to make text pop
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180) 
        overlay.fill((20, 20, 20))
        screen.blit(overlay, (0, 0))

        # --- 2. Draw Title ---
        draw_text_centered(screen, "CONTROLLER SETUP", fonts['title'], COLOR_SELECT, 150)

        # --- 3. Draw Input Box ---
        box_width, box_height = 360, 80
        box_center_x = SCREEN_WIDTH // 2
        box_center_y = 280
        box_rect = pygame.Rect(box_center_x - box_width//2, box_center_y - box_height//2, box_width, box_height)
        
        # Change border color if currently checking connection
        if is_checking: 
            border_color = (255, 255, 0) # Yellow for checking
            bg_color = (60, 60, 40)
        else: 
            border_color = (255, 255, 255) # White for idle
            bg_color = (50, 50, 50)
            
        pygame.draw.rect(screen, bg_color, box_rect, border_radius=15)
        pygame.draw.rect(screen, border_color, box_rect, 4, border_radius=15)

        # --- 4. Draw Input Text ---
        txt_surf = fonts['input'].render(input_text, True, (255, 255, 255))
        txt_rect = txt_surf.get_rect(center=box_rect.center)
        screen.blit(txt_surf, txt_rect)
        
        # --- 5. Draw Blinking Cursor ---
        if not is_checking and cursor_visible:
            cursor_h = 40
            cursor_rect = pygame.Rect(txt_rect.right + 4, box_center_y - cursor_h//2, 3, cursor_h)
            pygame.draw.rect(screen, (255, 255, 255), cursor_rect)

        # --- 6. Draw Status Message ---
        if "Success" in status_text: status_color = (100, 255, 100)
        elif "Failed" in status_text or "Error" in status_text: status_color = (255, 80, 80)
        
        draw_text_centered(screen, status_text, fonts['status'], status_color, 380)

        # --- 7. Draw Bottom Hint (Breathing Animation) ---
        pulse_val = (math.sin(pulse_timer * 0.005) + 1) * 0.5 # 0.0 ~ 1.0
        alpha = int(100 + pulse_val * 155) # Calculate alpha for fading
        
        hint_surf = fonts['hint'].render("Press ENTER to Connect   |   ESC to Quit", True, (180, 180, 180))
        hint_surf.set_alpha(alpha) 
        hint_rect = hint_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 60))
        screen.blit(hint_surf, hint_rect)

        pygame.display.flip()

        # --- EVENT HANDLING ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if is_checking:
                        is_checking = False
                        status_text = "Cancelled"
                        status_color = (255, 100, 100)
                    else:
                        return None
                
                elif event.key == pygame.K_RETURN:
                    # Start connection check
                    if not is_checking and len(input_text) > 0:
                        is_checking = True
                        connection_result = None
                        status_text = "Connecting..."
                        status_color = (255, 255, 0)
                        
                        # Start thread
                        t = threading.Thread(target=threaded_check_connection, args=(input_text,))
                        t.daemon = True
                        t.start()
                
                elif not is_checking:
                    # Handle typing
                    if event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        if len(input_text) < 10: 
                            input_text += event.unicode.upper()

        # --- CHECK RESULT FROM THREAD ---
        if connection_result is not None:
            success, msg = connection_result
            if success:
                status_text = msg
                # Force draw one last frame to show success
                pygame.draw.rect(screen, (20, 20, 20), (0, 360, SCREEN_WIDTH, 50)) 
                draw_text_centered(screen, status_text, fonts['status'], (100, 255, 100), 380)
                pygame.display.flip()
                
                print("[DEBUG] Waiting 1.5s for port release...")
                time.sleep(1.5) # Wait for OS to release the port handle
                return input_text
            else:
                status_text = msg
                status_color = (255, 80, 80)
                connection_result = None

        # Update Timers
        dt = clock.tick(30)
        cursor_timer += dt
        pulse_timer += dt
        
        if cursor_timer > 500:
            cursor_visible = not cursor_visible
            cursor_timer = 0