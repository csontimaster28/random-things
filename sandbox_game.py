import pygame
import random
import sys

# Simple sandbox physics game
# Elements: empty=0, sand=1, water=2, sodium=3, dirt=4, snow=5

CELL_EMPTY = 0
CELL_SAND = 1
CELL_WATER = 2
CELL_SODIUM = 3
CELL_DIRT = 4
CELL_SNOW = 5

COLORS = {
    CELL_EMPTY: (10, 10, 10),
    CELL_SAND: (194, 178, 128),
    CELL_WATER: (64, 164, 223),
    CELL_SODIUM: (240, 240, 240),
    CELL_DIRT: (106, 55, 5),
    CELL_SNOW: (230, 250, 250),
}

WIDTH_CELLS = 200
HEIGHT_CELLS = 150
CELL_SIZE = 4

SCREEN_W = WIDTH_CELLS * CELL_SIZE
SCREEN_H = HEIGHT_CELLS * CELL_SIZE

FPS = 60

def make_grid():
    return [[CELL_EMPTY for _ in range(WIDTH_CELLS)] for _ in range(HEIGHT_CELLS)]

def in_bounds(x, y):
    return 0 <= x < WIDTH_CELLS and 0 <= y < HEIGHT_CELLS

def swap(grid, x1, y1, x2, y2):
    grid[y1][x1], grid[y2][x2] = grid[y2][x2], grid[y1][x1]

def update_grid(grid, explosions, frame_count):
    # Process from bottom to top
    for y in range(HEIGHT_CELLS - 1, -1, -1):
        for x in range(WIDTH_CELLS):
            cell = grid[y][x]
            if cell == CELL_SAND:
                # sand falls like granular
                if y + 1 < HEIGHT_CELLS and grid[y+1][x] == CELL_EMPTY:
                    swap(grid, x, y, x, y+1)
                else:
                    dirs = []
                    if x - 1 >= 0 and y + 1 < HEIGHT_CELLS and grid[y+1][x-1] == CELL_EMPTY:
                        dirs.append((x-1, y+1))
                    if x + 1 < WIDTH_CELLS and y + 1 < HEIGHT_CELLS and grid[y+1][x+1] == CELL_EMPTY:
                        dirs.append((x+1, y+1))
                    if dirs:
                        nx, ny = random.choice(dirs)
                        swap(grid, x, y, nx, ny)
            elif cell == CELL_WATER:
                # water prefers down, otherwise sideways
                if y + 1 < HEIGHT_CELLS and grid[y+1][x] == CELL_EMPTY:
                    swap(grid, x, y, x, y+1)
                else:
                    choices = []
                    if x - 1 >= 0 and grid[y][x-1] == CELL_EMPTY:
                        choices.append((x-1, y))
                    if x + 1 < WIDTH_CELLS and grid[y][x+1] == CELL_EMPTY:
                        choices.append((x+1, y))
                    if choices:
                        nx, ny = random.choice(choices)
                        swap(grid, x, y, nx, ny)
            elif cell == CELL_SNOW:
                # snow falls slowly and piles (update only every other frame)
                if frame_count % 2 != 0:
                    continue
                if y + 1 < HEIGHT_CELLS and grid[y+1][x] == CELL_EMPTY:
                    swap(grid, x, y, x, y+1)
                else:
                    dirs = []
                    if x - 1 >= 0 and y + 1 < HEIGHT_CELLS and grid[y+1][x-1] == CELL_EMPTY:
                        dirs.append((x-1, y+1))
                    if x + 1 < WIDTH_CELLS and y + 1 < HEIGHT_CELLS and grid[y+1][x+1] == CELL_EMPTY:
                        dirs.append((x+1, y+1))
                    if dirs and random.random() < 0.6:
                        nx, ny = random.choice(dirs)
                        swap(grid, x, y, nx, ny)
            elif cell == CELL_DIRT:
                # mostly static, but can be moved if space below
                if y + 1 < HEIGHT_CELLS and grid[y+1][x] == CELL_EMPTY and random.random() < 0.02:
                    swap(grid, x, y, x, y+1)
            elif cell == CELL_SODIUM:
                # check for adjacent water to trigger reaction
                reacted = False
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]:
                    nx, ny = x+dx, y+dy
                    if in_bounds(nx, ny) and grid[ny][nx] == CELL_WATER:
                        # trigger explosion clearing nearby cells
                        rad = 2
                        for ex in range(x-rad, x+rad+1):
                            for ey in range(y-rad, y+rad+1):
                                if in_bounds(ex, ey):
                                    grid[ey][ex] = CELL_EMPTY
                                    explosions.append([ex, ey, 8])
                        reacted = True
                        break
                if reacted:
                    # remove the sodium itself
                    grid[y][x] = CELL_EMPTY
                    continue
                # sodium falls like sand
                if y + 1 < HEIGHT_CELLS and grid[y+1][x] == CELL_EMPTY:
                    swap(grid, x, y, x, y+1)
                else:
                    dirs = []
                    if x - 1 >= 0 and y + 1 < HEIGHT_CELLS and grid[y+1][x-1] == CELL_EMPTY:
                        dirs.append((x-1, y+1))
                    if x + 1 < WIDTH_CELLS and y + 1 < HEIGHT_CELLS and grid[y+1][x+1] == CELL_EMPTY:
                        dirs.append((x+1, y+1))
                    if dirs and random.random() < 0.9:
                        nx, ny = random.choice(dirs)
                        swap(grid, x, y, nx, ny)

    # decay explosions
    for ex in explosions[:]:
        ex[2] -= 1
        if ex[2] <= 0:
            explosions.remove(ex)

def draw_grid(screen, grid, explosions):
    for y in range(HEIGHT_CELLS):
        row = grid[y]
        for x in range(WIDTH_CELLS):
            color = COLORS.get(row[x], (255, 0, 255))
            rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            screen.fill(color, rect)
    # draw explosions as red flashes
    for (ex, ey, life) in explosions:
        alpha = max(0, min(255, int(255 * (life / 8))))
        color = (255, 80, 0)
        rect = pygame.Rect(ex*CELL_SIZE, ey*CELL_SIZE, CELL_SIZE, CELL_SIZE)
        screen.fill(color, rect)

def draw_ui(screen, selected, brush_size, paused):
    font = pygame.font.get_default_font()
    f = pygame.font.Font(font, 14)
    lines = [
        f"Selected: {selected}  (1:Sand 2:Water 3:Sodium 4:Dirt 5:Snow)",
        f"Brush: {brush_size}  (Use mouse, +/- to change)",
        f"Space: Pause ({'Paused' if paused else 'Running'})  C:Clear  Right-click: Erase",
    ]
    y = 6
    for line in lines:
        surf = f.render(line, True, (240,240,240))
        screen.blit(surf, (6, y))
        y += 18

def element_code_from_index(idx):
    mapping = {1: CELL_SAND, 2: CELL_WATER, 3: CELL_SODIUM, 4: CELL_DIRT, 5: CELL_SNOW}
    return mapping.get(idx, CELL_SAND)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption('Sandbox Physics')
    clock = pygame.time.Clock()

    grid = make_grid()
    explosions = []
    running = True
    paused = False
    selected_idx = 1
    selected = element_code_from_index(selected_idx)
    brush = 4
    frame_count = 0

    while running:
        frame_count += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_c:
                    grid = make_grid()
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    brush = min(32, brush + 1)
                elif event.key == pygame.K_MINUS:
                    brush = max(1, brush - 1)
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5):
                    selected_idx = int(event.unicode)
                    selected = element_code_from_index(selected_idx)

        mouse_pressed = pygame.mouse.get_pressed()
        mx, my = pygame.mouse.get_pos()
        grid_x = mx // CELL_SIZE
        grid_y = my // CELL_SIZE

        if mouse_pressed[0]:
            # draw selected
            for dx in range(-brush+1, brush):
                for dy in range(-brush+1, brush):
                    nx, ny = grid_x + dx, grid_y + dy
                    if in_bounds(nx, ny):
                        grid[ny][nx] = selected
        if mouse_pressed[2]:
            # erase
            for dx in range(-brush+1, brush):
                for dy in range(-brush+1, brush):
                    nx, ny = grid_x + dx, grid_y + dy
                    if in_bounds(nx, ny):
                        grid[ny][nx] = CELL_EMPTY

        if not paused:
            update_grid(grid, explosions, frame_count)

        draw_grid(screen, grid, explosions)
        draw_ui(screen, ['Sand','Water','Sodium','Dirt','Snow'][selected_idx-1], brush, paused)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
