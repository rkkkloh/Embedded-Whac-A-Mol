import pygame
import sys
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from comms import SerialManager
from game_state import GameState
import renderer

from input_screen import get_port_from_user 

def main():
    """
    Main Entry Point of the Application.
    Steps:
    1. Init Pygame
    2. Show Input Screen to get COM port
    3. Initialize Serial Connection
    4. Enter Game Loop
    """
    pygame.init()
    pygame.mixer.init()
    
    # Initialize Display Surface
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("PIC18F Whac-A-Mole Controller")
    clock = pygame.time.Clock()
    

    # ==========================================
    # 1. GET PORT FROM UI
    # ==========================================
    # Blocking call that waits for user to enter a valid port
    selected_port = get_port_from_user(screen)
    
    # If user closed the window instead of entering a port
    if selected_port is None:
        pygame.quit()
        sys.exit()
        
    print(f"User selected: {selected_port}")

    # ==========================================
    # 2. START GAME
    # ==========================================
    # Pass the validated port to SerialManager
    comms = SerialManager(port=selected_port) 
    
    # Initialize Game State with the serial connection
    game = GameState(comms)

    running = True
    while running:
        # --- 1. Read Serial Inputs ---
        # Fetch commands from PIC (buttons, potentiometer)
        commands = comms.read_commands()
        for cmd in commands:
            game.process_input(cmd)

        # --- 2. Window Events ---
        for event in pygame.event.get():
            # Handle Window Close (X Button)
            if event.type == pygame.QUIT:
                game.cleanup() # Send signal to reset hardware before quitting
                running = False

        # --- 3. Update & Draw ---
        game.update()       # Update game logic (timers, states)
        renderer.draw(screen, game) # Render current state to screen

        pygame.display.flip() # Update display
        clock.tick(60)        # Limit to 60 FPS

    # Clean exit
    comms.close()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()