import streamlit as st
import os
import random
import time
from PIL import Image

# --- Headless Server Fixes (Before importing Pygame) ---
os.environ["SDL_VIDEODRIVER"] = "dummy" 
os.environ["SDL_AUDIODRIVER"] = "dummy" 

import pygame

# Only initialize the display driver to avoid cloud server crashes
pygame.display.init()

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="2D Snake Maze Game", layout="centered")
st.title("🐍 2D Snake Maze Game")
st.write("Control the snake using your keyboard's **ARROW KEYS**! 🔼 🔽 ◀️ ▶️")

# --- Game Constants ---
TILE_SIZE = 30
WIDTH, HEIGHT = 600, 450

# Colors
BG_COLOR = (20, 20, 30)
WALL_COLOR = (50, 150, 200)      # Obstacles / Walls
SNAKE_HEAD_COLOR = (50, 250, 50)  # Bright Green for Head
SNAKE_BODY_COLOR = (34, 139, 44)  # Darker Forest Green for Tail
GOAL_COLOR = (220, 50, 50)       # Red Goal

# --- Session State for Level & Progress ---
if 'level' not in st.session_state:
    st.session_state.level = 1
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()
if 'shake_frames' not in st.session_state:
    st.session_state.shake_frames = 0
if 'trigger_vibrate' not in st.session_state:
    st.session_state.trigger_vibrate = False

# --- Proper Snake Body Initialization (Length 3) ---
if 'snake_body' not in st.session_state:
    st.session_state.snake_body = [[1, 1], [1, 1], [1, 1]] 

# --- Random Maze Generation Algorithm ---
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
    maze[rows-2][cols-2] = 0 # Solvability guaranteed
    
    st.session_state.maze = maze
    st.session_state.rows = rows
    st.session_state.cols = cols
    st.session_state.snake_body = [[1, 1], [1, 1], [1, 1]]
    st.session_state.current_level = st.session_state.level

# --- Controls & Input Logic ---
maze = st.session_state.maze
rows = st.session_state.rows
cols = st.session_state.cols

def move_snake(dx, dy):
    current_body = list(st.session_state.snake_body)
    head = current_body[0]
    new_head = [head[0] + dx, head[1] + dy]
    
    # Collision Detection with Walls
    if maze[new_head[1]][new_head[0]] == 1:
        st.session_state.shake_frames = 1 # Triggers web page CSS shake
        st.session_state.trigger_vibrate = True # Triggers device hardware vibration
        st.session_state.snake_body = [[1, 1], [1, 1], [1, 1]] # Reset body to start position
        st.session_state.start_time = time.time() # Reset Timer for this exact same level
        return
    else:
        # Move snake segments forward
        current_body.insert(0, new_head)
        current_body.pop()
        st.session_state.snake_body = current_body
        
    # Win Condition
    if new_head == [cols-2, rows-2]:
        if st.session_state.level < 100:
            st.session_state.level += 1
            st.balloons()
        else:
            st.success("🎉 You completed all 100 levels! You won the game!")

# UI Information Display
st.write(f"### Level: {st.session_state.level} / 100")
elapsed_time = int(time.time() - st.session_state.start_time)
st.write(f"⏱️ **Time Taken:** {elapsed_time} seconds")

# Invisible steering buttons layout for JavaScript triggers
col1, col2, col3 = st.columns([1, 1, 1])
with col2: st.button("🔼 UP", on_click=move_snake, args=(0, -1), use_container_width=True)
col4, col5, col6 = st.columns([1, 1, 1])
with col4: st.button("◀️ LEFT", on_click=move_snake, args=(-1, 0), use_container_width=True)
with col5: 
    if st.button("🔄 Restart", use_container_width=True):
        st.session_state.snake_body = [[1, 1], [1, 1], [1, 1]]
        st.session_state.start_time = time.time()
with col6: st.button("▶️ RIGHT", on_click=move_snake, args=(1, 0), use_container_width=True)
col7, col8, col9 = st.columns([1, 1, 1])
with col8: st.button("🔽 DOWN", on_click=move_snake, args=(0, 1), use_container_width=
