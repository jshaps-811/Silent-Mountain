from pyray import *
from os.path import join
from collections import deque
from platformer import *
from settings import * 
from random import uniform
from anim import *


class Projectile:
    """A straight-travelling ranged shot fired by the player."""

    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.vx = PROJECTILE_SPEED * direction   
        self.alive = True
        self.life  = PROJECTILE_LIFE

    def update(self, delta_time, level, tile_rows, tile_cols):
        self.life -= delta_time
        if self.life <= 0:
            self.alive = False
            return

        self.x += self.vx * delta_time

        # Tile collision – can't shoot through tiles
        col = int(self.x / TILE_SIZE)
        row = int(self.y / TILE_SIZE)
        if 0 <= row < tile_rows and 0 <= col < tile_cols:
            if level[row][col] == TILE_SOLID:
                self.alive = False

    def get_rect(self):
        r = PROJECTILE_RADIUS
        return (self.x - r, self.y - r, r * 2, r * 2)

    def draw(self):
        # Glowing orb: bright white core with a coloured halo
        cx, cy = int(self.x), int(self.y)
        draw_circle(cx, cy, PROJECTILE_RADIUS + 3, Color(80, 160, 255, 120))   # outer glow
        draw_circle(cx, cy, PROJECTILE_RADIUS,     Color(160, 210, 255, 220))  # mid ring
        draw_circle(cx, cy, PROJECTILE_RADIUS - 2, WHITE)                      # bright core


class Player:
    def __init__(self, x, y):
        # Store starting position for reset
        self.start_x = x 
        self.start_y = y
        # Current position (top-left for collision)
        self.x = x
        self.y = y
        self.width  = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        
        # Physics
        self.vx = 0.0
        self.vy = 0.0
        self.is_grounded = False

        # Facing direction: 1 = right, -1 = left
        self.facing = 1

        # --- Melee state ---
        self.is_attacking      = False   # True while hitbox is active
        self.attack_timer      = 0.0    # counts down active duration
        self.attack_cooldown   = 0.0    # counts down between attacks

        # --- Ranged state ---
        self.projectiles       = []     # list[Projectile]
        self.shoot_cooldown    = 0.0    # counts down between shots

    # ------------------------------------------------------------------
    def startup(self):
        # Textures
        self.walk_texture = load_texture("assets/monk_walk.png")
        self.animation = Animation(1, 5, 1, 1, 0.1, 0.1, 1, 0, 5,
                                   self.walk_texture.width // 5)
        self.frame = self.animation.frame(0)

    # ------------------------------------------------------------------
    def get_rect(self):
        """Returns the player's collision bounding box (top-left, width, height)."""
        return (self.x, self.y, self.width, self.height)

    def get_melee_rect(self):
        """Returns the melee hitbox rect in front of the player."""
        if self.facing == 1:
            mx = self.x + self.width          # right side
        else:
            mx = self.x - MELEE_RANGE         # left side
        my = self.y + (self.height - MELEE_HEIGHT) / 2
        return (mx, my, MELEE_RANGE, MELEE_HEIGHT)

    # ------------------------------------------------------------------
    def update(self, delta_time, level, tile_rows, tile_cols, world_width):

        # ── Cooldown timers ──────────────────────────────────────────
        if self.attack_cooldown > 0:
            self.attack_cooldown -= delta_time
        if self.shoot_cooldown > 0:
            self.shoot_cooldown  -= delta_time

        # ── Melee attack timing ──────────────────────────────────────
        if self.is_attacking:
            self.attack_timer -= delta_time
            if self.attack_timer <= 0:
                self.is_attacking = False

        # ── Input: melee (Left Shift) ────────────────────────────────
        if (is_key_pressed(KeyboardKey.KEY_LEFT_SHIFT) and
                not self.is_attacking and self.attack_cooldown <= 0):
            self.is_attacking    = True
            self.attack_timer    = MELEE_DURATION
            self.attack_cooldown = MELEE_COOLDOWN

        # ── Input: ranged (Z key) ────────────────────────────────────
        if is_key_pressed(KeyboardKey.KEY_Z) and self.shoot_cooldown <= 0:
            # Spawn projectile from the centre-front edge of the player
            spawn_x = self.x + self.width  if self.facing == 1 else self.x
            spawn_y = self.y + self.height / 2
            self.projectiles.append(Projectile(spawn_x, spawn_y, self.facing))
            self.shoot_cooldown = PROJECTILE_COOLDOWN

        # ── Projectile updates ───────────────────────────────────────
        for p in self.projectiles:
            p.update(delta_time, level, tile_rows, tile_cols)
        self.projectiles = [p for p in self.projectiles if p.alive]

        # ── Horizontal movement ──────────────────────────────────────
        self.vx = 0.0
        if is_key_down(KeyboardKey.KEY_LEFT)  or is_key_down(KeyboardKey.KEY_A):
            self.vx = -PLAYER_SPEED
            self.facing = -1
        if is_key_down(KeyboardKey.KEY_RIGHT) or is_key_down(KeyboardKey.KEY_D):
            self.vx = PLAYER_SPEED
            self.facing = 1

        # ── Velocity zeroing for stability ───────────────────────────
        if self.is_grounded:
            self.vy = 0.0
            
        # ── Jump ─────────────────────────────────────────────────────
        if ((is_key_pressed(KeyboardKey.KEY_SPACE) or
             is_key_pressed(KeyboardKey.KEY_UP)) and self.is_grounded):
            self.vy = JUMP_VELOCITY

        # ── Gravity ──────────────────────────────────────────────────
        self.vy += GRAVITY * delta_time
        if self.vy > 1000:
            self.vy = 1000

        # ── Reset grounded before tile sweep ─────────────────────────
        self.is_grounded = False

        # ── Movement + tile collision (X then Y) ─────────────────────
        self.x += self.vx * delta_time
        self.handle_tile_collision(level, 'X', tile_rows, tile_cols)
        
        self.y += self.vy * delta_time
        self.handle_tile_collision(level, 'Y', tile_rows, tile_cols)

        # ── World bounds clamp ────────────────────────────────────────
        self.x = max(0, min(self.x, world_width - 2 * self.width))

        # ── Animation ────────────────────────────────────────────────
        if self.vx != 0:
            self.animation.update(delta_time)
            self.frame = self.animation.frame(0)

    # ------------------------------------------------------------------
    def handle_tile_collision(self, level, axis, tile_rows, tile_cols):
        """Performs AABB collision checks against solid tiles and resolves."""
        player_rect = self.get_rect()
        px, py, pw, ph = player_rect
        
        min_col = int(px / TILE_SIZE)
        max_col = int((px + pw) / TILE_SIZE)
        min_row = int(py / TILE_SIZE)
        max_row = int((py + ph) / TILE_SIZE)

        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):

                if row < 0 or row >= tile_rows or col < 0 or col >= tile_cols:
                    continue

                if level[row][col] == TILE_GOAL:
                    self.reset()
                    break
                
                if level[row][col] == TILE_SOLID:
                    tile_rect = (col * TILE_SIZE, row * TILE_SIZE,
                                 TILE_SIZE, TILE_SIZE)
                    
                    if check_collision_recs(player_rect, tile_rect):
                        
                        if axis == 'X':
                            if self.vx > 0:
                                self.x = tile_rect[0] - self.width
                            elif self.vx < 0:
                                self.x = tile_rect[0] + TILE_SIZE
                            self.vx = 0.0 
                            
                        elif axis == 'Y':
                            if self.vy >= 0:
                                self.y = tile_rect[1] - self.height
                                self.is_grounded = True 
                            elif self.vy < 0:
                                self.y = tile_rect[1] + TILE_SIZE
                            self.vy = 0.0 
                            
                        player_rect = self.get_rect()
                        px, py, pw, ph = player_rect

    # ------------------------------------------------------------------
    def check_collection(self, collectibles):
        """Checks for collision with coins; returns indices of collected ones."""
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

    # ------------------------------------------------------------------
    def check_enemy_collision(self, enemies):
        """Checks player body vs enemies (stomp or lethal).
        Returns (hit_type, enemy_index) or (None, -1).
        """
        player_rect = self.get_rect()
        px, py, pw, ph = player_rect
        
        for i, enemy in enumerate(enemies):
            enemy_rect = enemy.get_rect()
            if check_collision_recs(player_rect, enemy_rect):
                is_stompable_zone = py + ph < enemy.y + enemy.height * 0.5
                if self.vy > 0 and is_stompable_zone:
                    return "STOMP", i
                else:
                    return "LETHAL", i
                    
        return None, -1

    def check_melee_hit(self, enemies):
        """Returns indices of enemies hit by the active melee hitbox.
        Call only when self.is_attacking is True.
        """
        if not self.is_attacking:
            return []

        melee_rect = self.get_melee_rect()
        hit_indices = []
        for i, enemy in enumerate(enemies):
            if check_collision_recs(melee_rect, enemy.get_rect()):
                hit_indices.append(i)
        return hit_indices

    def check_projectile_hits(self, enemies):
        """Returns list of (projectile_index, enemy_index) pairs for hits.
        Marks hit projectiles as dead.
        """
        hits = []
        for pi, proj in enumerate(self.projectiles):
            proj_rect = proj.get_rect()
            for ei, enemy in enumerate(enemies):
                if check_collision_recs(proj_rect, enemy.get_rect()):
                    hits.append((pi, ei))
                    proj.alive = False
                    break   # one enemy per projectile
        return hits

    # ------------------------------------------------------------------
    def reset(self):
        """Resets the player to their starting position."""
        self.x = self.start_x
        self.y = self.start_y
        self.vx = 0.0
        self.vy = 0.0
        self.is_grounded  = False
        self.is_attacking = False
        self.attack_timer = 0.0
        self.projectiles.clear()

    # ------------------------------------------------------------------
    def draw(self):
        """Draws projectiles, the player sprite, and (optionally) debug rects."""

        # ── Projectiles (draw behind player) ─────────────────────────
        for p in self.projectiles:
            p.draw()

        # ── Player sprite ─────────────────────────────────────────────
        dest_rect = Rectangle(
            self.x + self.width  / 2,
            self.y + self.height / 2,
            self.width,
            self.height
        )
        origin = Vector2(self.width / 2, self.height / 2)

        src_frame = Rectangle(
            self.frame.x,
            self.frame.y,
            self.frame.width  * self.facing,
            self.frame.height
        )

        draw_texture_pro(self.walk_texture, src_frame, dest_rect, origin, 0, WHITE)

        # ── Melee hitbox flash ────────────────────────────────────────
        if self.is_attacking:
            mx, my, mw, mh = self.get_melee_rect()
            # Bright slash indicator that fades with the remaining duration
            alpha = int(200 * (self.attack_timer / MELEE_DURATION))
            draw_rectangle(int(mx), int(my), int(mw), int(mh),
                           Color(255, 220, 80, alpha))
            draw_rectangle_lines(int(mx), int(my), int(mw), int(mh),
                                 Color(255, 255, 180, min(alpha + 55, 255)))

        # ── Debug collision outline 
        # draw_rectangle_lines(int(self.x), int(self.y),
        #                      int(self.width), int(self.height), WHITE)