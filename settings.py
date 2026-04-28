
# --- Game Constants ---
WINDOW_WIDTH = 854
WINDOW_HEIGHT = 480
TILE_SIZE = 40          # Size of one tile in pixels
GRAVITY = 1800.0        # Downward acceleration (pixels/s/s)
JUMP_VELOCITY = -1000.0  # Initial upward velocity on jump
STOMP_BOUNCE = JUMP_VELOCITY * 0.6 # Reduced jump velocity for bounce
PLAYER_SPEED = 300.0    # Player horizontal movement speed
ENEMY_SPEED = -100.0     # Enemy horizontal movement speed
PLAYER_WIDTH = TILE_SIZE * 2.0
PLAYER_HEIGHT = TILE_SIZE * 2.0

# --- Tilemap Definitions ---
TILE_AIR = 0
TILE_BOTTOM_GRASS = 1 
TILE_TOP_GRASS = 2
TILE_COIN = 3
TILE_GOAL = 4
TILE_YATAGARASU = 5
TILE_GHOST = 6

# --- Attack Constants ---
MELEE_RANGE        = 48        # px reach in front of player
MELEE_HEIGHT       = 40        # vertical height of the hitbox
MELEE_DURATION     = 0.18      # seconds the hitbox is active
MELEE_COOLDOWN     = 0.45      # seconds between attacks

PROJECTILE_SPEED   = 520       # px/s (horizontal only)
PROJECTILE_RADIUS  = 6         # visual + collision radius
PROJECTILE_LIFE    = 1.8       # seconds before despawn
PROJECTILE_COOLDOWN = 0.35     # seconds between shots
SHOT_COOLDOWN = 2.5

ATT_THRESHOLD = 48
BASE_HEALTH = 100
ENEMY_XRANGE = 200
ENEMY_YRANGE = 40
