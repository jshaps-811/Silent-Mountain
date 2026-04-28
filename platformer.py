import random
import math
import os
from pyray import *
from settings import *
from enemy import *
from ghost import *
import Utilities
from player import *


# --- Main Game Logic ---
def main():
    # --- Initialization ---
    init_window(WINDOW_WIDTH, WINDOW_HEIGHT, "Raylib 2D Platformer Clone (Stomp Mechanic)".encode('utf-8'))
    set_target_fps(60)
    base_dir = os.path.dirname(__file__)

    init_audio_device()
    bg_music = load_music_stream(os.path.join(base_dir, "assets/audio/bg_music.wav"))
    play_music_stream(bg_music)

     # --- Level map ---
    LEVEL1 = Utilities.load_level(os.path.join(base_dir, "assets", "cave_level_map.csv"))
    LEVEL2 = Utilities.load_level(os.path.join(base_dir, "assets", "cave_level_map.csv"))
    TILE_ROWS = len(LEVEL1)
    TILE_COLS = len(LEVEL1[0])

    # --- World Dimensions ---
    WORLD_WIDTH = TILE_COLS * TILE_SIZE
    WORLD_HEIGHT = TILE_ROWS * TILE_SIZE
    Y_OFFSET = 200

    # Prepare Level Data: Separate collision map from dynamic entities
    cur_game_level1, cur_collectibles1, cur_enemies1 = Utilities.parse_level(LEVEL1, TILE_ROWS, TILE_COLS)
    cur_game_level2, cur_collectibles2, cur_enemies2 = Utilities.parse_level(LEVEL2, TILE_ROWS, TILE_COLS)


    cur_game_level = cur_game_level1
    cur_collectibles = cur_collectibles1
    cur_enemies = cur_enemies1

    # Game State Variables
    player = Player(TILE_SIZE * 2, WORLD_HEIGHT // 2) 
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
    forest = load_texture(os.path.join(base_dir, "assets", "forest.png"))
    top_grass = load_texture(os.path.join(base_dir, "assets", "Tiles", "Tile_01.png"))
    bottom_grass = load_texture(os.path.join(base_dir, "assets", "Tiles", "Tile_24.png"))
    tiles = [top_grass, bottom_grass]

    player.startup()


    # --- Game Loop ---
    while not window_should_close():
        update_music_stream(bg_music)
        delta_time = get_frame_time()

        if player.level == 2:
            cur_game_level = cur_game_level2
            cur_collectibles = cur_collectibles2
            cur_enemies = cur_enemies2

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
                            player.health -= 10
                            enemy.projectiles.remove(proj)  # Remove projectile on hit

            Utilities.update_cam(camera, player, WORLD_WIDTH, WORLD_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT)

            # Check for coin collection
            collected_indices = player.check_collection(cur_collectibles)
            if collected_indices:
                for index in sorted(collected_indices, reverse=True):
                    cur_collectibles.pop(index)
                    

           # Check for melee hits
            if player.is_attacking:
                melee_hits = player.check_melee_hit(cur_enemies)
                for index in sorted(melee_hits, reverse=True):
                    cur_enemies.pop(index)
                    

            # Check for projectile hits
            projectile_hits = player.check_projectile_hits(cur_enemies)
            # De-duplicate enemy indices in case two projectiles hit the same enemy
            hit_enemy_indices = sorted(
                set(ei for _, ei in projectile_hits), reverse=True
            )
            for index in hit_enemy_indices:
                cur_enemies.pop(index)
                
            
        # --- Draw ---
        begin_drawing()
        clear_background(SKYBLUE) 

        if game_state == "PLAYING":
            # Start the 2D camera mode
            begin_mode_2d(camera)
            
            # --- Draw the background ---
            # draw_texture(
            #     forest,
            #     0,
            #     0,
            #     WHITE
            # )

            Utilities.draw_level(cur_game_level, TILE_ROWS, TILE_COLS, tiles)

            # # Draw cur_collectibles
            Utilities.draw_coins(cur_collectibles)
                
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
            
            debug_text = f"Grounded: {player.is_grounded} | cur_enemies: {len(cur_enemies)}".encode('utf-8')
            draw_text(debug_text, 10, 10, 20, BLACK) 

            player_health = f"Health: {player.health}".encode('utf-8')
            draw_text(player_health, 10, 30, 20, BLACK)

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

        end_drawing()

    # --- De-Initialization ---
    unload_music_stream(bg_music)
    close_window()

if __name__ == "__main__":
    main()
