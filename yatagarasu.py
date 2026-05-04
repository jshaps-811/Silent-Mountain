from pyray import *
import player
from settings import *
from enemy import *
import random
import math
import os
from anim import *


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

        base_dir =  os.path.dirname(__file__)
        self.texture = load_texture(os.path.join(base_dir, "assets", "yatagarasu.png"))
        self.animation = Animation(1, 4, 1, 1, 0.2, 0.2, 1, 0, 4, self.texture.width // 4)
        self.frame = self.animation.frame(0, 50)

        self.attack_sound = load_sound("assets/audio/slice.mp3")

    def get_melee_rect(self):
        """Returns the melee hitbox rect in front of the player."""
        if self.facing == -1:
            mx = self.x + self.width          # right side
        else:
            mx = self.x - MELEE_RANGE         # left side
        my = self.y + (self.height - MELEE_HEIGHT) / 2
        return (mx, my, MELEE_WIDTH, MELEE_HEIGHT)

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
        if random.random() < 0.005 or self.x < self.start_x - ENEMY_XRANGE or self.x > self.start_x + ENEMY_XRANGE:
            self.vx *= -1
            self.facing *= -1

        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= delta_time

        # Attack Logic
        self.attack_timer -= delta_time
        if self.attack_timer <= 0:
                self.is_attacking = False

        if abs(self.x - player.x) < ATT_THRESHOLD and abs(self.y - player.y) < ATT_THRESHOLD:
            if not self.is_attacking and self.attack_cooldown <= 0:
                self.is_attacking    = True
                play_sound(self.attack_sound)
                self.attack_timer    = MELEE_DURATION
                self.attack_cooldown = MELEE_COOLDOWN
        
        self.animation.update(delta_time)
        self.frame = self.animation.frame(0, 0)

    def draw(self):
        # draw_rectangle(int(self.x), int(self.y), int(self.width), int(self.height), BLACK)
        # draw_rectangle_lines(int(self.x), int(self.y), int(self.width), int(self.height), WHITE)

        dest = self.get_rect()
        src = Rectangle(
            self.frame.x,
            self.frame.y,
            self.frame.width * -self.facing,
            self.frame.height
        )
        draw_texture_pro(self.texture, src, dest, Vector2(0, 0), 0.0, WHITE)


