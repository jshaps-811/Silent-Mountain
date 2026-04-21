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

     # --- Level map ---
    base_dir = os.path.dirname(__file__)
    LEVEL = Utilities.load_level(os.path.join(base_dir, "assets", "forest_level_map.csv"))
    TILE_ROWS = len(LEVEL)
    TILE_COLS = len(LEVEL[0])

    # --- World Dimensions ---
    WORLD_WIDTH = TILE_COLS * TILE_SIZE
    WORLD_HEIGHT = TILE_ROWS * TILE_SIZE
    Y_OFFSET = 200

    # Prepare Level Data: Separate collision map from dynamic entities
    game_level, collectibles, enemies = Utilities.parse_level(LEVEL, TILE_ROWS, TILE_COLS)
    
    # Game State Variables
    player = Player(TILE_SIZE * 2, TILE_SIZE * 2) 
    score = 0
    game_state = "PLAYING" 
    
    # --- Camera Initialization ---
    camera = Camera2D()
    camera.target = Vector2(player.x, player.y) 
    camera.offset = Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2) 
    camera.rotation = 0.0
    camera.zoom = 1.0

    # --- Background Texure Initialization ---
    base_dir = os.path.dirname(__file__)
    forest = load_texture(os.path.join(base_dir, "assets", "forest.png"))

    player.startup()


    # --- Game Loop ---
    while not window_should_close():
        delta_time = get_frame_time()
        
        # --- Update ---
        if game_state == "PLAYING":
            player.update(delta_time, game_level, TILE_ROWS, TILE_COLS, WORLD_WIDTH)

            # Update Enemies
            for enemy in enemies:
                enemy.update(delta_time, game_level, TILE_ROWS, TILE_COLS, WORLD_WIDTH, player)
                for proj in enemy.projectiles:
                    proj.update(delta_time)
                    # Check collision with player
                    if check_collision_circle_rec((proj.x, proj.y), proj.radius, player.get_rect()):
                        # Player hit by projectile: Reset player and apply penalty
                        player.reset()

            Utilities.update_cam(camera, player, forest.width, forest.height, WINDOW_WIDTH, WINDOW_HEIGHT)

            # Check for coin collection
            collected_indices = player.check_collection(collectibles)
            if collected_indices:
                for index in sorted(collected_indices, reverse=True):
                    collectibles.pop(index)
                    score += 10

            # Check for enemy collision (Stomp/Death/Reset)
            # hit_type, enemy_index = player.check_enemy_collision(enemies)

            # if hit_type == "STOMP":
            #     # Stomp mechanic: Remove enemy, score, and bounce
            #     enemies.pop(enemy_index)
            #     score += 100
            #     player.vy = STOMP_BOUNCE  # Player bounces up

            # elif hit_type == "LETHAL":
            #     # Death/Reset mechanic: Penalty and restart
            #     player.reset()
            #     score -= 50
            #     if score < 0: score = 0

            # Check for melee hits
            if player.is_attacking:
                melee_hits = player.check_melee_hit(enemies)
                for index in sorted(melee_hits, reverse=True):
                    enemies.pop(index)
                    score += 75

            # Check for projectile hits
            projectile_hits = player.check_projectile_hits(enemies)
            # De-duplicate enemy indices in case two projectiles hit the same enemy
            hit_enemy_indices = sorted(
                set(ei for _, ei in projectile_hits), reverse=True
            )
            for index in hit_enemy_indices:
                enemies.pop(index)
                score += 50
            
        # --- Draw ---
        begin_drawing()
        clear_background(SKYBLUE) 
        
        # Start the 2D camera mode
        begin_mode_2d(camera)
        
        # --- Draw the background ---
        # draw_texture(
        #     forest,
        #     0,
        #     0,
        #     WHITE
        # )

        Utilities.draw_level(game_level, TILE_ROWS, TILE_COLS)

        # 2. Draw Collectibles
        Utilities.draw_coins(collectibles)
            
        # 3. Draw Enemies
        for enemy in enemies:
            # print(type(enemy))
            enemy.draw()

        # 4. Draw Player 
        player.draw()
        
        # End the 2D camera mode
        end_mode_2d()
        
        # 5. Draw HUD (Drawn on screen, outside of BeginMode2D)
        score_text = f"Score: {score}".encode('utf-8')
        draw_text(score_text, WINDOW_WIDTH - measure_text(score_text, 20) - 10, 10, 20, BLACK)
        
        debug_text = f"Grounded: {player.is_grounded} | Enemies: {len(enemies)}".encode('utf-8')
        draw_text(debug_text, 10, 10, 20, BLACK) 


        end_drawing()

    # --- De-Initialization ---
    close_window()

if __name__ == "__main__":
    main()
