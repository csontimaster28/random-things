import pygame
import numpy as np
from PIL import Image
from scipy.spatial import cKDTree
import sys
import os
import psutil
import time
from collections import deque

# GPU/CuPy acceleration removed — use pure NumPy + SciPy KD-tree for fast color lookup
cp = None

def resource_path(rel_path):
    """Return absolute path to resource, works for dev and PyInstaller bundles."""
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base, rel_path)

# === INIT ===
pygame.init()

# Prompt the user to pick a JPEG file. If they cancel, fall back to bundled "image.jpg".
try:
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    # Support common image formats beyond JPEG
    file_path = filedialog.askopenfilename(
        title="Select image",
        filetypes=[
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tif *.tiff"),
            ("All files", "*")
        ]
    )
    root.destroy()
except Exception:
    file_path = ""

if file_path:
    img_path = file_path
else:
    img_path = resource_path("image.jpg")

# Load image without resizing and set window size to image size
target_img = Image.open(img_path)
# Handle images with alpha by compositing onto white background
if target_img.mode in ("RGBA", "LA") or ("transparency" in target_img.info):
    bg = Image.new("RGB", target_img.size, (255, 255, 255))
    try:
        bg.paste(target_img, mask=target_img.split()[-1])
        target_img = bg
    except Exception:
        target_img = target_img.convert("RGB")
else:
    target_img = target_img.convert("RGB")

# If the image is extremely large, downscale slightly for real-time performance
MAX_DIM = 2048
if max(target_img.size) > MAX_DIM:
    scale = MAX_DIM / max(target_img.size)
    new_size = (int(target_img.size[0] * scale), int(target_img.size[1] * scale))
    target_img = target_img.resize(new_size, Image.LANCZOS)
WIDTH, HEIGHT = target_img.size
screen = pygame.display.set_mode((WIDTH, HEIGHT))
caption = "Pixel Morph Draw"
pygame.display.set_caption(caption)

clock = pygame.time.Clock()

# === PERFORMANCE & RESOURCE MONITORING ===
# FPS averaging buffer
fps_samples = deque(maxlen=60)
# Stats panel toggle and storage
show_stats = False
stats = {}
stats_last_update = 0.0
stats_update_interval = 0.5  # seconds
font_small = pygame.font.SysFont(None, 18)
# icon rect (top-right)
icon_rect = pygame.Rect(WIDTH - 46, 6, 40, 40)

NVML = False
nvml_handle = None


def format_bytes(n):
    if n is None:
        return "N/A"
    n = float(n)
    for unit in ['B','KB','MB','GB','TB']:
        if n < 1024.0:
            return f"{n:.1f}{unit}"
        n /= 1024.0
    return f"{n:.1f}PB"


def estimate_cuda_cores(major, minor, mp_count):
    # Rough estimate using common architectures' cores per SM
    if major is None or mp_count is None:
        return None
    cores_per_sm_map = {2:48, 3:192, 5:128, 6:64, 7:64, 8:64}
    per_sm = cores_per_sm_map.get(major, 64)
    return mp_count * per_sm


def update_stats():
    """Populate the `stats` dict (called periodically)."""
    global stats_last_update, stats
    now = time.time()
    if now - stats_last_update < stats_update_interval:
        return
    stats_last_update = now
    proc = psutil.Process(os.getpid())
    try:
        stats['proc_mem'] = proc.memory_info().rss
    except Exception:
        stats['proc_mem'] = None
    try:
        vm = psutil.virtual_memory()
        stats['ram_percent'] = vm.percent
    except Exception:
        stats['ram_percent'] = None
    try:
        stats['cpu_percent'] = psutil.cpu_percent(interval=None)
    except Exception:
        stats['cpu_percent'] = None
    try:
        stats['cpu_cores'] = psutil.cpu_count(logical=False) or psutil.cpu_count()
    except Exception:
        stats['cpu_cores'] = None
    try:
        cfreq = psutil.cpu_freq()
        stats['cpu_clock'] = cfreq.current if cfreq else None
    except Exception:
        stats['cpu_clock'] = None

    # GPU metrics removed — keep GPU-related stats keys empty
    stats.update({'gpu_name': None, 'gpu_util': None, 'gpu_mem_used': None, 'gpu_mem_total': None, 'gpu_clock': None, 'gpu_cuda_cores': None})


def draw_stats_icon():
    color = (200,200,200)
    mx,my = pygame.mouse.get_pos()
    if icon_rect.collidepoint((mx,my)):
        color = (255,255,255)
    pygame.draw.rect(screen, (40,40,40), icon_rect)
    pygame.draw.circle(screen, color, icon_rect.center, 12, 2)
    txt = font_small.render('i', True, color)
    txt_rect = txt.get_rect(center=icon_rect.center)
    screen.blit(txt, txt_rect)


def draw_stats_panel():
    update_stats()
    lines = []
    avg_fps = (sum(fps_samples)/len(fps_samples)) if fps_samples else 0.0
    lines.append(f"FPS avg: {avg_fps:.1f}")
    cpu_line = f"CPU: {stats.get('cpu_percent','N/A')}% | Cores: {stats.get('cpu_cores','N/A')}"
    if stats.get('cpu_clock'):
        cpu_line += f" | Clock: {stats.get('cpu_clock'):.0f}MHz"
    lines.append(cpu_line)
    lines.append(f"RAM: {format_bytes(stats.get('proc_mem',0))}  ({stats.get('ram_percent','N/A')}%)")
    if stats.get('gpu_name'):
        lines.append(f"GPU: {stats.get('gpu_name')}")
        if stats.get('gpu_util') is not None:
            lines.append(f"GPU Util: {stats.get('gpu_util')}% | CUDA cores: {stats.get('gpu_cuda_cores','N/A')}")
        if stats.get('gpu_mem_total'):
            lines.append(f"GPU Mem: {format_bytes(stats.get('gpu_mem_used',0))} / {format_bytes(stats.get('gpu_mem_total',0))}")
        if stats.get('gpu_clock'):
            lines.append(f"GPU Clock: {stats.get('gpu_clock')} MHz")
    else:
        lines.append("GPU: N/A")

    w = 300
    h = 20 + 18 * len(lines)
    x = WIDTH - w - 10
    y = 52
    pygame.draw.rect(screen, (20,20,20), (x,y,w,h))
    pygame.draw.rect(screen, (150,150,150), (x,y,w,h), 1)
    for i,line in enumerate(lines):
        txt = font_small.render(line, True, (220,220,220))
        screen.blit(txt, (x+8, y+8 + i*18))


target = np.array(target_img)

# UI vertical size reserved for sliders and brush
UI_HEIGHT = 90

target_pixels = []
for y in range(HEIGHT):
    for x in range(WIDTH):
        target_pixels.append(((x, y), target[y, x]))

tgt_pos = np.array([p[0] for p in target_pixels])
# color array as float32, contiguous for KD-tree
tgt_col = np.ascontiguousarray(np.array([p[1] for p in target_pixels], dtype=np.float32))
# Keep track of which target pixels are already taken so we spread draws across multiple pixels
# When a target is chosen it's marked True and won't be chosen again (prevents many pixels going to the same spot)
tgt_used = np.zeros(len(tgt_pos), dtype=bool)

# Build a single cKDTree on the target colors (RGB) for fast nearest-neighbor color lookup.
# This tree is constructed once at initialization and reused for all frames.
tgt_color_tree = cKDTree(tgt_col)

# Precompute float32 target positions to avoid per-draw conversions
tgt_pos_f = np.ascontiguousarray(tgt_pos.astype(np.float32))

# === RAJZOLT PIXELEK ===
draw_pixels = []  # [pos, color, velocity, target_idx]

current_color = [0, 0, 0]
# Brush size (radius in pixels). Mapped to a slider in the UI (1..60).
brush_size = 6

# === COLOR PICKER SLIDERS ===
def draw_slider(y, value, color):
    pygame.draw.rect(screen, (80,80,80), (10, y, 150, 10))
    pygame.draw.circle(screen, color, (10 + int(value/255*150), y+5), 6)

# === SZÍN PÁROSÍTÁS ===
def find_target(color, max_candidates=200):
    """Return the index of a nearby target pixel whose color is closest to `color`.
    Uses a single pre-built `cKDTree` (`tgt_color_tree`) to query the k nearest
    color matches (k is min(max_candidates, len(tgt_col), 50)). Prefer unused
    targets; if none of the k nearest are unused, fall back to searching the
    nearest unused pixel. Only allow reuse when no unused pixels remain.
    """
    n = len(tgt_pos)
    if n == 0:
        return 0
    # cap k to a reasonable range (10..50) for fast queries
    k = min(max(10, max_candidates), 50, n)

    color_pt = np.asarray(color, dtype=np.float32)
    # Query the KD-tree for k nearest color matches (use all CPUs)
    dists, idxs = tgt_color_tree.query(color_pt, k=k, workers=-1)
    # normalize shapes: if k==1, make arrays
    if k == 1:
        idxs = np.array([int(idxs)])
        dists = np.array([dists])
    # Prefer unused target pixels among the k nearest
    for idx in idxs:
        idx = int(idx)
        if not tgt_used[idx]:
            tgt_used[idx] = True
            return idx

    # If any unused pixels remain, compute nearest among them (fallback).
    unused = np.where(~tgt_used)[0]
    if unused.size > 0:
        # compute distances only on the unused subset (vectorized)
        d_unused = np.linalg.norm(tgt_col[unused] - color_pt, axis=1)
        pick = int(np.argmin(d_unused))
        idx = int(unused[pick])
        tgt_used[idx] = True
        return idx

    # No unused pixels left — allow reuse: return overall nearest
    # idxs[0] is the nearest returned by the KD-tree
    return int(idxs[0])

# === LOOP ===
running = True
while running:
    screen.fill((20,20,20))
    # frame timing & FPS averaging
    dt_ms = clock.tick(60)
    dt = dt_ms / 1000.0
    fps_sample = (1.0 / dt) if dt > 0 else 0.0
    fps_samples.append(fps_sample)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Toggle stats panel when top-right icon clicked
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if icon_rect.collidepoint(event.pos):
                show_stats = not show_stats

        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            # only draw when below the UI area (color/brush sliders)
            if my > UI_HEIGHT:
                # spawn `n` samples per frame within the brush radius to form a thicker stroke
                n = max(1, int(brush_size))
                for _ in range(n):
                    # uniform random point inside circle of radius brush_size
                    r = brush_size * np.sqrt(np.random.rand())
                    theta = 2 * np.pi * np.random.rand()
                    ox = r * np.cos(theta)
                    oy = r * np.sin(theta)
                    px = mx + ox
                    py = my + oy
                    idx = find_target(np.array(current_color))
                    draw_pixels.append({
                        "pos": np.array([px, py], dtype=np.float32),
                        "target_idx": int(idx),
                        "color": current_color.copy()
                    })

    # === COLOR PICKER ===
    mx, my = pygame.mouse.get_pos()
    if pygame.mouse.get_pressed()[0]:
        if 10 <= mx <= 160:
            if 10 <= my <= 20:
                current_color[0] = int((mx-10)/150*255)
            if 30 <= my <= 40:
                current_color[1] = int((mx-10)/150*255)
            if 50 <= my <= 60:
                current_color[2] = int((mx-10)/150*255)
            if 70 <= my <= 80:
                # map slider position to brush size in range 1..60
                brush_size = int((mx-10)/150*59) + 1
                brush_size = max(1, min(60, brush_size))

    draw_slider(10, current_color[0], (255,0,0))
    draw_slider(30, current_color[1], (0,255,0))
    draw_slider(50, current_color[2], (0,0,255))
    # brush slider UI (scaled to 0-255)
    brush_val = int((brush_size - 1) / 59 * 255)
    draw_slider(70, brush_val, (200,200,200))

    # draw brush preview when in drawing area
    mx, my = pygame.mouse.get_pos()
    if my > UI_HEIGHT:
        pygame.draw.circle(screen, (200,200,200), (int(mx), int(my)), int(brush_size), 1)

    # === PIXEL MOZGÁS ===
    # Local references for speed
    _tgt_pos_f = tgt_pos_f
    for p in draw_pixels:
        target = _tgt_pos_f[p["target_idx"]]
        direction = target - p["pos"]
        dist = np.linalg.norm(direction)
        # move if far, otherwise snap to avoid jitter
        if dist > 0.5:
            p["pos"] += direction * 0.05
        else:
            p["pos"] = target.copy()
        pygame.draw.circle(screen, p["color"], p["pos"].astype(int), 2)

    # draw FPS and stats icon/panel
    fps_avg = (sum(fps_samples)/len(fps_samples)) if fps_samples else 0.0
    fps_txt = font_small.render(f"FPS: {fps_avg:.1f}", True, (220,220,220))
    screen.blit(fps_txt, (WIDTH - 150, 14))
    draw_stats_icon()
    if show_stats:
        draw_stats_panel()

    pygame.display.flip()

pygame.quit()
