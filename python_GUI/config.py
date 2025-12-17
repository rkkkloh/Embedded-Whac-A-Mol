# config.py
# ---------------------------------------------------------
# Configuration file for the Whac-A-Mole Game.
# Contains all constants for Hardware, GUI, and Game Logic.
# ---------------------------------------------------------

# --- Serial Communication Settings ---
# Default Bluetooth COM port (Can be changed in the Input Screen)
SERIAL_PORT = 'COM7'  
# Baud rate must match the PIC18F4520 UART setting
BAUD_RATE = 9600

# --- Animation Settings ---
# Duration of the hammer swing animation in milliseconds
HAMMER_SWING_DURATION = 150

# --- Window & Graphics Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
MOLE_RADIUS = 80

# --- Color Definitions (R, G, B) ---
COLOR_BG = (30, 30, 30)       # Dark Gray Background
COLOR_HOLE = (0, 0, 0)        # Black Holes
COLOR_SELECT = (255, 215, 0)  # Gold for highlights
COLOR_TEXT = (220, 220, 220)  # Off-white for text

# --- Game Modes ---
MODE_EASY = 0
MODE_MEDIUM = 1
MODE_HARD = 2
MODE_MULTIPLAYER = 3  # Multiplayer mode (Time Attack)
MENU_QUIT = 4         # Option to close the application

# Display names for the menu selection
MODE_NAMES = ["Easy", "Medium", "Hard", "Multiplayer", "Quit"]

# --- Game States ---
# These constants control the main state machine of the game
STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAMEOVER = 2
STATE_PAUSED = 3
STATE_WAITING_P2 = 5   # Intermission screen for Multiplayer
STATE_WINNER = 6       # Final result screen for Multiplayer

# --- Multiplayer Settings ---
# Duration for each player's turn in Multiplayer (in ms)
GAME_DURATION = 30000  # 30 Seconds