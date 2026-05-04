from pyray import *
from settings import *
from enemy import *
from player import *
from ghost import *
from yatagarasu import *
from oni import *


def load_level(filepath):
        levelmap = []
        with open(filepath, 'r') as f:
            for line in f:
                row = [int(cell) if cell.strip() else 0 for cell in line.strip().split(',')]
                levelmap.append(row)
        return levelmap

def parse_level(level, tile_rows, tile_cols):
    """
    Parses the level map, extracts all dynamic entities (coins, enemies), 
    replaces their spawn points with air, and returns the modified collision map and entity lists.
    """
    coins = []
    enemies = []
    # Create a deep copy of the level to modify the tiles, leaving the original map intact
    new_level = [row[:] for row in level] 
    
    for r in range(tile_rows):
        for c in range(tile_cols):
            x = c * TILE_SIZE
            y = r * TILE_SIZE

            if new_level[r][c] == TILE_GOAL:
                pass

            elif new_level[r][c] == TILE_GHOST:
                enemies.append(Ghost(x, y))
                new_level[r][c] = TILE_AIR

            elif new_level[r][c] == TILE_YATAGARASU:
                enemies.append(Yatagarasu(x, y))
                new_level[r][c] = TILE_AIR

            elif new_level[r][c] == TILE_ONI:
                enemies.append(Oni(x, y))
                new_level[r][c] = TILE_AIR

    return new_level, coins, enemies

def update_cam(camera, player, world_width, world_height, screen_width, screen_height):
    """Centers the camera on the player and clamps the camera's target to the world bounds."""
    
    camera.target.x = player.x + player.width / 2
    camera.target.y = player.y + player.height / 2

    min_x = screen_width / 2
    if player.level == 3:
        max_x = world_width // 3
    else:
        max_x = world_width - screen_width / 2

    if camera.target.x < min_x:
        camera.target.x = min_x
    if camera.target.x > max_x:
        camera.target.x = max_x

    min_y = screen_height / 2 
    max_y = world_height - screen_height // 2
    
    if camera.target.y < min_y:
        camera.target.y = min_y
    if camera.target.y > max_y:
        camera.target.y = max_y
    
    camera.offset.x = screen_width / 2
    camera.offset.y = screen_height / 2


def draw_level(level, tile_rows, tile_cols, tiles):
    """Draws the solid tiles of the level map."""
    for row in range(tile_rows):
        for col in range(tile_cols):
            tile_value = level[row][col]
            x = col * TILE_SIZE
            y = row * TILE_SIZE

            if tile_value == TILE_GOAL:
                draw_rectangle(x, y, TILE_SIZE, TILE_SIZE, WHITE)

            elif tile_value in tiles:
                tex = tiles[tile_value]
                draw_texture_pro(
                    tex,
                    Rectangle(0, 0, tex.width, tex.height),
                    Rectangle(x, y, TILE_SIZE, TILE_SIZE),
                    Vector2(0, 0),
                    0.0,
                    WHITE
                )

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