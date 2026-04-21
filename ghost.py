from pyray import *
from enemy import *
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
        self.vy = -(dy / dist) * (ENEMY_SPEED * 1.5)

        self.active = True

    def update(self, delta_time):
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time

    def draw(self):
        draw_circle(int(self.x), int(self.y), int(self.radius), ORANGE)


class Ghost(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        
        # Ghost-specific behavior
        self.vx = ENEMY_SPEED * 0.5  # slower drift
        self.vy = 0.0
        
        self.float_offset = random.uniform(0, 2 * math.pi)
        self.float_amplitude = TILE_SIZE * 0.3
        self.float_speed = 2.0
        
        # Shooting
        self.projectiles = []
        self.shoot_cooldown = 2.5  # seconds
        self.shoot_timer = 0.0

    def update(self, delta_time, level, tile_rows, tile_cols, world_width, player):
        # 1. FLOATING MOTION (no gravity)
        self.float_offset += self.float_speed * delta_time
        self.y += math.sin(self.float_offset) * self.float_amplitude * delta_time
        
        # 2. HORIZONTAL DRIFT (no collision reversal needed)
        self.x += self.vx * delta_time
        
        # Optional: reverse direction occasionally
        if random.random() < 0.005:
            self.vx *= -1

        # 3. SHOOTING LOGIC
        self.shoot_timer += get_frame_time()
        if self.shoot_timer >= self.shoot_cooldown and not player.x + WINDOW_WIDTH // 2 < self.x:
            self.shoot_timer = 0.0
            
            proj = MagicProjectile(
                self.x + self.width / 2,
                self.y + self.height / 2,
                player.x,
                player.y
            )
            self.projectiles.append(proj)

        # 4. UPDATE PROJECTILES
        for proj in self.projectiles:
            proj.update(delta_time)

        # Optional: remove off-screen projectiles
        self.projectiles = [
            p for p in self.projectiles
            if 0 <= p.x <= world_width
        ]

    def draw(self):
        # Draw ghost body
        draw_rectangle(int(self.x), int(self.y), int(self.width), int(self.height), SKYBLUE)
        draw_rectangle_lines(int(self.x), int(self.y), int(self.width), int(self.height), WHITE)

        # Eyes (simple)
        eye_size = self.width * 0.15
        draw_circle(int(self.x + self.width * 0.3), int(self.y + self.height * 0.4), int(eye_size), WHITE)
        draw_circle(int(self.x + self.width * 0.7), int(self.y + self.height * 0.4), int(eye_size), WHITE)

        # Draw projectiles
        for proj in self.projectiles:
            print("Projectile")
            proj.draw()