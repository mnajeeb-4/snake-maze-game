import pygame
import random
import time
import sys

# --- Constants & Configuration ---
TILE_SIZE = 40
FPS = 15 # Snake speed
WIDTH, HEIGHT = 800, 600

# Colors
BG_COLOR = (20, 20, 30)
WALL_COLOR = (50, 150, 200)
SNAKE_COLOR = (50, 200, 50)
GOAL_COLOR = (220, 50, 50)
TEXT_COLOR = (255, 255, 255)

# --- Pygame Initialization ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("100-Level Snake Maze Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

# --- Maze Generation (Recursive Backtracking) ---
def generate_maze(cols, rows):
    """Generates a random maze using Recursive Backtracking algorithm."""
    # Create grid full of walls (1 = wall, 0 = path)
    maze = [[1 for _ in range(cols)] for _ in range(rows)]
    
    def carve_passages(cx, cy):
        directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 1 <= ny < rows-1 and 1 <= nx < cols-1 and maze[ny][nx] == 1:
                maze[cy + dy//2][cx + dx//2] = 0 # Carve through wall
                maze[ny][nx] = 0 # Carve cell
                carve_passages(nx, ny)
                
    maze[1][1] = 0 # Start point
    carve_passages(1, 1)
    
    # Ensure Goal is reachable at the bottom right
    maze[rows-2][cols-2] = 0 
    maze[rows-3][cols-2] = 0 
    maze[rows-2][cols-3] = 0 
    
    return maze

# --- Screen Shake Effect (Alternative to Vibration) ---
def screen_shake():
    """Shakes the screen slightly when the snake hits a wall."""
    shake_offsets = [(5, 5), (-5, -5), (5, -5), (-5, 5), (0, 0)]
    for offset in shake_offsets:
        screen.fill(BG_COLOR)
        # Briefly shift the display surface
        display_surface = pygame.display.get_surface()
        display_surface.blit(display_surface, offset)
        pygame.display.flip()
        pygame.time.wait(30)

# --- Main Game Function ---
def main():
    level = 1
    max_levels = 100
    
    while level <= max_levels:
        # Dynamic grid size based on level (gets harder)
        cols = min(15 + (level // 5) * 2, 35) 
        rows = min(11 + (level // 5) * 2, 25)
        
        # Center the maze on screen
        offset_x = (WIDTH - (cols * TILE_SIZE)) // 2
        offset_y = (HEIGHT - (rows * TILE_SIZE)) // 2 + 30
        
        maze = generate_maze(cols, rows)
        
        # Player attributes
        snake_pos = [1, 1] # [x, y] in grid coordinates
        start_time = time.time()
        goal_pos = [cols-2, rows-2]
        
        level_running = True
        while level_running:
            screen.fill(BG_COLOR)
            elapsed_time = int(time.time() - start_time)
            
            # --- Event Handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Movement Controls
                if event.type == pygame.KEYDOWN:
                    new_x, new_y = snake_pos[0], snake_pos[1]
                    if event.key == pygame.K_UP: new_y -= 1
                    elif event.key == pygame.K_DOWN: new_y += 1
                    elif event.key == pygame.K_LEFT: new_x -= 1
                    elif event.key == pygame.K_RIGHT: new_x += 1
                    
                    # Collision Detection
                    if maze[new_y][new_x] == 1:
                        # Hit a wall! Shake and reset position/time
                        screen_shake()
                        snake_pos = [1, 1]
                        start_time = time.time() # Reset timer for the level
                    else:
                        snake_pos = [new_x, new_y] # Move snake
            
            # --- Win Condition ---
            if snake_pos == goal_pos:
                level += 1
                level_running = False # Break out to start next level
            
            # --- Drawing the Maze ---
            for y in range(rows):
                for x in range(cols):
                    rect = pygame.Rect(offset_x + x * TILE_SIZE, offset_y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if maze[y][x] == 1:
                        pygame.draw.rect(screen, WALL_COLOR, rect)
                    
            # Draw Goal
            goal_rect = pygame.Rect(offset_x + goal_pos[0] * TILE_SIZE, offset_y + goal_pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, GOAL_COLOR, goal_rect)
            
            # Draw Snake
            snake_rect = pygame.Rect(offset_x + snake_pos[0] * TILE_SIZE, offset_y + snake_pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, SNAKE_COLOR, snake_rect)
            
            # Draw UI (Level and Timer)
            ui_text = font.render(f"Level: {level}/{max_levels}   |   Time: {elapsed_time}s", True, TEXT_COLOR)
            screen.blit(ui_text, (20, 20))
            
            pygame.display.flip()
            clock.tick(FPS)
            
    # --- Game Over / Won Screen ---
    screen.fill(BG_COLOR)
    win_text = font.render("Congratulations! You completed all 100 levels!", True, TEXT_COLOR)
    screen.blit(win_text, (WIDTH//2 - 200, HEIGHT//2))
    pygame.display.flip()
    pygame.time.wait(5000)
    pygame.quit()

if __name__ == "__main__":
    main()
