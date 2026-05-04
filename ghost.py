import os
from pyray import *
from enemy import *
from anim import *
import math
import random


class MagicProjectile:
    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        self.radius = TILE_SIZE * 0.2
        
        # Direction toward player
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx*dx + dy*dy) or 1

        self.vx = -(dx / dist) * (ENEMY_SPEED * 1.5)
        self.vy = 0

        self.active = True


    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self):
    # Glowing orb: bright white core with a fiery halo
        cx, cy = int(self.x), int(self.y)
        draw_circle(cx, cy, PROJECTILE_RADIUS + 3, Color(200, 40, 0, 120))    # outer glow
        draw_circle(cx, cy, PROJECTILE_RADIUS,     Color(255, 120, 20, 220))  # mid ring
        draw_circle(cx, cy, PROJECTILE_RADIUS - 2, Color(255, 230, 180, 255)) # bright core


class Ghost(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        base_dir =  os.path.dirname(__file__)
        self.texture = load_texture(os.path.join(base_dir, "assets", "ghost.png"))
        self.animation = Animation(1, 3, 1, 1, 0.1, 0.1, 1, 0, 3, self.texture.width // 3)
        self.frame = self.animation.frame(0, 0)
        
        # Ghost-specific behavior
        self.vx = ENEMY_SPEED * 0.5  
        self.vy = 0.0
        
        self.float_offset = random.uniform(0, 2 * math.pi)
        self.float_amplitude = TILE_SIZE * 0.3
        self.float_speed = 2.0
        
        # Shooting
        self.projectiles = []
        self.shoot_timer = 0.0
        self.proj_sound = load_sound("assets/audio/projectile.wav")
    

    def update(self, dt, level, tile_rows, tile_cols, world_width, player):
        # Floating Motion
        self.float_offset += self.float_speed * dt
        self.y += math.sin(self.float_offset) * self.float_amplitude * dt

        # Horizontal Drift (no collision reversal needed)
        self.x += self.vx * dt
        
        # Reverse direction occasionally
        if random.random() < 0.005 or self.x < self.start_x - ENEMY_XRANGE or self.x > self.start_x + ENEMY_XRANGE:
            self.vx *= -1
            self.facing *= -1

        # SHOOTING LOGIC
        self.shoot_timer += dt

        facing_player = (self.facing == 1 and player.x > self.x) or \
                            (self.facing == -1 and player.x < self.x)

        if self.shoot_timer >= SHOT_COOLDOWN and facing_player:
            self.shoot_timer = 0.0
            proj = MagicProjectile(
                self.x + self.width / 2,
                self.y + self.height / 2,
                player.x,
                player.y
            )
            self.projectiles.append(proj)
            play_sound(self.proj_sound)

        # UPDATE PROJECTILES
        for proj in self.projectiles:
            proj.update(dt)

        # Remove off-screen projectiles
        self.projectiles = [
            proj for proj in self.projectiles
            if abs(proj.x - self.x) <= WINDOW_WIDTH
        ]

        self.animation.update(dt)

    def draw(self):
        # draw_rectangle(int(self.x), int(self.y), int(self.width), int(self.height), SKYBLUE)
        # draw_rectangle_lines(int(self.x), int(self.y), int(self.width), int(self.height), WHITE)

        dest = Rectangle(int(self.x), int(self.y), int(self.width), int(self.height))
        src = Rectangle(
            self.frame.x,
            self.frame.y,
            self.frame.width * -self.facing,
            self.frame.height
        )
        draw_texture_pro(self.texture, src, dest, Vector2(0, 0), 0.0, WHITE)

        # --- Draw Hitbox ---
        # draw_rectangle_lines_ex(self.get_hitbox_rect(), 1, WHITE)

        # Draw projectiles
        for proj in self.projectiles:
            # print("Projectile")
            proj.draw()