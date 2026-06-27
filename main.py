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
st.set_page_config(page_title="2D Snake Maze Ultimate Pro", layout="centered")
st.title("🐍 2D Snake Maze Ultimate Pro")
st.write("Apne keyboard ke Arrow Keys ya W, A, S, D se khele! Snake ke face ko dhyan se dekhein aur portals ka istemal karein.")

# --- Game Resolution Settings ---
TILE_SIZE = 30
WIDTH, HEIGHT = 600, 450

# --- Pure Python RGBA Color Palettes ---
BG_COLOR = (12, 14, 24)
WALL_COLOR = (34, 112, 198)
GOAL_COLOR = (255, 204, 0)
ENEMY_COLOR = (255, 255, 0)       
PORTAL_1_COLOR = (0, 191, 255)    
PORTAL_2_COLOR = (0, 191, 255)    

ITEM_COLORS = {
    "apple": (255, 51, 51),
    "gem": (51, 204, 255),
    "diamond": (51, 204, 255)
}

# --- Session State Management (Pure Python Memory Storage) ---
if 'level' not in st.session_state: st.session_state.level = 1
if 'score' not in st.session_state: st.session_state.score = 0
if 'high_score' not in st.session_state: st.session_state.high_score = 0
if 'start_time' not in st.session_state: st.session_state.start_time = time.time()
if 'pure_python_shake' not in st.session_state: st.session_state.pure_python_shake = 0
if 'game_logs' not in st.session_state: st.session_state.game_logs = ["Game Initialized!"]
if 'snake_body' not in st.session_state: st.session_state.snake_body = [[1, 1], [1, 1], [1, 1], [1, 1], [1, 1]]
if 'active_items' not in st.session_state: st.session_state.active_items = []
if 'portals' not in st.session_state: st.session_state.portals = []
if 'enemies' not in st.session_state: st.session_state.enemies = []

# --- Night Mode Settings ---
hardcore_mode = st.sidebar.checkbox("🌙 Enable Night Mode (Hardcore!)", value=False)

# --- Dynamic Game Entities Generator ---
def generate_entities(maze, rows, cols, snake):
    available_spaces = []
    for r in range(rows):
        for c in range(cols):
            if maze[r][c] == 0 and [c, r] not in snake and [c, r] != [cols-2, rows-2] and [c, r] != [1, 1]:
                available_spaces.append([c, r])
    
    random.shuffle(available_spaces)
    
    # 1. Spawn Items (Loot)
    items_list = []
    types = ["apple", "apple", "gem", "diamond"]
    for _ in range(min(3, len(available_spaces))):
        space = available_spaces.pop()
        items_list.append({"pos": space, "type": random.choice(types)})
        
    # 2. Spawn Teleportation Portals (Needs exactly 2 spaces)
    portals = []
    if len(available_spaces) >= 2:
        portals = [available_spaces.pop(), available_spaces.pop()]
        
    # 3. Spawn Moving Enemies (More enemies on higher levels)
    enemies = []
    num_enemies = min(st.session_state.level // 2, 5) # Max 5 enemies
    for _ in range(min(num_enemies, len(available_spaces))):
        enemies.append(available_spaces.pop())
        
    return items_list, portals, enemies

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
    
    items, ports, enems = generate_entities(built_maze, rows, cols, st.session_state.snake_body)
    st.session
