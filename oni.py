import os
from pyray import *
from enemy import *
from anim import *
import math
import random


class Oni(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        base_dir = os.path.dirname(__file__)
        self.texture = load_texture(os.path.join(base_dir, "assets", "oni.png"))
        self.width = TILE_SIZE * 2.75
        self.height = TILE_SIZE * 2.75

        self.anim_walk   = Animation(1, 4, 1, 1, 0.15, 0.15, 1, 0, 4, self.texture.width // 4)
        self.anim_attack = Animation(1, 4, 1, 1, 0.15, 0.15, 1, 1, 4, self.texture.width // 4)
        self.frame       = self.anim_walk.frame(0, 0)

        # Movement
        self.vx = ONI_PATROL_SPEED
        self.vy = 0.0

        # State machine
        #   "patrol"  – no player nearby, wander in ENEMY_XRANGE
        #   "chase"   – moving toward player.x
        #   "attack"  – within melee range, swinging
        self.state = "patrol"

        self.attack_timer = ONI_ATTACK_COOLDOWN  

        # Track whether this swing has already dealt damage
        self._hit_applied = False

        # Health
        self.health = ONI_HEALTH
        self.invincible = False
        self.i_frames = 0.5

        self.bat_swing = load_sound("assets/audio/whoosh.mp3")


    def _dist_to_player(self, player):
        """Horizontal distance between Oni centre and player centre."""
        return abs((self.x + self.width / 2) - (player.x + player.width / 2))

    def _face_player(self, player):
        """Set facing toward the player."""
        if player.x + player.width / 2 > self.x + self.width / 2:
            self.facing = 1
        else:
            self.facing = -1


    def update(self, dt, level, tile_rows, tile_cols, world_width, player):
        dist = self._dist_to_player(player)

        if self.i_frames <= 0:
            self.invincible = False
        else:
            self.i_frames -= dt

        # ── State transitions ──────────────────────────────────────────────
        if self.state == "patrol":
            if dist <= ONI_AGGRO_RANGE:
                self.state = "chase"

        elif self.state == "chase":
            if dist <= ONI_MELEE_RANGE:
                self.state = "attack"
                self.attack_timer = 0.0
                self._hit_applied = False
                play_sound(self.bat_swing)
            elif dist > ONI_AGGRO_RANGE:
                self.state = "patrol"

        elif self.state == "attack":
            if dist > ONI_MELEE_RANGE:
                self.state = "chase"

        # ── Per-state horizontal behaviour ────────────────────────────────
        if self.state == "patrol":
            if (self.x < self.start_x - ENEMY_XRANGE or
                    self.x > self.start_x + ENEMY_XRANGE):
                self.vx   *= -1
                self.facing *= -1
            self.anim_walk.update(dt)
            self.frame = self.anim_walk.frame(0, 0)

        elif self.state == "chase":
            self._face_player(player)
            self.vx = ONI_CHASE_SPEED * -self.facing
            self.anim_walk.update(dt)
            self.frame = self.anim_walk.frame(0, 0)

        elif self.state == "attack":
            self._face_player(player)
            self.vx = 0.0
            self.anim_attack.update(dt)
            self.frame = self.anim_attack.frame(1, 45)

            self.attack_timer += dt
            part_cooldown = ONI_ATTACK_COOLDOWN * 0.4
            if self.attack_timer >= part_cooldown and not self._hit_applied:
                if self._dist_to_player(player) <= ONI_MELEE_RANGE:
                    player.health -= ONI_ATTACK_DAMAGE
                self._hit_applied = True
            if self.attack_timer >= ONI_ATTACK_COOLDOWN:
                self.attack_timer = 0.0
                self._hit_applied = False

        # ── Gravity ────────────────────────────────────────────────────────
        if self.is_grounded:
            self.vy = 0.0
        self.vy += GRAVITY * dt
        self.is_grounded = False

        # ── X movement + collision ─────────────────────────────────────────
        self.x += self.vx * dt
        self.handle_tile_collision(level, 'X', tile_rows, tile_cols)

        # ── Y movement + collision ─────────────────────────────────────────
        self.y += self.vy * dt
        self.handle_tile_collision(level, 'Y', tile_rows, tile_cols)


    def draw(self):
        dest = Rectangle(int(self.x), int(self.y), int(self.width), int(self.height))
        src  = Rectangle(
            self.frame.x,
            self.frame.y,
            self.frame.width * self.facing,
            self.frame.height,
        )
        if self.invincible:
            draw_texture_pro(self.texture, src, dest, Vector2(0, 0), 0.0, LIGHTGRAY)
        else:
            draw_texture_pro(self.texture, src, dest, Vector2(0, 0), 0.0, WHITE)

        # ── Health bar ────────────────────────────────────────────────────
        bar_width  = int(self.width)
        bar_height = 6
        bar_x      = int(self.x)
        bar_y      = int(self.y) - bar_height - 4

        health_percent = max(self.health / ONI_HEALTH, 0.0)
        filled_w   = int(bar_width * health_percent)

        draw_rectangle(bar_x, bar_y, bar_width, bar_height, Color(100, 100, 100, 200))
        draw_rectangle(bar_x, bar_y, filled_w, bar_height, Color(220, 30, 30, 255))
        draw_rectangle_lines(bar_x, bar_y, bar_width, bar_height, Color(0, 0, 0, 180))

        # Uncomment for debugging:
        # draw_rectangle_lines_ex(self.get_hitbox_rect(), 1, RED)
        # draw_rectangle_lines_ex(dest, 1, WHITE)