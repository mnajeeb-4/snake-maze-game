import streamlit as st
import pygame
import random
import time
from PIL import Image

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="2D Maze Game", layout="centered")
st.title("🐍 2D Snake Maze Game")
st.write("Developed according to the internship task requirements.")

# --- Game Constants ---
TILE_SIZE = 30
FPS = 30
WIDTH, HEIGHT = 600, 450

# Colors
BG_COLOR = (20, 20, 30)
WALL_COLOR = (50, 150, 200)      # Obstacles / Walls [cite: 17]
SNAKE_COLOR = (50, 200, 50)     # Player Character [cite: 15]
GOAL_COLOR = (220, 50, 50)      # Goal [cite: 18]

# --- Initialize Pygame in Headless Mode (For Cloud/Web Compatibility) ---
import os
os.environ["SDL_VIDEODRIVER"] = "dummy" 
pygame.init()
pygame.font.init()
font = pygame.font.SysFont("Arial", 20)

# --- Session State for Level & Progress ---
if 'level' not in st.session_state:
    st.session_state.level = 1
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()
if 'snake_pos' not in st.session_state:
    st.session_state.snake_pos = [1, 1]
if 'shake_frames' not in st.session_state:
    st.session_state.shake_frames = 0

# --- Random Maze Generation Algorithm (Recursive Backtracking) [cite: 14, 28] ---
if 'maze' not in st.session_state or 'current_level' not in st.session_state or st.session_state.current_level != st.session_state.level:
    cols = min(11 + (st.session_state.level // 5) * 2, 19)
    rows = min(9 + (st.session_state.level // 5) * 2, 13)
    
    maze = [[1 for _ in range(cols)] for _ in range(rows)]
    
    def carve_passages(cx, cy):
        directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 1 <= ny < rows-1 and 1 <= nx < cols-1 and maze[ny][nx] == 1:
                maze[cy + dy//2][cx + dx//2] = 0
                maze[ny][nx] = 0
                carve_passages(nx, ny)
                
    maze[1][1] = 0
    carve_passages(1, 1)
    maze[rows-2][cols-2] = 0 # Solvability guaranteed [cite: 23]
    
    st.session_state.maze = maze
    st.session_state.rows = rows
    st.session_state.cols = cols
    st.session_state.snake_pos = [1, 1]
    st.session_state.current_level = st.session_state.level

# --- Controls & Input ---
maze = st.session_state.maze
rows = st.session_state.rows
cols = st.session_state.cols
snake_pos = st.session_state.snake_pos

def move_snake(dx, dy):
    new_x = snake_pos[0] + dx
    new_y = snake_pos[1] + dy
    
    # Collision Detection [cite: 24]
    if maze[new_y][new_x] == 1:
        st.session_state.shake_frames = 5 # Trigger Screen Shake (Vibration feel)
        st.session_state.snake_pos = [1, 1] # Restart Level Position [cite: 26]
        st.session_state.start_time = time.time() # Reset Timer [cite: 19]
    else:
        st.session_state.snake_pos = [new_x, new_y]
        
    # Win Condition [cite: 18, 25]
    if st.session_state.snake_pos == [cols-2, rows-2]:
        if st.session_state.level < 100:
            st.session_state.level += 1
            st.balloons()
        else:
            st.success("🎉 You completed all 100 levels! You won the game!")

# UI Controls Layout [cite: 20]
st.write(f"### Level: {st.session_state.level} / 100")
elapsed_time = int(time.time() - st.session_state.start_time)
st.write(f"⏱️ **Time Taken:** {elapsed_time} seconds") [cite: 19]

col1, col2, col3 = st.columns([1, 1, 1])
with col2: st.button("🔼 UP", on_click=move_snake, args=(0, -1), use_container_width=True)
col4, col5, col6 = st.columns([1, 1, 1])
with col4: st.button("◀️ LEFT", on_click=move_snake, args=(-1, 0), use_container_width=True)
with col5: 
    if st.button("🔄 Restart", use_container_width=True):
        st.session_state.snake_pos = [1, 1]
        st.session_state.start_time = time.time()
with col6: st.button("▶️ RIGHT", on_click=move_snake, args=(1, 0), use_container_width=True)
col7, col8, col9 = st.columns([1, 1, 1])
with col8: st.button("🔽 DOWN", on_click=move_snake, args=(0, 1), use_container_width=True)

# --- Pygame Rendering Logic  ---
surface = pygame.Surface((WIDTH, HEIGHT))
surface.fill(BG_COLOR)

# Calculate centering offsets
offset_x = (WIDTH - (cols * TILE_SIZE)) // 2
offset_y = (HEIGHT - (rows * TILE_SIZE)) // 2

# Shake Effect
if st.session_state.shake_frames > 0:
    offset_x += random.randint(-5, 5)
    offset_y += random.randint(-5, 5)
    st.session_state.shake_frames -= 1

# Draw Maze Walls [cite: 16, 17]
for r in range(rows):
    for c in range(cols):
        rect = pygame.Rect(offset_x + c * TILE_SIZE, offset_y + r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        if maze[r][c] == 1:
            pygame.draw.rect(surface, WALL_COLOR, rect)

# Draw Goal [cite: 16, 18]
goal_rect = pygame.Rect(offset_x + (cols-2) * TILE_SIZE, offset_y + (rows-2) * TILE_SIZE, TILE_SIZE, TILE_SIZE)
pygame.draw.rect(surface, GOAL_COLOR, goal_rect)

# Draw Snake (Player) [cite: 11, 16]
snake_rect = pygame.Rect(offset_x + snake_pos[0] * TILE_SIZE, offset_y + snake_pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
pygame.draw.rect(surface, SNAKE_COLOR, snake_rect)

# Convert Pygame Surface to PIL Image for Streamlit Compatibility
image_data = pygame.image.tostring(surface, "RGB")
img = Image.frombytes("RGB", (WIDTH, HEIGHT), image_data)

# Display the game frame on Streamlit
st.image(img, use_container_width=True)

# Sidebar Quit Option [cite: 26]
if st.sidebar.button("Quit & Reset Entire Game"):
    st.session_state.clear()
    st.rerun()
