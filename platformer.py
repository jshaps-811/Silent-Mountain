import random
import math
import os
from pyray import *
from settings import *
from enemy import *
import Utilities
from ghost import *
from yatagarasu import *
from oni import *
from player import *


# --- Main Game Logic ---
def main():
    # --- Initialization ---
    init_window(WINDOW_WIDTH, WINDOW_HEIGHT, "Silent-Mountain : Cleanse the Mountain of Monsters!".encode('utf-8'))
    set_target_fps(60)
    base_dir = os.path.dirname(__file__)

    init_audio_device()
    bg_music = load_music_stream(os.path.join(base_dir, "assets/audio/bg_music.wav"))
    play_music_stream(bg_music)

     # --- Level map ---
    LEVEL1 = Utilities.load_level(os.path.join(base_dir, "assets", "levelmaps", "forest_level_map.csv"))
    LEVEL2 = Utilities.load_level(os.path.join(base_dir, "assets", "levelmaps", "cave_level_map.csv"))
    LEVEL3 = Utilities.load_level(os.path.join(base_dir, "assets", "levelmaps", "peak_level_map.csv"))
    TILE_ROWS = len(LEVEL1)
    TILE_COLS = len(LEVEL1[0])

    # --- World Dimensions ---
    WORLD_WIDTH = TILE_COLS * TILE_SIZE
    WORLD_HEIGHT = TILE_ROWS * TILE_SIZE
    Y_OFFSET = 200

    # Prepare Level Data: Separate collision map from dynamic entities
    cur_game_level1, cur_collectibles1, cur_enemies1 = Utilities.parse_level(LEVEL1, TILE_ROWS, TILE_COLS)
    cur_game_level2, cur_collectibles2, cur_enemies2 = Utilities.parse_level(LEVEL2, TILE_ROWS, TILE_COLS)
    cur_game_level3, cur_collectibles3, cur_enemies3 = Utilities.parse_level(LEVEL3, TILE_ROWS, TILE_COLS)

    original_enemies1 = cur_enemies1.copy()
    original_enemies2 = cur_enemies2.copy()
    original_enemies3 = cur_enemies3.copy()

    cur_game_level = cur_game_level1
    cur_collectibles = cur_collectibles1
    cur_enemies = cur_enemies1

    # Game State Variables
    player = Player(TILE_SIZE * 2, WORLD_HEIGHT // 2 + Y_OFFSET) 
    score = 0
    game_state = "SPLASH" 
    
    # --- Camera Initialization ---
    camera = Camera2D()
    camera.target = Vector2(player.x, player.y) 
    camera.offset = Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2) 
    camera.rotation = 0.0
    camera.zoom = 1.0

    # --- Texture Initialization ---
    base_dir = os.path.dirname(__file__)
    splash = load_texture(os.path.join(base_dir, "assets", "splash-1.png"))
    game_over_splash = load_texture(os.path.join(base_dir, "assets", "game-over.png"))
    victory_splash = load_texture(os.path.join(base_dir, "assets", "victory.png"))
    forest = load_texture(os.path.join(base_dir, "assets", "forest.png"))
    cave = load_texture(os.path.join(base_dir, "assets", "cave.png"))
    peak = load_texture(os.path.join(base_dir, "assets", "peak.png"))
    heart = load_texture(os.path.join(base_dir, "assets", "heart.png"))
    top_grass = load_texture(os.path.join(base_dir, "assets", "Tiles", "Tile_02.png"))
    bottom_grass = load_texture(os.path.join(base_dir, "assets", "Tiles", "Tile_66.png"))
    ledge_grass = load_texture(os.path.join(base_dir, "assets", "Tiles", "Tile_50.png"))
    ledge_left = load_texture(os.path.join(base_dir, "assets", "Tiles", "Tile_49.png"))
    ledge_right = load_texture(os.path.join(base_dir, "assets", "Tiles", "Tile_51.png"))
    grass_left = load_texture(os.path.join(base_dir, "assets", "Tiles", "Tile_01.png"))
    grass_right = load_texture(os.path.join(base_dir, "assets", "Tiles", "Tile_03.png"))
    rocks_middle = load_texture(os.path.join(base_dir, "assets", "Tiles", "Tile_02.png"))
    rocky_ledge_left = load_texture(os.path.join(base_dir, "assets", "Tiles", "Tile_44.png"))
    rocky_ledge_mid = load_texture(os.path.join(base_dir, "assets", "Tiles", "Tile_45.png"))
    rocky_ledge_right = load_texture(os.path.join(base_dir, "assets", "Tiles", "Tile_46.png"))

    tiles = {TILE_TOP_GRASS: top_grass, 
             TILE_BOTTOM_GRASS: bottom_grass, 
             TILE_LEDGE_GRASS: ledge_grass, 
             LEDGE_LEFT: ledge_left, 
             LEDGE_RIGHT: ledge_right, 
             GRASS_LEFT: grass_left, 
             GRASS_RIGHT: grass_right, 
             ROCKS_MIDDLE: rocks_middle, 
             ROCKY_LEDGE_LEFT: rocky_ledge_left, 
             ROCKY_LEDGE_MID: rocky_ledge_mid, 
             ROCKY_LEDGE_RIGHT: rocky_ledge_right,
        }

    player.startup()


    # --- Game Loop ---
    while not window_should_close():
        update_music_stream(bg_music)
        delta_time = get_frame_time()

        # print("PLAYER LEVEL:", player.level)
        if player.level == 2:
            cur_game_level = cur_game_level2
            cur_collectibles = cur_collectibles2
            cur_enemies = cur_enemies2

        if player.level == 3:
            cur_game_level = cur_game_level3
            cur_collectibles = cur_collectibles3
            cur_enemies = cur_enemies3

        if game_state == "SPLASH":
            draw_texture_pro(
                splash,
                Rectangle(0, 0, splash.width, splash.height),   
                Rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),  
                Vector2(0, 0),
                0.0,
                WHITE
            )
            if is_key_pressed(KeyboardKey.KEY_ENTER):
                game_state = "PLAYING"

        # --- Update ---
        elif game_state == "PLAYING":
            player.update(delta_time, cur_game_level, TILE_ROWS, TILE_COLS, WORLD_WIDTH)
            if player.health <= 0:
                game_state = "GAME_OVER"

            # Update cur_enemies
            for enemy in cur_enemies:
                enemy.update(delta_time, cur_game_level, TILE_ROWS, TILE_COLS, WORLD_WIDTH, player)
                if type(enemy) == Ghost:
                    for proj in enemy.projectiles:
                        proj.update(delta_time)
                        # Check collision with player
                        if check_collision_circle_rec((proj.x, proj.y), proj.radius, player.get_rect()):
                            player.apply_damage(GHOST_DAMAGE)
                            enemy.projectiles.remove(proj)  # Remove projectile on hit
                elif type(enemy) == Yatagarasu:
                    if check_collision_recs(enemy.get_hitbox_rect(), player.get_rect()) or enemy.check_melee_hit(player):
                        if not player.invincible:
                            play_sound(enemy.attack_sound)
                            player.apply_damage(YATAGARASU_DAMAGE)
                            knockback_direction = 1 if player.x > enemy.x else -1
                            player.knockback_vy = -Y_KNOCKBACK                        # upward pop
                            player.is_grounded = False                        # ensure player is airborne for knockback
                            player.knockback_vx = knockback_direction * X_KNOCKBACK   # horizontal push
                elif type(enemy) == Oni:
                    if check_collision_recs(enemy.get_hitbox_rect(), player.get_rect()):
                        if not player.invincible:
                            player.apply_damage(ONI_PASSIVE_DAMAGE)
                            # Knock the player away from the Oni
                            knockback_direction = 1 if player.x > enemy.x else -1
                            player.knockback_vy = -Y_KNOCKBACK                        # upward pop
                            player.is_grounded = False                        # ensure player is airborne for knockback
                            player.knockback_vx = knockback_direction * X_KNOCKBACK   # horizontal push

            Utilities.update_cam(camera, player, WORLD_WIDTH, WORLD_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT)
                    

           # Check for melee hits
            if player.is_attacking:
                melee_hits = player.check_melee_hit(cur_enemies)
                for index in sorted(melee_hits, reverse=True):
                    if type(cur_enemies[index]) == Oni and cur_enemies[index].health > 0:
                        if not cur_enemies[index].invincible:
                            cur_enemies[index].health -= 10
                        cur_enemies[index].invincible = True
                        cur_enemies[index].i_frames = ONI_IFRAMES
                    else:
                        cur_enemies.pop(index)

            # Check for projectile hits
            projectile_hits = player.check_projectile_hits(cur_enemies)
            # De-duplicate enemy indices in case two projectiles hit the same enemy
            hit_enemy_indices = sorted(
                set(ei for _, ei in projectile_hits), reverse=True
            )
            for index in hit_enemy_indices:
                if type(cur_enemies[index]) == Oni and cur_enemies[index].health > 0:
                    if not cur_enemies[index].invincible:
                        cur_enemies[index].health -= 2
                    cur_enemies[index].invincible = True
                    cur_enemies[index].i_frames = ONI_IFRAMES
                else:
                    cur_enemies.pop(index)

            if len(cur_enemies) == 0:
                player.all_enemies_defeated = True
            else:
                player.all_enemies_defeated = False

        # --- Draw ---
        begin_drawing()
        clear_background(SKYBLUE) 

        if game_state == "PLAYING" or game_state == "PAUSED":
            # Start the 2D camera mode
            begin_mode_2d(camera)
            
            # --- Draw the background ---
            if player.level == 1:
                bg_y = WORLD_HEIGHT - forest.height 
                for x in range(0, WORLD_WIDTH, forest.width):
                    draw_texture(forest, x, bg_y, WHITE)

            elif player.level == 2:
                bg_y = WORLD_HEIGHT - cave.height - 160
                for x in range(0, WORLD_WIDTH, cave.width):
                    draw_texture(cave, x, bg_y, WHITE)

            elif player.level == 3:
                bg_y = WORLD_HEIGHT - peak.height
                for x in range(0, WORLD_WIDTH, peak.width):
                    draw_texture(peak, x, bg_y, WHITE)
            
            elif player.level == 4:
                game_state = "VICTORY"

            Utilities.draw_level(cur_game_level, TILE_ROWS, TILE_COLS, tiles)

                
            # Draw cur_enemies
            for enemy in cur_enemies:
                # print(type(enemy))
                enemy.draw()

            # Draw Player 
            player.draw()
            
            # End the 2D camera mode
            end_mode_2d()
            
            # Draw HUD (Drawn on screen, outside of BeginMode2D)
            score_text = f"Score: {score}".encode('utf-8')
            draw_text(score_text, WINDOW_WIDTH - measure_text(score_text, 20) - 10, 10, 20, BLACK)
            
            enemy_text = f"Enemies Remaining: {len(cur_enemies)}".encode('utf-8')
            draw_text(enemy_text, 10, 10, 20, WHITE)

            move_instruction_text = f"Instructions: Use arrow keys to move and space to jump".encode('utf-8')
            draw_text(move_instruction_text, 10, 40, 10, WHITE)
            attack_instruction_text = f"Instructions: Use Z and X to attack".encode('utf-8')
            draw_text(attack_instruction_text, 10, 50, 10, WHITE)
            goal_text = f"Goal: Cleanse the mountain of monsters!".encode('utf-8')
            draw_text(goal_text, 10, 60, 10, WHITE)

            for i in range(BASE_HEALTH):
                height_x = WINDOW_WIDTH - 190 + i * 27
                height_y = 40
                if i < player.health:
                    draw_texture_ex(heart, Vector2(height_x, height_y), 0.0, 0.1, WHITE)
                else:
                    draw_texture_ex(heart, Vector2(height_x, height_y), 0.0, 0.1, DARKGRAY)

            player.draw_hud()

        elif game_state == "GAME_OVER":
            draw_texture_pro(
                game_over_splash,
                Rectangle(0, 0, game_over_splash.width, game_over_splash.height),   
                Rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),  
                Vector2(0, 0),
                0.0,
                WHITE
            )
            if is_key_pressed(KeyboardKey.KEY_ENTER):
                game_state = "SPLASH"
                player.health = BASE_HEALTH
                player.reset()
                player.level = 1
                cur_game_level = cur_game_level1
                cur_enemies = original_enemies1.copy()
                cur_enemies2 = original_enemies2.copy()
                cur_enemies3 = original_enemies3.copy()

        elif game_state == "VICTORY":
            draw_texture_pro(
                victory_splash,
                Rectangle(0, 0, victory_splash.width, victory_splash.height),
                Rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),
                Vector2(0, 0),
                0.0,
                WHITE
            )
            if is_key_pressed(KeyboardKey.KEY_ENTER):
                game_state = "SPLASH"
                player.health = BASE_HEALTH
                player.reset()
                player.level = 1
                cur_game_level = cur_game_level1
                cur_enemies = original_enemies1.copy()
                cur_enemies2 = original_enemies2.copy()
                cur_enemies3 = original_enemies3.copy()


        end_drawing()

    # --- De-Initialization ---
    unload_texture(player.texture)
    unload_texture(player.whirlwind_tex)
    unload_texture(game_over_splash)
    unload_texture(victory_splash)
    unload_sound(player.proj_sound_short)
    unload_sound(player.proj_sound_long)
    unload_sound(player.damage_tick)
    for val in tiles.values():
        unload_texture(val)
    close_window()

if __name__ == "__main__":
    main()
