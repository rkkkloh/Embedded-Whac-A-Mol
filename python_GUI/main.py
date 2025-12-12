# main.py
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from comms import SerialManager
from game_state import GameState
import renderer

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("PIC18F Whac-A-Mole Controller (3x3)")
    clock = pygame.time.Clock()

    comms = SerialManager()
    game = GameState(comms)

    running = True
    while running:
        # 1. Read Serial Inputs (PIC)
        commands = comms.read_commands()
        for cmd in commands:
            game.process_input(cmd)

        # 2. Window Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 3. Update & Draw
        game.update()
        renderer.draw(screen, game)

        pygame.display.flip()
        clock.tick(60)

    comms.close()
    pygame.quit()

if __name__ == "__main__":
    main()