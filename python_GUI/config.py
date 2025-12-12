# config.py

# --- Serial Settings ---
SERIAL_PORT = 'COM17'  # Change this to your actual port
BAUD_RATE = 9600

# --- Window Settings ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
MOLE_RADIUS = 60

# --- Colors ---
COLOR_BG = (30, 30, 30)
COLOR_MOLE = (255, 100, 100) # Red
COLOR_HOLE = (80, 80, 80)    # Gray
COLOR_TEXT = (255, 255, 255)
COLOR_SELECT = (255, 215, 0) # Gold
# config.py (Add this line)
STATE_PAUSED = 3

# --- Game Constants ---
STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAMEOVER = 2

MODE_EASY = 0
MODE_MEDIUM = 1
MODE_HARD = 2
MODE_NAMES = ["Easy (Simple)", "Medium (Capped)", "Hard (Uncapped)"]