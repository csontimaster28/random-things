import pygame
import random
import sys
from typing import List, Tuple, Optional

"""
Battleship (Torpedó) with Manual Ship Placement — Pygame
-------------------------------------------------
Enhancements:
- Player places ships manually before the game starts.
- Fullscreen mode enabled.
- Added background gradient and design elements.

Controls
- Place ships: left-click to place horizontally, right-click for vertical.
- After placing all ships, game starts.
- Shoot enemy board with left-click.
- N = New game, C = Cheat, R = Reset.
"""

CELL = 40
GRID = 10
MARGIN = 60
TOP_UI = 120
PANEL_H = 64
GAP = 80

SHIP_SIZES = [5, 4, 3, 3, 2]

# fullscreen later — determine screen size dynamically
pygame.init()
info = pygame.display.Info()
W, H = info.current_w, info.current_h

# Colors
BG_TOP = (25, 40, 65)
BG_BOTTOM = (10, 15, 25)
GRID_LINE = (70, 80, 95)
WATER = (36, 48, 70)
WATER_ALT = (32, 44, 66)
SHIP = (90, 120, 150)
HIT = (214, 72, 92)
MISS = (130, 130, 140)
TEXT = (235, 235, 238)
SUBTEXT = (170, 176, 188)
ACCENT = (120, 190, 255)

LEFT_ORIGIN = (MARGIN, TOP_UI)
RIGHT_ORIGIN = (W//2 + GAP//2, TOP_UI)

PLAYER_TURN = 0
AI_TURN = 1
GAME_OVER = 2
PLACEMENT = 3

Vec2 = Tuple[int, int]

def in_bounds(x: int, y: int) -> bool:
    return 0 <= x < GRID and 0 <= y < GRID

class Board:
    def __init__(self):
        self.grid = [[0]*GRID for _ in range(GRID)]
        self.shot = [[0]*GRID for _ in range(GRID)]
        self.ships: List[List[Vec2]] = []
        self.sunk: List[bool] = []

    def place_ship(self, coords: List[Vec2]):
        if all(in_bounds(x, y) and self.grid[y][x] == 0 for (x, y) in coords):
            for x, y in coords:
                self.grid[y][x] = 1
            self.ships.append(coords)
            return True
        return False

    def place_fleet_random(self):
        self.grid = [[0]*GRID for _ in range(GRID)]
        self.ships = []
        for size in SHIP_SIZES:
            placed = False
            while not placed:
                horiz = random.choice([True, False])
                if horiz:
                    x = random.randint(0, GRID - size)
                    y = random.randint(0, GRID - 1)
                    coords = [(x+i, y) for i in range(size)]
                else:
                    x = random.randint(0, GRID - 1)
                    y = random.randint(0, GRID - size)
                    coords = [(x, y+i) for i in range(size)]
                if self.place_ship(coords):
                    placed = True
        self.sunk = [False]*len(self.ships)

    def fire(self, x: int, y: int):
        if not in_bounds(x, y):
            return False, None
        if self.shot[y][x] != 0:
            return False, None
        if self.grid[y][x] == 1:
            self.shot[y][x] = 2
            for idx, ship in enumerate(self.ships):
                if (x, y) in ship:
                    if all(self.shot[cy][cx] == 2 for (cx, cy) in ship):
                        self.sunk[idx] = True
                        return True, idx
                    return True, None
        else:
            self.shot[y][x] = 1
        return False, None

    def all_sunk(self):
        return all(self.sunk) if self.sunk else False

class SimpleAI:
    def __init__(self):
        self.reset()

    def reset(self):
        self.tried = set()

    def next_shot(self, board: Board):
        while True:
            x, y = random.randint(0, GRID-1), random.randint(0, GRID-1)
            if (x, y) not in self.tried:
                self.tried.add((x, y))
                return x, y

class Game:
    def __init__(self):
        pygame.display.set_caption("Torpedó Manual Placement")
        self.screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.big = pygame.font.SysFont("arial", 48, bold=True)
        self.med = pygame.font.SysFont("arial", 28)
        self.small = pygame.font.SysFont("arial", 20)

        self.player = Board()
        self.enemy = Board()
        self.ai = SimpleAI()
        self.turn = PLACEMENT
        self.placing_index = 0
        self.message = "Place your ships: Left-click horizontal, Right-click vertical"
        self.enemy.place_fleet_random()

    def new_game(self):
        self.player = Board()
        self.enemy = Board()
        self.ai.reset()
        self.enemy.place_fleet_random()
        self.turn = PLACEMENT
        self.placing_index = 0
        self.message = "Place your ships"

    def run(self):
        running = True
        while running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        running = False
                    if e.key == pygame.K_n:
                        self.new_game()

                if self.turn == PLACEMENT and e.type == pygame.MOUSEBUTTONDOWN:
                    cell = self.cell_from_mouse(e.pos, LEFT_ORIGIN)
                    if cell:
                        x, y = cell
                        size = SHIP_SIZES[self.placing_index]
                        horiz = e.button == 1
                        coords = [(x+i, y) for i in range(size)] if horiz else [(x, y+i) for i in range(size)]
                        if self.player.place_ship(coords):
                            self.placing_index += 1
                            if self.placing_index >= len(SHIP_SIZES):
                                self.turn = PLAYER_TURN
                                self.message = "All ships placed! Your turn."

                elif self.turn == PLAYER_TURN and e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    cell = self.cell_from_mouse(e.pos, RIGHT_ORIGIN)
                    if cell:
                        x, y = cell
                        hit, sunk = self.enemy.fire(x, y)
                        if hit:
                            self.message = "Hit!"
                            if self.enemy.all_sunk():
                                self.message = "You WIN! Press N for new game."
                                self.turn = GAME_OVER
                        else:
                            self.message = "Miss! Enemy's turn."
                            self.turn = AI_TURN

            if self.turn == AI_TURN:
                x, y = self.ai.next_shot(self.player)
                hit, sunk = self.player.fire(x, y)
                if hit:
                    self.message = "Enemy hit!"
                    if self.player.all_sunk():
                        self.message = "Enemy WINS! Press N for new game."
                        self.turn = GAME_OVER
                else:
                    self.message = "Enemy missed! Your turn."
                    self.turn = PLAYER_TURN

            self.draw()
            self.clock.tick(60)

    def draw(self):
        # background gradient
        for y in range(H):
            c = [BG_TOP[i] + (BG_BOTTOM[i]-BG_TOP[i])*y//H for i in range(3)]
            pygame.draw.line(self.screen, c, (0, y), (W, y))

        title = self.big.render("Torpedó", True, TEXT)
        self.screen.blit(title, (W//2 - title.get_width()//2, 20))

        self.draw_grid(LEFT_ORIGIN, True, self.player, "Your Board")
        self.draw_grid(RIGHT_ORIGIN, False, self.enemy, "Enemy Board")

        msg = self.med.render(self.message, True, ACCENT)
        self.screen.blit(msg, (W//2 - msg.get_width()//2, H - 80))

        pygame.display.flip()

    def draw_grid(self, origin, reveal, board, label):
        ox, oy = origin
        for y in range(GRID):
            for x in range(GRID):
                rect = pygame.Rect(ox + x*CELL, oy + y*CELL, CELL, CELL)
                color = WATER if (x+y)%2==0 else WATER_ALT
                pygame.draw.rect(self.screen, color, rect)
                if reveal and board.grid[y][x] == 1:
                    pygame.draw.rect(self.screen, SHIP, rect)
                if board.shot[y][x] == 1:
                    pygame.draw.circle(self.screen, MISS, rect.center, CELL//6)
                elif board.shot[y][x] == 2:
                    pygame.draw.circle(self.screen, HIT, rect.center, CELL//3)
        pygame.draw.rect(self.screen, GRID_LINE, (ox, oy, GRID*CELL, GRID*CELL), 2)
        t = self.med.render(label, True, TEXT)
        self.screen.blit(t, (ox, oy - 40))

    def cell_from_mouse(self, pos, origin):
        x, y = pos
        ox, oy = origin
        if ox <= x < ox + GRID*CELL and oy <= y < oy + GRID*CELL:
            return (x-ox)//CELL, (y-oy)//CELL
        return None

if __name__ == "__main__":
    Game().run()
