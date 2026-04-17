import random
import math
import os
from pyray import *
from Utilities import *
from settings import *
from player import *
from enemy import *


# --- Main Game Logic ---
def main():
    # --- Initialization ---
    init_window(WINDOW_WIDTH, WINDOW_HEIGHT, "Raylib 2D Platformer Clone (Stomp Mechanic)".encode('utf-8'))
    set_target_fps(60)

    # Prepare Level Data: Separate collision map from dynamic entities
    game_level, collectibles, enemies = Utilities.parse_level(LEVEL)
    
    # Game State Variables
    # Player starts at TILE_SIZE * 2, TILE_SIZE * 2
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


    # --- Game Loop ---
    while not window_should_close():
        delta_time = get_frame_time()
        
        # --- Update ---
        if game_state == "PLAYING":
            player.update(delta_time, game_level)
            
            # Update Enemies
            for enemy in enemies:
                enemy.update(delta_time, game_level)

            Utilities.update_cam(camera, player, forest.width, forest.height, WINDOW_WIDTH, WINDOW_HEIGHT)

            # Check for coin collection
            collected_indices = player.check_collection(collectibles)
            if collected_indices:
                for index in sorted(collected_indices, reverse=True):
                    collectibles.pop(index)
                    score += 10
            
            # Check for enemy collision (Stomp/Death/Reset)
            hit_type, enemy_index = player.check_enemy_collision(enemies)

            if hit_type == "STOMP":
                # Stomp mechanic: Remove enemy, score, and bounce
                enemies.pop(enemy_index)
                score += 100 
                player.vy = STOMP_BOUNCE # Player bounces up
                
            elif hit_type == "LETHAL":
                # Death/Reset mechanic: Penalty and restart
                player.reset()
                score -= 50 
                if score < 0: score = 0
            
        # --- Draw ---
        begin_drawing()
        clear_background(SKYBLUE) 
        
        # Start the 2D camera mode
        begin_mode_2d(camera)
        
        # --- Draw the background ---
        draw_texture(
            forest,
            0,
            0,
            WHITE
        )

        Utilities.draw_level(game_level)

        # 2. Draw Collectibles
        Utilities.draw_coins(collectibles)
            
        # 3. Draw Enemies
        for enemy in enemies:
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
