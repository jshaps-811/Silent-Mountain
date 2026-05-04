
# --- Game Constants ---
WINDOW_WIDTH = 854
WINDOW_HEIGHT = 480
TILE_SIZE = 40          # Size of one tile in pixels
GRAVITY = 1800.0        # Downward acceleration (pixels/s/s)
JUMP_VELOCITY = -700.0  # Initial upward velocity on jump
STOMP_BOUNCE = JUMP_VELOCITY * 0.6 # Reduced jump velocity for bounce
PLAYER_SPEED = 300.0    # Player horizontal movement speed
ENEMY_SPEED = -100.0     # Enemy horizontal movement speed
PLAYER_WIDTH = TILE_SIZE * 1.5
PLAYER_HEIGHT = TILE_SIZE * 1.5

# --- Tilemap Definitions ---
TILE_AIR = 0
TILE_BOTTOM_GRASS = 1 
TILE_TOP_GRASS = 2
TILE_LEDGE_GRASS = 3
TILE_GOAL = 4
TILE_YATAGARASU = 5
TILE_GHOST = 6
ROCKS_MIDDLE = 7
LEDGE_LEFT = 8
LEDGE_RIGHT = 9
GRASS_LEFT = 10
GRASS_RIGHT = 11
ROCKY_LEDGE_LEFT = 12
ROCKY_LEDGE_MID = 13
ROCKY_LEDGE_RIGHT = 14
INVISIBLE = 15
TILE_ONI = 20

COLLISION_TILES = {
    TILE_BOTTOM_GRASS: 1,
    TILE_TOP_GRASS:    0,
    TILE_LEDGE_GRASS:  2,
    LEDGE_LEFT:        3,
    LEDGE_RIGHT:       4,
    GRASS_LEFT:        5,
    GRASS_RIGHT:       6,
    ROCKS_MIDDLE:      7,
    ROCKY_LEDGE_LEFT:  12,
    ROCKY_LEDGE_MID:   13,
    ROCKY_LEDGE_RIGHT: 14,
    INVISIBLE:        15
}

# --- Attack Constants ---
MELEE_RANGE        = 40        # px reach in front of player
MELEE_WIDTH        = 60        # px width of the hitbox
MELEE_HEIGHT       = 80        # vertical height of the hitbox
MELEE_DURATION     = 0.3      # seconds the hitbox is active
MELEE_COOLDOWN     = 0.5      # seconds between attacks

PROJECTILE_SPEED   = 520       # px/s (horizontal only)
PROJECTILE_RADIUS  = 6         # visual + collision radius
PROJECTILE_LIFE    = 1.8       # seconds before despawn
PROJECTILE_COOLDOWN = 0.35     # seconds between shots
SHOT_COOLDOWN = 2.5

ATT_THRESHOLD = 48
BASE_HEALTH = 7
ENEMY_XRANGE = 200
ENEMY_YRANGE = 40
INVINCIBILITY_DURATION = 0.5

GHOST_DAMAGE = 1
YATAGARASU_DAMAGE = 2

# --- Breath system ---
BREATH_MAX         = 100.0   # maximum breath pool
BREATH_REGEN       = 12.0    # units recovered per second
BREATH_COST_MELEE  = 25.0    # short-range attack cost
BREATH_COST_RANGED = 40.0    # long-range attack cost (more expensive)
WHIRLWIND_OFFSET = 150

# --- Oni Constants ---
ONI_MELEE_RANGE   = TILE_SIZE * 1.25   # px distance to trigger an attack swing
ONI_ATTACK_COOLDOWN = 0.9             # seconds between swings
ONI_CHASE_SPEED   = ENEMY_SPEED * 1.2 # speed when player is nearby (chasing)
ONI_PATROL_SPEED  = ENEMY_SPEED * 0.5 # speed while no player is nearby
ONI_AGGRO_RANGE   = TILE_SIZE * 8     # horizontal distance at which Oni "notices" the player
ONI_ATTACK_DAMAGE = 2                 # hearts / HP removed per hit (consumed by player)
ONI_PASSIVE_DAMAGE = 1
ONI_IFRAMES = 0.5
ONI_HEALTH = 100

X_KNOCKBACK = 700
Y_KNOCKBACK = 100