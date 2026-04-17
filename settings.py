import Utilities
import os

 # --- Level map ---
base_dir = os.path.dirname(__file__)
LEVEL = Utilities.load_level(os.path.join(base_dir, "assets", "forest_level_map.csv"))
TILE_ROWS = len(LEVEL)
TILE_COLS = len(LEVEL[0])


# --- Game Constants ---
WINDOW_WIDTH = 854
WINDOW_HEIGHT = 480
TILE_SIZE = 40          # Size of one tile in pixels
GRAVITY = 1800.0        # Downward acceleration (pixels/s/s)
JUMP_VELOCITY = -750.0  # Initial upward velocity on jump
STOMP_BOUNCE = JUMP_VELOCITY * 0.6 # Reduced jump velocity for bounce
PLAYER_SPEED = 300.0    # Player horizontal movement speed
ENEMY_SPEED = 100.0     # Enemy horizontal movement speed
PLAYER_WIDTH = TILE_SIZE * 0.8
PLAYER_HEIGHT = TILE_SIZE * 0.9

# --- Tilemap Definitions ---
TILE_AIR = 0
TILE_SOLID = 1 
TILE_LAVA = 2
TILE_COIN = 3
TILE_ENEMY = 4 

# --- World Dimensions ---
WORLD_WIDTH = TILE_COLS * TILE_SIZE
WORLD_HEIGHT = TILE_ROWS * TILE_SIZE
Y_OFFSET = 200

