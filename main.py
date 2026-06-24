import streamlit as st
import os
import random
import time
from PIL import Image

# --- Headless Server Fixes (For Cloud Deployment) ---
os.environ["SDL_VIDEODRIVER"] = "dummy" 
os.environ["SDL_AUDIODRIVER"] = "dummy" 

import pygame
import keyboard  # Pure Python Native Keyboard Listener

# Initialize Pygame Display Core Only
pygame.display.init()

# --- Streamlit Configurations ---
st.set_page_config(page_title="2D Snake Maze Ultimate Pro", layout="centered")
st.title("🐍 2D Snake Maze Ultimate Pro")
st.write("Use your Keyboard Arrow Keys (⬆️ ⬇️ ⬅️ ➡️) or W, A, S, D to play!")

# --- Game Resolution Settings ---
TILE_SIZE = 30
WIDTH, HEIGHT = 600, 450

# --- Pure Python RGBA Color Palettes ---
BG_COLOR = (12, 14, 24)
WALL_COLOR = (34, 112, 198)
GOAL_COLOR = (255, 204, 0)

ITEM_COLORS = {
    "apple": (255, 51, 51),
    "gem": (204, 51, 255),
    "diamond": (51, 204, 255)
}

# --- Session State Management ---
if 'level' not in st.session_state:
    st.session_state.level = 1
    st.session_state.score = 0
    st.session_state.high_score = 0
    st.session_state.start_time = time.time()
    st.session_state.pure_python_shake = 0
    st.session_state.snake_body = [[1, 1], [1, 1], [1, 1], [1, 1], [1, 1]]
    st.session_state.active_items = []
    # Anti-bounce variable for keys
    st.session_state.last_move_time = time.time()

# --- Item Generation Logic ---
def generate_maze_items(maze, rows, cols, snake, num_items=3):
    items_list = []
    available_spaces = []
    for r in range(rows):
        for c in range(cols):
            if maze[r][c] == 0 and [c, r] not in snake and [c, r] != [cols-2, rows-2]:
                available_spaces.append([c, r])
                
    if len(available_spaces) < num_items: num_items = len(available_spaces)
    chosen_spaces = random.sample(available_spaces, num_items) if available_spaces else []
    for space in chosen_spaces:
        items_list.append({"pos": space, "type": random.choice(["apple", "gem", "diamond"])})
    return items_list

# --- Maze Generation Algorithm ---
if 'maze' not in st.session_state or 'current_level' not in st.session_state or st.session_state.current_level != st.session_state.level:
    cols = min(11 + (st.session_state.level // 4) * 2, 19)
    rows = min(9 + (st.session_state.level // 4) * 2, 13)
    
    built_maze = [[1 for _ in range(cols)] for _ in range(rows)]
    
    def process_passages(cx, cy):
        vectors = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(vectors)
        for dx, dy in vectors:
            nx, ny = cx + dx, cy + dy
            if 1 <= ny < rows-1 and 1 <= nx < cols-1 and built_maze[ny][nx] == 1:
                built_maze[cy + dy//2][cx + dx//2] = 0
                built_maze[ny][nx] = 0
                process_passages(nx, ny)
                
    built_maze[1][1] = 0
    process_passages(1, 1)
    built_maze[rows-2][cols-2] = 0
    
    st.session_state.maze = built_maze
    st.session_state.rows = rows
    st.session_state.cols = cols
    st.session_state.snake_body = [[1, 1], [1, 1], [1, 1], [1, 1], [1, 1]]
    st.session_state.active_items = generate_maze_items(built_maze, rows, cols, st.session_state.snake_body)
    st.session_state.current_level = st.session_state.level

maze = st.session_state.maze
rows = st.session_state.rows
cols = st.session_state.cols

# --- Snake Movement Logic ---
def move_snake(dx, dy):
    current_segments = list(st.session_state.snake_body)
    lead_head = current_segments[0]
    target_head = [lead_head[0] + dx, lead_head[1] + dy]
    
    # 1. Wall Crash Detection (Shake & Reset)
    if not (0 <= target_head[0] < cols and 0 <= target_head[1] < rows) or maze[target_head[1]][target_head[0]] == 1:
        st.session_state.pure_python_shake = 8  
        st.session_state.snake_body = [[1, 1], [1, 1], [1, 1], [1, 1], [1, 1]]
        if st.session_state.score >= 5: st.session_state.score -= 5
        return

    # 2. Tail Collision Detection
    if target_head in current_segments[:-1]:
        st.session_state.pure_python_shake = 8
        st.session_state.snake_body = [[1, 1], [1, 1], [1, 1], [1, 1], [1, 1]]
        return
        
    current_segments.insert(0, target_head)
    
    # 3. Loot Logic
    item_hit_index = -1
    for index, live_item in enumerate(st.session_state.active_items):
        if target_head == live_item["pos"]:
            item_hit_index = index
            break
            
    if item_hit_index != -1:
        found_item = st.session_state.active_items.pop(item_hit_index)
        if found_item["type"] == "apple": st.session_state.score += 10
        elif found_item["type"] == "gem": st.session_state.score += 25
        elif found_item["type"] == "diamond": st.session_state.score += 50
            
        if st.session_state.score > st.session_state.high_score:
            st.session_state.high_score = st.session_state.score
            
        if len(st.session_state.active_items) < 2:
            st.session_state.active_items.extend(generate_maze_items(maze, rows, cols, current_segments, 2))
    else:
        current_segments.pop()
        
    st.session_state.snake_body = current_segments
        
    # 4. Target Coordinates Destination Reached
    if target_head == [cols-2, rows-2]:
        if st.session_state.level < 100:
            st.session_state.level += 1
            st.session_state.score += 100
        else:
            st.success("Masterful! All 100 Levels Conquered successfully!")

# --- Metrics Display ---
stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
with stat_col1: st.metric("Current Stage", f"{st.session_state.level} / 100")
with stat_col2: st.metric("Points", st.session_state.score)
with stat_col3: st.metric("Record High", st.session_state.high_score)
with stat_col4: 
    duration = int(time.time() - st.session_state.start_time)
    st.metric("Time Frame", f"{duration}s")


# ==========================================
# PURE PYTHON KEYBOARD LISTENER (NO BUTTONS, NO JS)
# ==========================================
current_time = time.time()
# Only allow a move every 0.15 seconds to prevent super-fast multiple movements
if current_time - st.session_state.last_move_time > 0.15:
    if keyboard.is_pressed('up') or keyboard.is_pressed('w'):
        move_snake(0, -1)
        st.session_state.last_move_time = current_time
    elif keyboard.is_pressed('down') or keyboard.is_pressed('s'):
        move_snake(0, 1)
        st.session_state.last_move_time = current_time
    elif keyboard.is_pressed('left') or keyboard.is_pressed('a'):
        move_snake(-1, 0)
        st.session_state.last_move_time = current_time
    elif keyboard.is_pressed('right') or keyboard.is_pressed('d'):
        move_snake(1, 0)
        st.session_state.last_move_time = current_time


# --- Python-Based Graphics Generation ---
surface = pygame.Surface((WIDTH, HEIGHT))
surface.fill(BG_COLOR)

offset_x = (WIDTH - (cols * TILE_SIZE)) // 2
offset_y = (HEIGHT - (rows * TILE_SIZE)) // 2

# Screen Shake Logic
if st.session_state.pure_python_shake > 0:
    offset_x += random.randint(-10, 10)
    offset_y += random.randint(-10, 10)
    st.session_state.pure_python_shake -= 1

# Draw Walls
for r in range(rows):
    for c in range(cols):
        block_rect = pygame.Rect(offset_x + c * TILE_SIZE, offset_y + r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        if maze[r][c] == 1:
            pygame.draw.rect(surface, WALL_COLOR, block_rect, border_radius=4)

# Draw Goal
end_rect = pygame.Rect(offset_x + (cols-2) * TILE_SIZE + 2, offset_y + (rows-2) * TILE_SIZE + 2, TILE_SIZE - 4, TILE_SIZE - 4)
pygame.draw.rect(surface, GOAL_COLOR, end_rect, border_radius=6)

# Draw Items
for target_item in st.session_state.active_items:
    ipos = target_item["pos"]
    itype = target_item["type"]
    icolor = ITEM_COLORS.get(itype, (255, 255, 255))
    item_rect = pygame.Rect(offset_x + ipos[0] * TILE_SIZE + 6, offset_y + ipos[1] * TILE_SIZE + 6, TILE_SIZE - 12, TILE_SIZE - 12)
    pygame.draw.rect(surface, icolor, item_rect, border_radius=8)

# Draw Snake
for idx, segment in enumerate(st.session_state.snake_body):
    seg_rect = pygame.Rect(offset_x + segment[0] * TILE_SIZE + 3, offset_y + segment[1] * TILE_SIZE + 3, TILE_SIZE - 6, TILE_SIZE - 6)
    if idx == 0:
        segment_color = (51, 255, 119) 
    else:
        color_phase = (idx * 35) % 120
        segment_color = (0, 210 - color_phase, 80 + color_phase // 2)
    pygame.draw.rect(surface, segment_color, seg_rect, border_radius=5)

# Convert to Image
try:
    byte_stream = pygame.image.tobytes(surface, "RGB")
except AttributeError:
    byte_stream = pygame.image.tostring(surface, "RGB")

final_processed_image = Image.frombytes("RGB", (WIDTH, HEIGHT), byte_stream)
st.image(final_processed_image, use_container_width=True)


# ==========================================
# AUTO REFRESH LOOP (REQUIRED FOR PURE PYTHON WEB GAMES)
# ==========================================
# Streamlit needs to constantly refresh the screen to catch your next keyboard press
time.sleep(0.05) # Speed of the game update (frame rate)
st.rerun()
