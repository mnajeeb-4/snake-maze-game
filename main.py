import os
# Force Pygame to run without a physical display window (Headless mode for Streamlit)
os.environ["SDL_VIDEODRIVER"] = "dummy"

import streamlit as st
import pygame
from PIL import Image
import random
import time

# --- INITIALIZATION ---
st.set_page_config(page_title="2D Snake Maze Game", page_icon="🐍", layout="centered")
pygame.init()

# --- ALGORITHM: RECURSIVE BACKTRACKING MAZE GENERATION ---
def generate_maze(width, height):
    # Create grid full of walls (1 = wall, 0 = path)
    maze = [[1 for _ in range(width)] for _ in range(height)]
    
    def carve_passages_from(cx, cy):
        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 1 <= ny < height - 1 and 1 <= nx < width - 1 and maze[ny][nx] == 1:
                maze[ny - dy//2][nx - dx//2] = 0
                maze[ny][nx] = 0
                carve_passages_from(nx, ny)
                
    maze[1][1] = 0
    carve_passages_from(1, 1)
    # Ensure goal area is open
    maze[height-2][width-2] = 0 
    maze[height-3][width-2] = 0 
    maze[height-2][width-3] = 0 
    return maze

# --- SESSION STATE MANAGEMENT (Saves game data between button clicks) ---
if "level" not in st.session_state:
    st.session_state.level = 1
    st.session_state.max_levels = 100
    st.session_state.start_time = time.time()
    st.session_state.maze_size = 11
    st.session_state.maze = generate_maze(11, 11)
    st.session_state.snake_pos = [1, 1]
    st.session_state.vibrate_alert = False

goal_pos = [st.session_state.maze_size - 2, st.session_state.maze_size - 2]

# --- GAME LOGIC: MOVEMENT & COLLISION ---
def move_snake(dx, dy):
    st.session_state.vibrate_alert = False
    new_x = st.session_state.snake_pos[0] + dx
    new_y = st.session_state.snake_pos[1] + dy

    # Check wall collision
    if st.session_state.maze[new_y][new_x] == 1:
        # Vibrate/Restart Logic
        st.session_state.vibrate_alert = True
        st.session_state.snake_pos = [1, 1] # Restart Level Position
    else:
        st.session_state.snake_pos = [new_x, new_y]
        
    # Check Goal reached
    if st.session_state.snake_pos == goal_pos:
        if st.session_state.level < st.session_state.max_levels:
            st.session_state.level += 1
            # Increase difficulty by increasing maze size
            new_size = min(31, 11 + (st.session_state.level // 5) * 2) 
            st.session_state.maze_size = new_size
            st.session_state.maze = generate_maze(new_size, new_size)
            st.session_state.snake_pos = [1, 1]
        else:
            st.session_state.level = "WIN"

# --- PYGAME RENDERING (Integrating Pygame in Streamlit) ---
def render_game_image():
    cell_size = 20
    size = st.session_state.maze_size
    surface = pygame.Surface((size * cell_size, size * cell_size))
    surface.fill((30, 30, 30)) # Dark background

    # Draw Maze Walls
    for y in range(size):
        for x in range(size):
            if st.session_state.maze[y][x] == 1:
                pygame.draw.rect(surface, (100, 100, 100), (x*cell_size, y*cell_size, cell_size, cell_size))

    # Draw Goal (Red)
    pygame.draw.rect(surface, (255, 50, 50), (goal_pos[0]*cell_size, goal_pos[1]*cell_size, cell_size, cell_size))

    # Draw Snake Character (Green)
    sx, sy = st.session_state.snake_pos
    pygame.draw.rect(surface, (50, 205, 50), (sx*cell_size, sy*cell_size, cell_size, cell_size))
    # Snake Eyes
    pygame.draw.rect(surface, (255, 255, 255), (sx*cell_size + 4, sy*cell_size + 4, 4, 4))
    pygame.draw.rect(surface, (255, 255, 255), (sx*cell_size + 12, sy*cell_size + 4, 4, 4))

    # Convert Pygame Surface to PIL Image for Streamlit
    image_str = pygame.image.tostring(surface, "RGB")
    return Image.frombytes("RGB", (size * cell_size, size * cell_size), image_str)

# --- UI DISPLAY ---
st.title("🐍 2D Snake Maze Game")

if st.session_state.level == "WIN":
    total_time = int(time.time() - st.session_state.start_time)
    st.success(f"🎉 Congratulations! You completed all 100 levels in {total_time} seconds!")
    if st.button("Play Again"):
        st.session_state.clear()
        st.rerun()
else:
    # Display Stats
    col1, col2 = st.columns(2)
    col1.markdown(f"### Level: {st.session_state.level}/100")
    elapsed = int(time.time() - st.session_state.start_time)
    col2.markdown(f"### Time: {elapsed}s")

    # Vibrate/Collision Alert
    if st.session_state.vibrate_alert:
        st.toast("📳 VIBRATE: You hit a wall! Level Restarted.", icon="💥")
        st.error("💥 Wall Hit! Back to start!")

    # Show Pygame Rendered Maze
    game_image = render_game_image()
    st.image(game_image, use_column_width=False)

    # Controls (On-Screen Buttons)
    st.markdown("### Controls")
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("⬆️ UP", use_container_width=True): move_snake(0, -1)
    
    c4, c5, c6 = st.columns([1, 1, 1])
    with c4:
        if st.button("⬅️ LEFT", use_container_width=True): move_snake(-1, 0)
    with c5:
        if st.button("⬇️ DOWN", use_container_width=True): move_snake(0, 1)
    with c6:
        if st.button("➡️ RIGHT", use_container_width=True): move_snake(1, 0)
