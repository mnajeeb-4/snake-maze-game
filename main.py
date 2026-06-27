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
st.write("Apne keyboard ke Arrow Keys ya W, A, S, D se khele! Red Dot ghosts se bachein aur tez bhagein.")

# --- Game Resolution Settings ---
TILE_SIZE = 30
WIDTH, HEIGHT = 600, 450

# --- Pure Python RGBA Color Palettes ---
BG_COLOR = (12, 14, 24)
WALL_COLOR = (34, 112, 198)
GOAL_COLOR = (255, 204, 0)
ENEMY_RED_DOT = (255, 30, 30) # Red dot color for ghosts
PORTAL_1_COLOR = (0, 255, 255) 
PORTAL_2_COLOR = (255, 0, 255) 

ITEM_COLORS = {
    "apple": (255, 51, 51),
    "gem": (204, 51, 255),
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
    
    # Spawn Items
    items_list = []
    types = ["apple", "apple", "gem", "diamond"]
    for _ in range(min(3, len(available_spaces))):
        space = available_spaces.pop()
        items_list.append({"pos": space, "type": random.choice(types)})
        
    # Spawn Portals
    portals = []
    if len(available_spaces) >= 2:
        portals = [available_spaces.pop(), available_spaces.pop()]
        
    # Spawn Ghosts
    enemies = []
    num_enemies = min(st.session_state.level // 2, 6) 
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
    st.session_state.active_items = items
    st.session_state.portals = ports
    st.session_state.enemies = enems
    st.session_state.current_level = st.session_state.level
    st.session_state.game_logs.append(f"Level {st.session_state.level} Ready!")

maze = st.session_state.maze
rows = st.session_state.rows
cols = st.session_state.cols

# --- Move Snake Actions Handler ---
def move_snake(dx, dy):
    current_segments = list(st.session_state.snake_body)
    lead_head = current_segments[0]
    target_head = [lead_head[0] + dx, lead_head[1] + dy]
    
    # 1. Wall Crash Detection
    if not (0 <= target_head[0] < cols and 0 <= target_head[1] < rows) or maze[target_head[1]][target_head[0]] == 1:
        st.session_state.pure_python_shake = 5 # Kam time shake for instant recovery
        st.session_state.snake_body = [[1, 1], [1, 1], [1, 1], [1, 1], [1, 1]] 
        st.session_state.start_time = time.time()
        st.session_state.game_logs.append("Crashed into a wall! Position Reset.")
        return

    # 2. Teleportation Portal Check
    if len(st.session_state.portals) == 2:
        if target_head == st.session_state.portals[0]:
            target_head = list(st.session_state.portals[1])
            st.session_state.game_logs.append("Whoosh! Teleported!")
        elif target_head == st.session_state.portals[1]:
            target_head = list(st.session_state.portals[0])
            st.session_state.game_logs.append("Whoosh! Teleported!")

    # 3. Enemy Ghost Patrol Logic
    new_enemies = []
    hit_enemy = False
    for ex, ey in st.session_state.enemies:
        if target_head == [ex, ey]:
            hit_enemy = True
        else:
            moves = [(0,1), (0,-1), (1,0), (-1,0)]
            random.shuffle(moves)
            moved = False
            for edx, edy in moves:
                nex, ney = ex + edx, ey + edy
                if maze[ney][nex] == 0 and [nex, ney] != target_head and [nex, ney] not in st.session_state.portals:
                    new_enemies.append([nex, ney])
                    moved = True
                    break
            if not moved:
                new_enemies.append([ex, ey])
                
    st.session_state.enemies = new_enemies
    
    if hit_enemy or target_head in st.session_state.enemies:
        st.session_state.pure_python_shake = 6
        st.session_state.snake_body = [[1, 1], [1, 1], [1, 1], [1, 1], [1, 1]]
        st.session_state.start_time = time.time()
        st.session_state.game_logs.append("Hit a Red Dot Ghost! Level Reset.")
        return

    # 4. Tail Collision Check
    if target_head in current_segments[:-1]:
        st.session_state.pure_python_shake = 4
        st.session_state.snake_body = [[1, 1], [1, 1], [1, 1], [1, 1], [1, 1]]
        st.session_state.start_time = time.time()
        st.session_state.game_logs.append("Bit your own tail!")
        return
        
    current_segments.insert(0, target_head)
    
    # 5. Loot Collection Logic
    item_hit_index = -1
    for index, live_item in enumerate(st.session_state.active_items):
        if target_head == live_item["pos"]:
            item_hit_index = index
            break
            
    if item_hit_index != -1:
        found_item = st.session_state.active_items.pop(item_hit_index)
        points = {"apple": 10, "gem": 25, "diamond": 50}[found_item["type"]]
        st.session_state.score += points
        st.session_state.game_logs.append(f"Ate {found_item['type']} (+{points})")
        if st.session_state.score > st.session_state.high_score:
            st.session_state.high_score = st.session_state.score
    else:
        current_segments.pop()
        
    st.session_state.snake_body = current_segments
        
    # 6. Target Reached Win Handle
    if target_head == [cols-2, rows-2]:
        if st.session_state.level < 100:
            st.session_state.level += 1
            st.session_state.score += 100
            st.session_state.game_logs.append(f"Level Cleared!")
            st.balloons()
        else:
            st.success("Masterful! Game Completed!")

# --- Metric Tracking Layout Displays ---
stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
with stat_col1: st.metric("Level", f"{st.session_state.level} / 100")
with stat_col2: st.metric("Points", st.session_state.score)
with stat_col3: st.metric("High Score", st.session_state.high_score)
with stat_col4: 
    duration = int(time.time() - st.session_state.start_time)
    st.metric("Timer", f"{duration}s")

# --- ⌨️ OPTIMIZED KEYBOARD CONTROLLER BOX ---
key_input = st.text_input("🎮 TYPE HERE TO MOVE FAST (w/a/s/d or Arrow Keys) then press Enter:", key="kb_in")

if key_input:
    k = key_input.strip().lower()
    if k in ["w", "up"]: move_snake(0, -1)
    elif k in ["s", "down"]: move_snake(0, 1)
    elif k in ["a", "left"]: move_snake(-1, 0)
    elif k in ["d", "right"]: move_snake(1, 0)
    st.session_state.kb_in = "" 
    st.rerun()

with st.expander("Show Screen Control Buttons"):
    c_row1, c_row2, c_row3 = st.columns([1, 1, 1])
    with c_row2: st.button("🔼 UP", on_click=move_snake, args=(0, -1), use_container_width=True)
    c_row4, c_row5, c_row6 = st.columns([1, 1, 1])
    with c_row4: st.button("◀️ LEFT", on_click=move_snake, args=(-1, 0), use_container_width=True)
    with c_row6: st.button("▶️ RIGHT", on_click=move_snake, args=(1, 0), use_container_width=True)
    c_row7, c_row8, c_row9 = st.columns([1, 1, 1])
    with c_row8: st.button("🔽 DOWN", on_click=move_snake, args=(0, 1), use_container_width=True)

# --- Python-Based Graphics & Canvas Generation ---
surface = pygame.Surface((WIDTH, HEIGHT))
surface.fill(BG_COLOR)

offset_x = (WIDTH - (cols * TILE_SIZE)) // 2
offset_y = (HEIGHT - (rows * TILE_SIZE)) // 2

if st.session_state.pure_python_shake > 0:
    offset_x += random.randint(-6, 6)
    offset_y += random.randint(-6, 6)
    st.session_state.pure_python_shake -= 1

# Render Walls
for r in range(rows):
    for c in range(cols):
        block_rect = pygame.Rect(offset_x + c * TILE_SIZE, offset_y + r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        if maze[r][c] == 1:
            pygame.draw.rect(surface, WALL_COLOR, block_rect, border_radius=4)

# Render Goal Trophy
end_rect = pygame.Rect(offset_x + (cols-2) * TILE_SIZE + 2, offset_y + (rows-2) * TILE_SIZE + 2, TILE_SIZE - 4, TILE_SIZE - 4)
pygame.draw.rect(surface, GOAL_COLOR, end_rect, border_radius=6)

# Render Portals (Math Pulsing Radius)
if len(st.session_state.portals) == 2:
    p1, p2 = st.session_state.portals
    pulse_radius = int(10 + 2 * math.sin(time.time() * 6))
    pygame.draw.circle(surface, PORTAL_1_COLOR, (offset_x + p1[0]*TILE_SIZE + 15, offset_y + p1[1]*TILE_SIZE + 15), pulse_radius)
    pygame.draw.circle(surface, PORTAL_2_COLOR, (offset_x + p2[0]*TILE_SIZE + 15, offset_y + p2[1]*TILE_SIZE + 15), pulse_radius)

# RENDER ITEMS: Apple aur loot items ko properly sharp rectangular frames mein rkha hai (No Dot)
for target_item in st.session_state.active_items:
    ipos = target_item["pos"]
    icolor = ITEM_COLORS.get(target_item["type"], (255, 255, 255))
    item_rect = pygame.Rect(offset_x + ipos[0] * TILE_SIZE + 5, offset_y + ipos[1] * TILE_SIZE + 5, TILE_SIZE - 10, TILE_SIZE - 10)
    pygame.draw.rect(surface, icolor, item_rect, border_radius=6)

# RENDER GHOST ENEMIES: Ab ghost ki jagah proper RED DOT dikhega jaisa aapne kaha!
for ex, ey in st.session_state.enemies:
    center_dot_x = offset_x + ex * TILE_SIZE + 15
    center_dot_y = offset_y + ey * TILE_SIZE + 15
    pygame.draw.circle(surface, ENEMY_RED_DOT, (center_dot_x, center_dot_y), 6) # Small clean red dot

# RENDER PROPER SNAKE: Snake ke head aur body pieces ke gaps khatam karke cohesive proper snake banaya hai
for idx, segment in enumerate(st.session_state.snake_body):
    # Border gap kam kiya taake body aapas mein seamless proper snake dikhe
    seg_rect = pygame.Rect(offset_x + segment[0] * TILE_SIZE + 1, offset_y + segment[1] * TILE_SIZE + 1, TILE_SIZE - 2, TILE_SIZE - 2)
    if idx == 0:
        pygame.draw.rect(surface, (51, 255, 119), seg_rect, border_radius=4) # Head
    else:
        color_phase = (idx * 25) % 100
        pygame.draw.rect(surface, (0, 200 - color_phase, 90 + color_phase), seg_rect, border_radius=2) # Connected tail

# Fog of War Effect
if hardcore_mode:
    fog = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    fog.fill((5, 5, 10, 245)) 
    head_pos = st.session_state.snake_body[0]
    center_x = offset_x + head_pos[0] * TILE_SIZE + 15
    center_y = offset_y + head_pos[1] * TILE_SIZE + 15
    flicker_radius = int(75 + 4 * math.sin(time.time() * 14))
    pygame.draw.circle(fog, (0, 0, 0, 0), (center_x, center_y), flicker_radius) 
    surface.blit(fog, (0, 0))

# Convert to PIL and output
try:
    byte_stream = pygame.image.tobytes(surface, "RGB")
except AttributeError:
    byte_stream = pygame.image.tostring(surface, "RGB")

st.image(Image.frombytes("RGB", (WIDTH, HEIGHT), byte_stream), use_container_width=True)

# Super Smooth Rerun speed optimization
if st.session_state.pure_python_shake > 0:
    time.sleep(0.005) # Super fast execution speed loop
    st.rerun()

# --- Sidebar Logs ---
st.sidebar.markdown("### 🏆 Live Game Console Logs")
for log_line in reversed(st.session_state.game_logs[-6:]):
    st.sidebar.info(log_line)

st.sidebar.markdown("---")
if st.sidebar.button("Hard Reset Game Engine"):
    st.session_state.clear()
    st.rerun()
