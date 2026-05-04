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

    def update(self, dt, level, tile_rows, tile_cols):
        self.life -= dt
        if self.life <= 0:
            self.alive = False
            return

        self.x += self.vx * dt

        # Tile collision – can't shoot through tiles
        col = int(self.x / TILE_SIZE)
        row = int(self.y / TILE_SIZE)
        if 0 <= row < tile_rows and 0 <= col < tile_cols:
            if level[row][col] == TILE_TOP_GRASS or level[row][col] == TILE_BOTTOM_GRASS:
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
        self.knockback_vx = 0.0
        self.knockback_vy = 0.0
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

        # --- Health ---
        self.health = BASE_HEALTH

        # --- Level ---
        self.level = 1
        self.all_enemies_defeated = False

        # --- Breath ---
        self.breath = BREATH_MAX        
        self.breath_max = BREATH_MAX

        # --- Animation State ---
        self.state = "IDLE"
        self.prev_state = None

        # --- Hit by Attack ---
        self.invincible = True
        self.invincibility_counter = INVINCIBILITY_DURATION

    def startup(self):
        # Textures
        self.texture = load_texture("assets/monk.png")
        self.animation = Animation(1, 6, 1, 1, 0.06, 0.06, 1, 0, 6,
                                   self.texture.width // 6)
        self.frame = self.animation.frame(0, 0)
        self.whirlwind_tex = load_texture("assets/whirlwind.png")
        self.whirlwind = Animation(1, 3, 1, 1, 0.1, 0.1, 0, 0, 3, self.whirlwind_tex.width // 3)
        self.whirlwind_frame = self.whirlwind.frame(0, 0)
        self.proj_sound_short = load_sound("assets/audio/flute_shot_short.wav")
        self.proj_sound_long = load_sound("assets/audio/flute_shot_long.wav")
        self.damage_tick = load_sound("assets/audio/damage_tick.mp3")

    def get_rect(self):
        """Returns the player's collision bounding box (top-left, width, height)."""
        return (self.x, self.y, self.width, self.height)

    def get_coll_rect(self):
        """Returns the player's collision rectangle (for tile collisions)."""
        return (self.x + TILE_SIZE // 3, self.y + self.height // 4, TILE_SIZE - TILE_SIZE // 3, self.height * 3 // 4)

    def get_melee_rect(self):
        """Returns the melee hitbox rect in front of the player."""
        if self.facing == 1:
            mx = self.x + MELEE_RANGE         # right side
        else:
            mx = self.x - MELEE_RANGE        # left side
        my = self.y + (self.height - MELEE_HEIGHT) / 2
        return Rectangle(mx, my, MELEE_WIDTH, MELEE_HEIGHT)


    def set_state(self, new_state):
        if new_state == self.state:
            return

        self.prev_state = self.state
        self.state = new_state

        if self.state == "JUMPING":
            self.animation.reset(AnimationType.ONESHOT)
        elif self.state in ("RUNNING", "ATTACKING"):
            self.animation.reset(AnimationType.REPEATING)

    def apply_damage(self, amount):
        if not self.invincible:
            self.health -= amount
            self.invincible = True
            self.invincibility_counter = INVINCIBILITY_DURATION
            play_sound(self.damage_tick)

    def update(self, dt, level, tile_rows, tile_cols, world_width):

        # ── Breath recharge ──────────────────────────────────────────
        self.breath = min(self.breath_max,
                          self.breath + BREATH_REGEN * dt)

        # ── Cooldown timers ──────────────────────────────────────────
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        if self.shoot_cooldown > 0:
            self.shoot_cooldown  -= dt

        # ── Melee attack timing ──────────────────────────────────────
        if self.is_attacking:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.is_attacking = False

        # --- Hit by Attack ---
        if self.invincible:
            self.invincibility_counter -= dt
            if self.invincibility_counter <= 0:
                self.invincible = False

        # ── Input: melee (X key) ────────────────────────────────
        if (is_key_pressed(KeyboardKey.KEY_X) and
                self.is_grounded and
                not self.is_attacking and self.attack_cooldown <= 0
                and self.breath >= BREATH_COST_MELEE):          
            self.is_attacking    = True
            self.attack_timer    = MELEE_DURATION
            self.attack_cooldown = MELEE_COOLDOWN
            self.breath         -= BREATH_COST_MELEE 
            play_sound(self.proj_sound_short)
        
        if self.is_attacking:
            self.whirlwind.update(dt)
            self.whirlwind_frame = self.whirlwind.frame(0, WHIRLWIND_OFFSET // 2)

        # ── Input: ranged (Z key) ────────────────────────────────────
        if (is_key_pressed(KeyboardKey.KEY_Z) and self.is_grounded and self.shoot_cooldown <= 0
                and self.breath >= BREATH_COST_RANGED):    
            # Spawn projectile from the centre-front edge of the player
            spawn_x = self.x + self.width  if self.facing == 1 else self.x
            spawn_y = self.y + self.height / 2
            self.projectiles.append(Projectile(spawn_x, spawn_y, self.facing))
            self.shoot_cooldown = PROJECTILE_COOLDOWN
            self.breath        -= BREATH_COST_RANGED
            play_sound(self.proj_sound_long)

        # ── Projectile updates ───────────────────────────────────────
        for p in self.projectiles:
            p.update(dt, level, tile_rows, tile_cols)
        self.projectiles = [p for p in self.projectiles if p.alive]

        # ── Horizontal movement ──────────────────────────────────────
        self.vx = 0.0
        if not self.is_attacking:
            if is_key_down(KeyboardKey.KEY_LEFT):
                self.vx = -PLAYER_SPEED
                self.facing = -1

            elif is_key_down(KeyboardKey.KEY_RIGHT):
                self.vx = PLAYER_SPEED
                self.facing = 1
        
        self.vx += self.knockback_vx
        self.vy += self.knockback_vy

        # Decay knockback each frame
        self.knockback_vx *= 0.9
        self.knockback_vy *= 0.75

        # Stop knockback once negligible
        if abs(self.knockback_vx) < 1.0:
            self.knockback_vx = 0.0
        if abs(self.knockback_vy) < 1.0:
            self.knockback_vy = 0.0

        # ── Velocity zeroing for stability ───────────────────────────
        if self.is_grounded:
            self.vy = 0.0
            
        # ── Jump ─────────────────────────────────────────────────────
        if (is_key_pressed(KeyboardKey.KEY_SPACE)) and self.is_grounded:
            self.vy = JUMP_VELOCITY

        # ── Gravity ──────────────────────────────────────────────────
        self.vy += GRAVITY * dt
        if self.vy > 1000:
            self.vy = 1000

        # ── Reset grounded before tile sweep ─────────────────────────
        self.is_grounded = False

        # ── Movement + tile collision (X then Y) ─────────────────────
        self.x += self.vx * dt
        self.handle_tile_collision(level, 'X', tile_rows, tile_cols)
        
        self.y += self.vy * dt
        self.handle_tile_collision(level, 'Y', tile_rows, tile_cols)

        # ── World bounds clamp ────────────────────────────────────────
        self.x = max(0, min(self.x, world_width - 2 * self.width))


        # --- Apply Animation ---
        if self.state == "JUMPING" and self.is_grounded and not self.animation.done:
            self.set_state("JUMPING")
        elif not self.is_grounded:
            self.set_state("JUMPING")
        elif self.is_attacking:
            self.set_state("ATTACKING")
        elif self.vx != 0:
            self.set_state("RUNNING")
        else:
            self.set_state("IDLE")

        match self.state:
            case "IDLE":
                self.frame = self.animation.frame(0, -15)

            case "ATTACKING":
                self.animation.update(dt)
                self.frame = self.animation.frame(3, 10)

            case "RUNNING":
                self.animation.update(dt)
                self.frame = self.animation.frame(1, 0)

            case "JUMPING":
                self.animation.update(dt)
                if not self.is_grounded and self.animation.cur > 4:
                    self.animation.cur = 4
                    self.animation.done = False
                self.frame = self.animation.frame(2, 10)


    def handle_tile_collision(self, level, axis, tile_rows, tile_cols):
        """Performs AABB collision checks against solid tiles and resolves."""
        player_rect = self.get_coll_rect()
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
                    tile_rect = (col * TILE_SIZE, row * TILE_SIZE,
                                 TILE_SIZE, TILE_SIZE)
                    if check_collision_recs(player_rect, tile_rect) and self.all_enemies_defeated:
                        self.level += 1
                        self.reset()
                        break

                if level[row][col] in COLLISION_TILES:
                    tile_rect = (col * TILE_SIZE, row * TILE_SIZE,
                                 TILE_SIZE, TILE_SIZE)
                    
                    if check_collision_recs(player_rect, tile_rect):
                        
                        if axis == 'X':
                            if self.vx > 0:
                                self.x = (tile_rect[0] - pw) - TILE_SIZE // 3
                            elif self.vx < 0:
                                self.x = (tile_rect[0] + TILE_SIZE) - TILE_SIZE // 3
                            self.vx = 0.0

                        elif axis == 'Y':
                            if self.vy >= 0:
                                self.y = tile_rect[1] - self.height 
                                self.is_grounded = True 
                            elif self.vy < 0:
                                self.y = tile_rect[1] + TILE_SIZE 
                            self.vy = 0.0 
                            
                        player_rect = self.get_coll_rect()
                        px, py, pw, ph = player_rect


    def check_enemy_collision(self, enemies):
        """Checks player body vs enemies (stomp or lethal).
        Returns (hit_type, enemy_index) or (None, -1).
        """
        player_rect = self.get_coll_rect()
        px, py, pw, ph = player_rect
        
        for i, enemy in enumerate(enemies):
            enemy_rect = enemy.get_hitbox_rect()
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
            if check_collision_recs(melee_rect, enemy.get_hitbox_rect()):
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
                if check_collision_recs(proj_rect, enemy.get_hitbox_rect()):
                    hits.append((pi, ei))
                    proj.alive = False
                    break   # one enemy per projectile
        return hits

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
        self.breath = self.breath_max   

    def draw(self):
        """Draws projectiles, the player sprite, and (optionally) debug rects."""

        # --- Projectiles (draw behind player) ---
        for p in self.projectiles:
            p.draw()

        # --- Player sprite ---
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
            self.frame.width * self.facing,
            self.frame.height
        )
        if self.invincible:
            draw_texture_pro(self.texture, src_frame, dest_rect, origin, 0, PINK)
        else:
            draw_texture_pro(self.texture, src_frame, dest_rect, origin, 0, WHITE)


        # --- Melee hitbox flash ---
        if self.is_attacking:
            melee_rect = self.get_melee_rect()
            whirl_src = self.whirlwind_frame
            whirl_src.height += WHIRLWIND_OFFSET
            draw_texture_pro(self.whirlwind_tex, whirl_src, melee_rect, Vector2(0, 0), 0, WHITE)

        # ── Debug collision outline 
        # draw_rectangle_lines_ex(self.get_coll_rect(), 1.0, WHITE)

    def draw_hud(self):
        """Draws the breath meter in the top-right corner of the screen."""
        bar_width      = 160          # total bar width  (px)
        bar_height      = 18           # bar height       (px)
        bar_margin = 12           # gap from screen edge
        bar_x      = WINDOW_WIDTH - bar_width - bar_margin
        bar_y      = bar_margin

        fill_ratio = self.breath / self.breath_max
        fill_w     = int(bar_width * fill_ratio)

        # ── Color shift: full=white, empty=black ───────────────────
        v = int(255 * fill_ratio)
        fill_color = Color(v, v, v, 220)    

        draw_rectangle(bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4,
                       Color(0, 0, 0, 160))

        if fill_w > 0:
            draw_rectangle(bar_x, bar_y, fill_w, bar_height, fill_color)

            draw_rectangle(bar_x, bar_y, fill_w, bar_height // 4,
                           Color(255, 255, 255, 40))

        if fill_w < bar_width:
            draw_rectangle(bar_x + fill_w, bar_y, bar_width - fill_w, bar_height,
                           Color(30, 30, 40, 180))

        draw_rectangle_lines(bar_x, bar_y, bar_width, bar_height,
                             Color(180, 220, 255, 200))

        label = "BREATH"
        label_x = bar_x - measure_text(label, 10) - 6
        draw_text(label, label_x, bar_y + 4, 10, Color(180, 220, 255, 200))

        for i in (1, 2, 3):
            pip_x = bar_x + int(bar_width * i / 4)
            draw_rectangle(pip_x, bar_y, 1, bar_height, Color(0, 0, 0, 100))