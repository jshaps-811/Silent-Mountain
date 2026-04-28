from pyray import *
from settings import *


class Enemy:
    def __init__(self, x, y):
        # Position (top-left for collision)
        self.x = x
        self.y = y
        self.width = TILE_SIZE * 0.7
        self.height = TILE_SIZE * 0.7

        self.start_x = x
        self.start_y = y
        
        # Physics/Movement
        self.vx = ENEMY_SPEED # Start moving right
        self.vy = 0.0 
        self.is_grounded = False

    def get_rect(self):
        """Returns the enemy's collision bounding box."""
        return (self.x, self.y, self.width, self.height)

    def update(self, delta_time, level, tile_rows, tile_cols, world_width, player):
        # 1. Apply Gravity
        if self.is_grounded:
            self.vy = 0.0
        self.vy += GRAVITY * delta_time
        self.is_grounded = False 

        # 2. Apply Movement 

        # Apply X movement
        if not player.x < self.x - WINDOW_WIDTH // 2:
            self.x += self.vx * delta_time
            self.handle_tile_collision(level, 'X', tile_rows, tile_cols)

        if abs(self.x - self.start_x) > ENEMY_XRANGE:
            self.vx *= -1
        
        if abs(self.y - self.start_y) > ENEMY_YRANGE:
            self.vy *= -1

        # Apply Y movement
        self.y += self.vy * delta_time
        self.handle_tile_collision(level, 'Y', tile_rows, tile_cols)

    def handle_tile_collision(self, level, axis, tile_rows, tile_cols):
        """Enemy collision: reverses direction on horizontal wall contact, respects vertical floor contact."""
        enemy_rect = self.get_rect()
        px, py, pw, ph = enemy_rect
        
        min_col = int(px / TILE_SIZE)
        max_col = int((px + pw) / TILE_SIZE)
        min_row = int(py / TILE_SIZE)
        max_row = int((py + ph) / TILE_SIZE)

        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):

                if row < 0 or row >= tile_rows or col < 0 or col >= tile_cols:
                    continue

                if level[row][col] == TILE_TOP_GRASS or level[row][col] == TILE_BOTTOM_GRASS:
                    tile_rect = (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    
                    if check_collision_recs(enemy_rect, tile_rect):
                        
                        if axis == 'X':
                            # Reverses direction on horizontal collision
                            if self.vx > 0:
                                self.x = tile_rect[0] - self.width
                            elif self.vx < 0:
                                self.x = tile_rect[0] + TILE_SIZE
                            self.vx *= -1 # Reverse direction
                            
                        elif axis == 'Y':
                            if self.vy >= 0: # Hitting Ground
                                self.y = tile_rect[1] - self.height
                                self.is_grounded = True 
                                
                            self.vy = 0.0 
                            
                        enemy_rect = self.get_rect() # Update rect after resolution

    def draw(self):
        """Draws the enemy as a red rectangle with a directional indicator."""
        draw_rectangle(int(self.x), int(self.y), int(self.width), int(self.height), RED)
        draw_rectangle_lines(int(self.x), int(self.y), int(self.width), int(self.height), BLACK)
        
        # Draw a small indicator for direction
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2
        indicator_size = self.width * 0.2
        
        if self.vx > 0: # Moving Right
            draw_triangle(Vector2(center_x + indicator_size, center_y), 
                         Vector2(center_x - indicator_size, center_y - indicator_size), 
                         Vector2(center_x - indicator_size, center_y + indicator_size), WHITE)
        elif self.vx < 0: # Moving Left
            draw_triangle(Vector2(center_x - indicator_size, center_y), 
                         Vector2(center_x + indicator_size, center_y - indicator_size), 
                         Vector2(center_x + indicator_size, center_y + indicator_size), WHITE)
