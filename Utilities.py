from pyray import *
from settings import *
from enemy import *
from player import *


def load_level(filepath):
        levelmap = []
        with open(filepath, 'r') as f:
            for line in f:
                row = [int(cell) for cell in line.strip().split(',')]
                levelmap.append(row)
        return levelmap

def parse_level(level):
    """
    Parses the level map, extracts all dynamic entities (coins, enemies), 
    replaces their spawn points with air, and returns the modified collision map and entity lists.
    """
    coins = []
    enemies = []
    # Create a deep copy of the level to modify the tiles, leaving the original map intact
    new_level = [row[:] for row in level] 
    
    for r in range(TILE_ROWS):
        for c in range(TILE_COLS):
            x = c * TILE_SIZE
            y = r * TILE_SIZE

            if new_level[r][c] == TILE_COIN:
                # Coin position is center
                coins.append((x + TILE_SIZE / 2, y + TILE_SIZE / 2))
                new_level[r][c] = TILE_AIR 
            
            # elif new_level[r][c] == TILE_LAVA:
            #     new_level[r][c] = TILE_AIR

            elif new_level[r][c] == TILE_ENEMY:
                # Enemy position is top-left
                enemies.append(Enemy(x, y))
                new_level[r][c] = TILE_AIR 
            
    return new_level, coins, enemies

def update_cam(camera, player, world_width, world_height, screen_width, screen_height):
    """Centers the camera on the player and clamps the camera's target to the world bounds."""
    
    camera.target.x = player.x + player.width / 2
    camera.target.y = player.y + player.height / 2

    min_x = screen_width / 2
    max_x = world_width
    
    if camera.target.x < min_x:
        camera.target.x = min_x
    if camera.target.x > max_x:
        camera.target.x = max_x

    min_y = screen_height / 2
    max_y = world_height - screen_height / 2
    
    if camera.target.y < min_y:
        camera.target.y = min_y
    if camera.target.y > max_y:
        camera.target.y = max_y
    
    camera.offset.x = screen_width / 2
    camera.offset.y = screen_height / 2

            
def draw_level(level):
    """Draws the solid tiles of the level map."""
    for row in range(TILE_ROWS):
        for col in range(TILE_COLS):
            tile_value = level[row][col]
            if level[row][col] == TILE_LAVA:
                draw_rectangle(x, y, TILE_SIZE, TILE_SIZE, RED)
            if tile_value == TILE_SOLID:
                x = col * TILE_SIZE
                y = row * TILE_SIZE

                draw_rectangle(x, y, TILE_SIZE, TILE_SIZE, DARKGRAY)
                draw_rectangle_lines(x, y, TILE_SIZE, TILE_SIZE, BLACK)
                
def draw_coins(coins):
        """Draws the active coins as small yellow diamonds (polygons)."""
        radius = TILE_SIZE * 0.3 / 2 
        
        for cx, cy in coins:
            v1 = Vector2(cx, cy - radius * 2)
            v2 = Vector2(cx + radius * 1.5, cy)
            v3 = Vector2(cx, cy + radius * 2)
            v4 = Vector2(cx - radius * 1.5, cy)
            
            draw_triangle(v1, v2, v4, YELLOW)
            draw_triangle(v2, v3, v4, GOLD)
            
            draw_line_v(v1, v3, BLACK)
            draw_line_v(v2, v4, BLACK)