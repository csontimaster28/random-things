import pygame
import numpy as np
from PIL import Image
from scipy.spatial.distance import cdist
import sys
import os
import psutil
import time
from collections import deque

# Optional CUDA acceleration via CuPy (NVIDIA GPUs)
USE_CUDA = False
try:
    import cupy as cp
    try:
        n_devices = cp.cuda.runtime.getDeviceCount()
        if n_devices > 0:
            # Quick smoke-test that runtime compilation / nvrtc is available
            try:
                a = cp.asarray([0., 0.], dtype=cp.float32)
                # this may trigger nvrtc usage in some builds; if it fails, we fallback
                _ = cp.linalg.norm(a - a)
                USE_CUDA = True
                print(f"CUDA-enabled GPU detected ({n_devices} device(s)) — using CuPy for acceleration")
            except Exception:
                USE_CUDA = False
                print("CuPy present but CUDA runtime compilation failed; falling back to NumPy")
        else:
            print("CuPy available but no CUDA device found; falling back to NumPy")
    except Exception:
        print("CuPy imported but CUDA runtime not available; falling back to NumPy")
except Exception:
    cp = None
    print("CuPy not available; using NumPy (CPU)")

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
    file_path = filedialog.askopenfilename(title="Select JPEG image", filetypes=[("JPEG files", "*.jpg *.jpeg")])
    root.destroy()
except Exception:
    file_path = ""

if file_path:
    img_path = file_path
else:
    img_path = resource_path("image.jpg")

# Load image without resizing and set window size to image size
target_img = Image.open(img_path).convert("RGB")
WIDTH, HEIGHT = target_img.size
screen = pygame.display.set_mode((WIDTH, HEIGHT))
caption = "Pixel Morph Draw"
if USE_CUDA:
    caption += " (CUDA)"
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

# Try NVML for detailed NVIDIA GPU metrics; fall back to CuPy memory query if NVML not installed
try:
    import pynvml
    pynvml.nvmlInit()
    NVML = True
    try:
        nvml_device_count = pynvml.nvmlDeviceGetCount()
        if nvml_device_count > 0:
            nvml_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        else:
            nvml_handle = None
            NVML = False
    except Exception:
        nvml_handle = None
        NVML = False
    print("pynvml available — GPU metrics enabled")
except Exception:
    NVML = False
    nvml_handle = None
    # not fatal — we'll still report limited GPU info via CuPy if available


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

    # GPU metrics
    if NVML and nvml_handle:
        try:
            name = pynvml.nvmlDeviceGetName(nvml_handle)
            if isinstance(name, bytes):
                name = name.decode()
            stats['gpu_name'] = name
            util = pynvml.nvmlDeviceGetUtilizationRates(nvml_handle)
            stats['gpu_util'] = util.gpu
            mem = pynvml.nvmlDeviceGetMemoryInfo(nvml_handle)
            stats['gpu_mem_used'] = mem.used
            stats['gpu_mem_total'] = mem.total
            stats['gpu_clock'] = pynvml.nvmlDeviceGetClockInfo(nvml_handle, pynvml.NVML_CLOCK_SM)
            mp = pynvml.nvmlDeviceGetMultiProcessorCount(nvml_handle)
            try:
                major, minor = pynvml.nvmlDeviceGetCudaComputeCapability(nvml_handle)
            except Exception:
                major = minor = None
            stats['gpu_cuda_cores'] = estimate_cuda_cores(major, minor, mp)
        except Exception:
            stats.update({'gpu_name': None, 'gpu_util': None, 'gpu_mem_used': None, 'gpu_mem_total': None, 'gpu_clock': None, 'gpu_cuda_cores': None})
    elif USE_CUDA and cp is not None:
        try:
            free, total = cp.cuda.runtime.memGetInfo()
            stats['gpu_mem_used'] = int(total - free)
            stats['gpu_mem_total'] = int(total)
            stats['gpu_name'] = "CUDA GPU"
            stats['gpu_util'] = None
            stats['gpu_clock'] = None
            stats['gpu_cuda_cores'] = None
        except Exception:
            stats.update({'gpu_name': None, 'gpu_util': None, 'gpu_mem_used': None, 'gpu_mem_total': None, 'gpu_clock': None, 'gpu_cuda_cores': None})
    else:
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
tgt_col = np.array([p[1] for p in target_pixels])
# Keep track of which target pixels are already taken so we spread draws across multiple pixels
# When a target is chosen it's marked True and won't be chosen again (prevents many pixels going to the same spot)
tgt_used = np.zeros(len(tgt_pos), dtype=bool)

# If CUDA is available, upload color positions to device for accelerated distance computations
if USE_CUDA:
    # Convert to float32 on device to avoid overflow and ensure compatibility with CuPy kernels
    tgt_pos_dev = cp.asarray(tgt_pos.astype(cp.float32))
    tgt_col_dev = cp.asarray(tgt_col.astype(cp.float32))

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
    Prefers unused targets to distribute draws across many pixels. Uses CuPy if available for acceleration."""
    global USE_CUDA
    n = len(tgt_pos)
    k = min(max_candidates, n)

    if USE_CUDA:
        try:
            # Work on device to compute distances; transfer only small index arrays back to host
            color_dev = cp.asarray(color, dtype=cp.float32)
            # compute L2 distances on device
            dists_dev = cp.linalg.norm(tgt_col_dev - color_dev, axis=1)
            # get k nearest candidates (unsorted), then sort them (all on device)
            idxs_dev = cp.argpartition(dists_dev, k-1)[:k]
            idxs_dev = idxs_dev[cp.argsort(dists_dev[idxs_dev])]
            # bring small set of indices back to host
            idxs = cp.asnumpy(idxs_dev)
            for idx in idxs:
                if not tgt_used[idx]:
                    tgt_used[idx] = True
                    return int(idx)
            # try any unused pixels by checking distances of unused indices
            unused = np.where(~tgt_used)[0]
            if unused.size > 0:
                unused_dev = cp.asarray(unused)
                dists_unused = dists_dev[unused_dev]
                min_pos = int(cp.asnumpy(cp.argmin(dists_unused)))
                idx = int(unused[min_pos])
                tgt_used[idx] = True
                return idx
            # fallback to nearest (allow reuse)
            return int(cp.asnumpy(cp.argmin(dists_dev)))
        except Exception:
            # If any CuPy/CUDA runtime error occurs, disable CUDA usage and fall back to CPU
            print("Warning: CuPy runtime failed during distance computation — falling back to NumPy")
            USE_CUDA = False

    # CPU fallback
    dists = np.linalg.norm(tgt_col - color, axis=1)
    k = min(max_candidates, len(dists))
    idxs = np.argpartition(dists, k-1)[:k]
    idxs = idxs[np.argsort(dists[idxs])]
    for idx in idxs:
        if not tgt_used[idx]:
            tgt_used[idx] = True
            return int(idx)
    unused = np.where(~tgt_used)[0]
    if unused.size > 0:
        idx = int(unused[np.argmin(dists[unused])])
        tgt_used[idx] = True
        return idx
    return int(np.argmin(dists))

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
                        "pos": np.array([px, py], dtype=float),
                        "target_idx": int(idx),
                        "target": tgt_pos[int(idx)].astype(float),
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
    for p in draw_pixels:
        direction = p["target"] - p["pos"]
        dist = np.linalg.norm(direction)
        # move if far, otherwise snap to avoid jitter
        if dist > 0.5:
            p["pos"] += direction * 0.05
        else:
            p["pos"] = p["target"].copy()
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
