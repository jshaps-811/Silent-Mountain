from pyray import *
import player
from settings import *
from enemy import *
import random
import math


class Yatagarasu(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        
        # Yatagarasu-specific behavior
        self.vx = ENEMY_SPEED * 0.8  
        self.vy = 0.0
        
        self.float_offset = random.uniform(0, 2 * math.pi)
        self.float_amplitude = TILE_SIZE * 2.0
        self.float_speed = 2.0

        self.is_attacking      = False   # True while hitbox is active
        self.attack_timer      = 0.0    # counts down active duration
        self.attack_cooldown   = 0.0    # counts down between attacks

        self.facing = 1  # 1 for right, -1 for left

    def get_melee_rect(self):
        """Returns the melee hitbox rect in front of the player."""
        if self.facing == -1:
            mx = self.x + self.width          # right side
        else:
            mx = self.x - MELEE_RANGE         # left side
        my = self.y + (self.height - MELEE_HEIGHT) / 2
        return (mx, my, MELEE_RANGE, MELEE_HEIGHT)
    
    def check_melee_hit(self, player):
        """Returns indices of enemies hit by the active melee hitbox.
        Call only when self.is_attacking is True.
        """
        if not self.is_attacking:
            return False

        melee_rect = self.get_melee_rect()
        if check_collision_recs(melee_rect, player.get_rect()):
            return True

        return False

    def update(self, delta_time, level, tile_rows, tile_cols, world_width, player):
        # Floating Motion
        self.float_offset += self.float_speed * delta_time
        self.y += math.sin(self.float_offset) * self.float_amplitude * delta_time

        # Horizontal Drift (no collision reversal needed)
        self.x += self.vx * delta_time
        
        # Reverse direction occasionally
        if random.random() < 0.005:
            self.vx *= -1
            self.facing *= -1

        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= delta_time

        # Attack Logic, similar to Player
        self.attack_timer -= delta_time
        if self.attack_timer <= 0:
                self.is_attacking = False

        if abs(self.x - player.x) < ATT_THRESHOLD and abs(self.y - player.y) < ATT_THRESHOLD:
            if not self.is_attacking and self.attack_cooldown <= 0:
                self.is_attacking    = True
                self.attack_timer    = MELEE_DURATION
                self.attack_cooldown = MELEE_COOLDOWN

        if self.check_melee_hit(player):
            player.health -= 25
            self.is_attacking = False


    def draw(self):
        # Draw yatagarasu body
        draw_rectangle(int(self.x), int(self.y), int(self.width), int(self.height), BLACK)
        draw_rectangle_lines(int(self.x), int(self.y), int(self.width), int(self.height), WHITE)

        if self.attack_timer > 0:
            mx, my, mw, mh = self.get_melee_rect()
            # Bright slash indicator that fades with the remaining duration
            alpha = int(200 * (self.attack_timer / MELEE_DURATION))
            draw_rectangle(int(mx), int(my), int(mw), int(mh),
                           Color(255, 220, 80, alpha))
            draw_rectangle_lines(int(mx), int(my), int(mw), int(mh),
                                 Color(255, 255, 180, min(alpha + 55, 255)))

