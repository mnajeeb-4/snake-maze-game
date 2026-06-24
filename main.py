import streamlit as st
import os
import random
import time
import math
from PIL import Image

# --- Headless Server Fixes (For Cloud Deployment) ---
os.environ["SDL_VIDEODRIVER"] = "dummy" 
os.environ["SDL_AUDIODRIVER"] = "dummy" 

import pygame

# Initialize Pygame Display Core Only
pygame.display.init()

# --- Streamlit Configurations ---
st.set_page_config(page_title="2D Snake Maze game", layout="centered")
st.title("🐍 2D Snake Maze game ")

# --- Game Resolution Settings ---
TILE_SIZE = 30
WIDTH, HEIGHT = 600, 450

# --- Pure Python RGBA Color Palettes ---
BG_COLOR = (12, 14, 24)
WALL_COLOR = (34, 112, 198)
GOAL_COLOR = (255, 204, 0)

# Item Color Dictionaries
ITEM_COLORS = {
    "apple": (255, 51, 51),
    "gem": (204, 51, 255),
    "diamond": (51, 204, 255)
}

# --- Session State Management (Pure Python Memory Storage) ---
if 'level' not in st.session_state:
    st.session_state.level = 1
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'high_score' not in st.session_state:
    st.session_state.high_score = 0
if 'moves_count' not in st.session_state:
    st.session_state.moves_count = 0
if 'total_apples_eaten' not in st.session_state:
    st.session_state.total_apples_eaten = 0
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()
if 'pure_python_shake' not in st.session_state:
    st.session_state.pure_python_shake = 0
if 'game_logs' not in st.session_state:
    st.session_state.game_logs = ["Game Initialized! Setup Complete."]

# Dynamic Tail Initialization (Length 5)
if 'snake_body' not in st.session_state:
    st.session_state.snake_body = [[1, 1], [1, 1], [1, 1], [1, 1], [1, 1]]

if 'active_items' not in st.session_state:
    st.session_state.active_items = []

# --- Custom Python Helper: Map Item Generation Location ---
def generate_maze_items(maze, rows, cols, snake, num_items=3):
    items_list = []
    available_spaces = []
    
    for r in range(rows):
        for c in range(cols):
            if maze[r][c] == 0 and [c, r] not in snake and [c, r] != [cols-2, rows-2]:
                available_spaces.append([c, r])
                
    if len(available_spaces) < num_items:
        num_items = len(available_spaces)
        
    chosen_spaces = random.sample(available_spaces, num_items) if available_spaces else []
    types = ["apple", "gem", "diamond"]
    
    for i, space in enumerate(chosen_spaces):
        itype = random.choice(types)
        items_list.append({"pos": space, "type": itype})
        
    return items_list

# --- Recursive Maze Builder Core Algorithm ---
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
    st.session_state.game_logs.append(f"Level {st.session_state.level} Maze Rendered Successfully!")

# Mirroring values
maze = st.session_state.maze
rows = st.session_state.rows
cols = st.session_state.cols

# --- Move Snake Actions Handler ---
def move_snake(dx, dy):
    st.session_state.moves_count += 1
    current_segments = list(st.session_state.snake_body)
    lead_head = current_segments[0]
    target_head = [lead_head[0] + dx, lead_head[1] + dy]
    
    # 1. Pure Python Wall Crash Detection
    if not (0 <= target_head[0] < cols and 0 <= target_head[1] < rows) or maze[target_head[1]][target_head[0]] == 1:
        st.session_state.pure_python_shake = 8  # Trigger 8 cycles of canvas-level shake
        st.session_state.snake_body = [[1, 1], [1, 1], [1, 1], [1, 1], [1, 1]] # Restart same layout position
        st.session_state.start_time = time.time()
        st.session_state.game_logs.append("Crashed into a wall! Position Reset to Start.")
        if st.session_state.score >= 5:
            st.session_state.score -= 5
        return

    # 2. Tail Self Intersection Collision
    if target_head in current_segments[:-1]:
        st.session_state.pure_python_shake = 8
        st.session_state.snake_body = [[1, 1], [1, 1], [1, 1], [1, 1], [1, 1]]
        st.session_state.start_time = time.time()
        st.session_state.game_logs.append("Bit your own tail! Level Reset to Start.")
        return
        
    current_segments.insert(0, target_head)
    
    # 3. Loot Collection Logic
    item_hit_index = -1
    for index, live_item in enumerate(st.session_state.active_items):
        if target_head == live_item["pos"]:
            item_hit_index = index
            break
            
    if item_hit_index != -1:
        found_item = st.session_state.active_items.pop(item_hit_index)
        st.session_state.total_apples_eaten += 1
        
        # Point Calculation by item types
        if found_item["type"] == "apple":
            st.session_state.score += 10
            st.session_state.game_logs.append("Ate a juicy apple (+10 Score)")
        elif found_item["type"] == "gem":
            st.session_state.score += 25
            st.session_state.game_logs.append("Acquired a mystical gem (+25 Score)")
        elif found_item["type"] == "diamond":
            st.session_state.score += 50
            st.session_state.game_logs.append("Uncovered a rare diamond (+50 Score)")
            
        if st.session_state.score > st.session_state.high_score:
            st.session_state.high_score = st.session_state.score
            
        # Spawn substitution item safely
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
            st.session_state.game_logs.append(f"Leveled Up to {st.session_state.level}!")
            st.balloons()
        else:
            st.success("Masterful! All 100 Levels Conquered successfully!")

# --- Metric Tracking Layout Displays ---
stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
with stat_col1: st.metric("Current Stage", f"{st.session_state.level} / 100")
with stat_col2: st.metric("Points", st.session_state.score)
with stat_col3: st.metric("Record High", st.session_state.high_score)
with stat_col4: 
    duration = int(time.time() - st.session_state.start_time)
    st.metric("Time Frame", f"{duration}s")

# --- Manual Python Controller Layout Rows ---
c_row1, c_row2, c_row3 = st.columns([1, 1, 1])
with c_row2: st.button("🔼 MOVE UP", on_click=move_snake, args=(0, -1), use_container_width=True)

c_row4, c_row5, c_row6 = st.columns([1, 1, 1])
with c_row4: st.button("◀️ MOVE LEFT", on_click=move_snake, args=(-1, 0), use_container_width=True)
with c_row5: 
    if st.button("🔄 RESTART LEVEL", use_container_width=True):
        st.session_state.snake_body = [[1, 1], [1, 1], [1, 1], [1, 1], [1, 1]]
        st.session_state.start_time = time.time()
        st.session_state.game_logs.append("User requested immediate level coordinate reset.")
with c_row6: st.button("▶️ MOVE RIGHT", on_click=move_snake, args=(1, 0), use_container_width=True)

c_row7, c_row8, c_row9 = st.columns([1, 1, 1])
with c_row8: st.button("🔽 MOVE DOWN", on_click=move_snake, args=(0, 1), use_container_width=True)

# --- Python-Based Graphics & Canvas Generation ---
surface = pygame.Surface((WIDTH, HEIGHT))
surface.fill(BG_COLOR)

# Calculate dynamic center alignments
offset_x = (WIDTH - (cols * TILE_SIZE)) // 2
offset_y = (HEIGHT - (rows * TILE_SIZE)) // 2

# --- PURE PYTHON CANVAS SHAKE RE-CALCULATION ---
# Screen vibration handle karne ke liye render offsets mein matrix variables ko shuffle kiya jata hai
if st.session_state.pure_python_shake > 0:
    offset_x += random.randint(-10, 10)
    offset_y += random.randint(-10, 10)
    st.session_state.pure_python_shake -= 1

# Render Walls Into Matrix
for r in range(rows):
    for c in range(cols):
        block_rect = pygame.Rect(offset_x + c * TILE_SIZE, offset_y + r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        if maze[r][c] == 1:
            pygame.draw.rect(surface, WALL_COLOR, block_rect, border_radius=4)

# Render Trophy Destination Goal
end_rect = pygame.Rect(offset_x + (cols-2) * TILE_SIZE + 2, offset_y + (rows-2) * TILE_SIZE + 2, TILE_SIZE - 4, TILE_SIZE - 4)
pygame.draw.rect(surface, GOAL_COLOR, end_rect, border_radius=6)

# Render Active Collectibles
for target_item in st.session_state.active_items:
    ipos = target_item["pos"]
    itype = target_item["type"]
    icolor = ITEM_COLORS.get(itype, (255, 255, 255))
    
    item_rect = pygame.Rect(offset_x + ipos[0] * TILE_SIZE + 6, offset_y + ipos[1] * TILE_SIZE + 6, TILE_SIZE - 12, TILE_SIZE - 12)
    pygame.draw.rect(surface, icolor, item_rect, border_radius=8)

# Render Beautiful Multi-Segment Animated Snake
for idx, segment in enumerate(st.session_state.snake_body):
    seg_rect = pygame.Rect(offset_x + segment[0] * TILE_SIZE + 3, offset_y + segment[1] * TILE_SIZE + 3, TILE_SIZE - 6, TILE_SIZE - 6)
    
    # Pure Python color blending algorithm for a smooth gradient tail effect
    if idx == 0:
        segment_color = (51, 255, 119) # Bright Green Head
    else:
        # Dynamic phase color mapping logic
        color_phase = (idx * 35) % 120
        segment_color = (0, 210 - color_phase, 80 + color_phase // 2)
        
    pygame.draw.rect(surface, segment_color, seg_rect, border_radius=5)

# Convert Canvas Buffer To Python PIL Image Stream Object
try:
    byte_stream = pygame.image.tobytes(surface, "RGB")
except AttributeError:
    byte_stream = pygame.image.tostring(surface, "RGB")

final_processed_image = Image.frombytes("RGB", (WIDTH, HEIGHT), byte_stream)
st.image(final_processed_image, use_container_width=True)

# --- Pure Python Auto Rerun Loop for Shake Effect ---
if st.session_state.pure_python_shake > 0:
    time.sleep(0.02)
    st.rerun()

# --- Custom Python Dashboard Side Panel ---
st.sidebar.markdown("### 🏆 Live Game Console Logs")
for log_line in reversed(st.session_state.game_logs[-6:]):
    st.sidebar.info(log_line)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Master Reset Settings")
if st.sidebar.button("Hard Reset Game Engine"):
    st.session_state.clear()
    st.rerun()
