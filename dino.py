import pygame
import random
import numpy as np
import threading

pygame.init()

# ----------------- Képernyő -----------------
WIDTH, HEIGHT = 900, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chrome Dino Pixel-Art Enhanced")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

# ----------------- Hangok -----------------
def play_sound(frequency, duration=0.1, volume=0.3):
    def _play():
        fs = 44100
        t = np.linspace(0, duration, int(fs*duration), endpoint=False)
        wave = volume * np.sin(2*np.pi*frequency*t)
        import sounddevice as sd
        sd.play(wave, samplerate=fs)
        sd.wait()
    threading.Thread(target=_play, daemon=True).start()

def jump_sound(): play_sound(800,0.08)
def point_sound(): play_sound(1200,0.08)
def death_sound(): play_sound(500,0.3)

# ----------------- Színek -----------------
dark_mode = False
last_switch = 0
score = 0
game_over = False
running = True

def get_colors():
    if dark_mode:
        return (10,10,30), (255,255,255)
    else:
        return (135,206,235), (0,0,0)

# ----------------- Dino -----------------
dino_x, dino_y = 50, HEIGHT-60
dino_w, dino_h = 40, 40
dino_vel_y = 0
gravity = 1
jump_strength = -15
on_ground = True
dino_frame = 0
dino_anim_timer = 0

# ----------------- Obstacles -----------------
obstacles = []
CACTUS, BIRD = "cactus", "bird"
spawn_timer = 0
obstacle_speed = 6

# ----------------- Parallax -----------------
clouds = [{"x": random.randint(0, WIDTH), "y": random.randint(20,100), "speed": random.uniform(0.2,0.6)} for _ in range(6)]
sun_pos = 700
moon_pos = -100
ground_pattern = [0,1,0,1,1,0,1,0]

# ----------------- Pixel-Art rajzoló függvények -----------------
def draw_dino(x, y, frame):
    color = (40,40,40)

    # Test
    pygame.draw.ellipse(screen, color, (x, y+10, 42, 22))
    pygame.draw.circle(screen, color, (x+35, y+12), 10)

    # Farok
    pygame.draw.polygon(screen, color, [
        (x, y+20),
        (x-18, y+26),
        (x, y+30)
    ])

    # Láb animáció
    if frame % 2 == 0:
        pygame.draw.line(screen, color, (x+12, y+32), (x+12, y+42), 4)
        pygame.draw.line(screen, color, (x+24, y+32), (x+30, y+42), 4)
    else:
        pygame.draw.line(screen, color, (x+12, y+32), (x+6, y+42), 4)
        pygame.draw.line(screen, color, (x+24, y+32), (x+24, y+42), 4)

def draw_bird(x, y, frame):
    color = (60,60,60)

    wing = -6 if frame % 2 == 0 else 6

    pygame.draw.circle(screen, color, (x, y), 6)

    pygame.draw.line(screen, color, (x, y), (x-14, y+wing), 3)
    pygame.draw.line(screen, color, (x, y), (x+14, y+wing), 3)

def draw_cactus(x, ground_y):
    color = (0,150,0)

    # Törzs
    pygame.draw.rect(screen, color, (x, ground_y-50, 16, 50))

    # Karok
    pygame.draw.rect(screen, color, (x-10, ground_y-35, 10, 8))
    pygame.draw.rect(screen, color, (x+16, ground_y-25, 10, 8))

def draw_ground(y):
    for i in range(0, WIDTH, 10):
        color = (100,50,0) if ground_pattern[(i//10)%len(ground_pattern)] else (120,70,0)
        pygame.draw.rect(screen,color,(i,y,10,20))

def draw_cloud(cloud):
    pygame.draw.ellipse(screen,(255,255,255),(cloud["x"],cloud["y"],50,20))

def draw_sun_moon(pos,is_sun=True):
    color = (255,255,0) if is_sun else (200,200,255)
    pygame.draw.circle(screen,color,(int(pos),60),30)

# ----------------- Main loop -----------------
while running:
    clock.tick(60)
    bg_color, fg_color = get_colors()
    screen.fill(bg_color)

    # események
    for event in pygame.event.get():
        if event.type==pygame.QUIT: running=False
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_SPACE and on_ground and not game_over:
                dino_vel_y = jump_strength
                on_ground=False
                jump_sound()
            if event.key==pygame.K_r and game_over:
                obstacles.clear()
                score=0
                dino_y=HEIGHT-60
                dino_vel_y=0
                game_over=False
                dark_mode=False
                last_switch=0
                obstacle_speed=6

    if not game_over:
        # Dino physics
        dino_vel_y += gravity
        dino_y += dino_vel_y
        if dino_y >= HEIGHT-60:
            dino_y = HEIGHT-60
            dino_vel_y = 0
            on_ground = True

        # Dino animáció
        dino_anim_timer += 1
        if dino_anim_timer >= 5:
            dino_frame = (dino_frame + 1) % 4
            dino_anim_timer = 0

        # Spawn obstacles
        spawn_timer += 1
        if spawn_timer > random.randint(60,100):
            kind=random.choice([CACTUS,BIRD])
            if kind==CACTUS:
                obstacles.append({"type": CACTUS, "x": WIDTH, "y": HEIGHT-20})
            else:
                obstacles.append({"type":BIRD,"x":WIDTH,"y":random.choice([HEIGHT-90,HEIGHT-120]),"frame":0,"timer":0})
            spawn_timer=0

        # Move obstacles
        for obs in obstacles:
            obs["x"] -= obstacle_speed
            if obs["type"]==BIRD:
                obs["timer"] += 1
                if obs["timer"] >= 10:
                    obs["frame"] = (obs["frame"]+1)%4
                    obs["timer"]=0
        obstacles = [o for o in obstacles if o["x"]>-50]

        # Collision
        dino_rect = pygame.Rect(dino_x,dino_y,dino_w,dino_h)
        for obs in obstacles:
            obs_rect = pygame.Rect(obs["x"], obs["y"], obs.get("width",28 if obs["type"]==CACTUS else 35), obs.get("height",35 if obs["type"]==CACTUS else 25))
            if dino_rect.colliderect(obs_rect):
                if not game_over: death_sound()
                game_over=True

        # Pontszám
        score += 1
        if score%100==0: point_sound()

        # Gyorsulás
        obstacle_speed = 6 + score//200

        # Black/White switch
        if score-last_switch >= 700:
            dark_mode = not dark_mode
            last_switch = score

        # Felhők
        for c in clouds:
            c["x"] -= c["speed"]
            if c["x"] < -60:
                c["x"] = WIDTH
                c["y"] = random.randint(20,100)

        # Nap/Hold ciklus
        day = score%2000 < 1000  # 1000 pont = nappal
        if day:
            sun_pos -= 0.1
            draw_sun_moon(sun_pos, True)
        else:
            moon_pos += 0.1
            draw_sun_moon(moon_pos, False)
        if sun_pos < -50: sun_pos = WIDTH+50
        if moon_pos > WIDTH+50: moon_pos = -50

    # Rajzolás
    for c in clouds: draw_cloud(c)
    draw_ground(HEIGHT-20)
    draw_dino(dino_x,dino_y,dino_frame)
    for obs in obstacles:
        if obs["type"]==CACTUS: draw_cactus(obs["x"],obs["y"])
        else: draw_bird(obs["x"],obs["y"],obs["frame"])

    score_text = font.render(f"Score: {score}", True, fg_color)
    screen.blit(score_text,(10,10))

    if game_over:
        text = font.render("GAME OVER - Press R", True, fg_color)
        screen.blit(text,(WIDTH//2-100, HEIGHT//2))

    pygame.display.update()

pygame.quit()
