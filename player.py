from pyray import *
from os.path import join
from collections import deque
from platformer import *
from settings import * 
from random import uniform
from anim import *

class Player:
    def __init__(self, x, y):
        # Store starting position for reset
        self.start_x = x 
        self.start_y = y
        # Current position (top-left for collision)
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        
        # Physics
        self.vx = 0.0
        self.vy = 0.0
        self.is_grounded = False

    def get_rect(self):
        """Returns the player's collision bounding box (top-left, width, height)."""
        return (self.x, self.y, self.width, self.height)

    def update(self, delta_time, level):
        # 1. Handle Input (Horizontal Movement)
        self.vx = 0.0
        if is_key_down(KeyboardKey.KEY_LEFT) or is_key_down(KeyboardKey.KEY_A):
            self.vx = -PLAYER_SPEED
        if is_key_down(KeyboardKey.KEY_RIGHT) or is_key_down(KeyboardKey.KEY_D):
            self.vx = PLAYER_SPEED

        # --- Velocity Zeroing for Stability ---
        if self.is_grounded:
            self.vy = 0.0
            
        # 2. Handle Input (Jump)
        if (is_key_pressed(KeyboardKey.KEY_SPACE) or is_key_pressed(KeyboardKey.KEY_UP)) and self.is_grounded:
            self.vy = JUMP_VELOCITY

        # 3. Apply Gravity
        self.vy += GRAVITY * delta_time
        if self.vy > 1000:
            self.vy = 1000

        # --- Reset grounded state at start of frame update ---
        self.is_grounded = False

        # 4. Apply Movement (Separated for X and Y collision checks)
        
        # Apply X movement
        self.x += self.vx * delta_time
        self.handle_tile_collision(level, 'X')
        
        # Apply Y movement
        self.y += self.vy * delta_time
        self.handle_tile_collision(level, 'Y')
        
        # --- Safety Clamp to World Bounds ---
        self.x = max(0, min(self.x, WORLD_WIDTH - self.width))
        
    def handle_tile_collision(self, level, axis):
        """Performs AABB collision checks against solid tiles and resolves the collision."""
        player_rect = self.get_rect()
        px, py, pw, ph = player_rect
        
        min_col = int(px / TILE_SIZE)
        max_col = int((px + pw) / TILE_SIZE)
        min_row = int(py / TILE_SIZE)
        max_row = int((py + ph) / TILE_SIZE)

        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                
                if row < 0 or row >= TILE_ROWS or col < 0 or col >= TILE_COLS:
                    continue

                if level[row][col] == TILE_LAVA:
                    self.reset()
                    break
                
                if level[row][col] == TILE_SOLID:
                    tile_rect = (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    
                    if check_collision_recs(player_rect, tile_rect):
                        
                        if axis == 'X':
                            if self.vx > 0: # Moving Right
                                self.x = tile_rect[0] - self.width
                            elif self.vx < 0: # Moving Left
                                self.x = tile_rect[0] + TILE_SIZE
                            self.vx = 0.0 
                            
                        elif axis == 'Y':
                            if self.vy >= 0: # Falling (Hitting Ground)
                                self.y = tile_rect[1] - self.height
                                self.is_grounded = True 
                            elif self.vy < 0: # Jumping (Hitting Ceiling)
                                self.y = tile_rect[1] + TILE_SIZE
                                
                            self.vy = 0.0 
                            
                        player_rect = self.get_rect()
                        px, py, pw, ph = player_rect
                        
    def check_collection(self, collectibles):
        """Checks for collision with coins and returns indices of collected coins."""
        collected_indices = []
        player_rect = self.get_rect()
        coin_collision_size = TILE_SIZE * 0.5
        
        for i, (cx, cy) in enumerate(collectibles):
            coin_x = cx - coin_collision_size / 2
            coin_y = cy - coin_collision_size / 2
            coin_rect = (coin_x, coin_y, coin_collision_size, coin_collision_size)

            if check_collision_recs(player_rect, coin_rect):
                collected_indices.append(i)
                
        return collected_indices
    
    def check_enemy_collision(self, enemies):
        """Checks for collision with enemies and determines outcome (stomp or death).
        Returns (hit_type, enemy_index) or (None, -1).
        hit_type: "STOMP" (safe kill) or "LETHAL" (death)
        """
        player_rect = self.get_rect()
        px, py, pw, ph = player_rect
        
        for i, enemy in enumerate(enemies):
            enemy_rect = enemy.get_rect()
            
            if check_collision_recs(player_rect, enemy_rect):
                
                # STOMP Condition: 
                # 1. Player is falling (vy > 0) 
                # 2. Player's bottom is above the enemy's mid-point (approximate stomping zone)
                is_stompable_zone = py + ph < enemy.y + enemy.height * 0.5 
                
                if self.vy > 0 and is_stompable_zone:
                    return "STOMP", i
                else:
                    # Lethal collision (side, head, or missing the stomp zone)
                    return "LETHAL", i
                    
        return None, -1
    
    def reset(self):
        """Resets the player to their starting position."""
        self.x = self.start_x
        self.y = self.start_y
        self.vx = 0.0
        self.vy = 0.0
        self.is_grounded = False

    def draw(self):
        """Draws the player at their world coordinates."""
        draw_rectangle(int(self.x), int(self.y), int(self.width), int(self.height), BLUE) 
        if self.is_grounded:
             draw_rectangle_lines(int(self.x), int(self.y), int(self.width), int(self.height), WHITE)
        else:
             draw_rectangle_lines(int(self.x), int(self.y), int(self.width), int(self.height), GRAY)
