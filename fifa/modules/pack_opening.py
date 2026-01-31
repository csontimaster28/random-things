import pygame, random, json, os

def load_players():
    with open("data/players.json","r") as f:
        players = json.load(f)
    for p in players:
        try:
            surf = pygame.image.load(p["img"]).convert_alpha()
            p["surface"] = pygame.transform.scale(surf,(100,60))
        except:
            p["surface"] = None
    return players

try:
    OPEN_SOUND = pygame.mixer.Sound("assets/pack_open.wav")
except:
    OPEN_SOUND = None

def buy_pack(username, WIN, pack_size=5, pack_price=200):
    from modules.user_system import spend_coins, add_coins
    if not spend_coins(username, pack_price):
        return False,"Not enough coins!"
    players = load_players()
    selected = random.sample(players, pack_size)
    
    if OPEN_SOUND:
        OPEN_SOUND.play()
    
    WIDTH, HEIGHT = WIN.get_size()
    WIN.fill((200,200,200))
    title = pygame.font.SysFont("arial",30).render("Opening Pack...",True,(0,0,0))
    WIN.blit(title,(WIDTH//2 - title.get_width()//2,20))
    pygame.display.update()
    pygame.time.delay(1000)
    
    card_width, card_height = 120,160
    start_x = 50
    start_y = 150
    padding = 30
    font = pygame.font.SysFont("arial",20)
    
    for i,p in enumerate(selected):
        x = start_x + i*(card_width + padding)
        y = start_y
        for alpha in range(0,256,25):
            WIN.fill((200,200,200))
            WIN.blit(title,(WIDTH//2 - title.get_width()//2,20))
            s = pygame.Surface((card_width,card_height))
            s.set_alpha(alpha)
            s.fill((255,255,255))
            WIN.blit(s,(x,y))
            if p["surface"]:
                WIN.blit(p["surface"],(x+10,y+40))
            else:
                pygame.draw.rect(WIN,(0,0,0),(x+10,y+40,card_width-20,60))
            name_text = font.render(p["name"], True, (0,0,0))
            rating_text = font.render(f"Rating: {p['rating']}", True, (0,0,0))
            pos_text = font.render(p["position"], True, (0,0,0))
            WIN.blit(name_text,(x+card_width//2 - name_text.get_width()//2, y+110))
            WIN.blit(rating_text,(x+card_width//2 - rating_text.get_width()//2, y+130))
            WIN.blit(pos_text,(x+card_width//2 - pos_text.get_width()//2, y+150))
            # Rare glow
            if p.get("rarity")=="rare":
                glow = pygame.Surface((card_width,card_height),pygame.SRCALPHA)
                pygame.draw.rect(glow,(255,223,0,alpha),(0,0,card_width,card_height),border_radius=8)
                WIN.blit(glow,(x,y))
            pygame.display.update()
            pygame.time.delay(50)
    
    pygame.time.delay(1000)
    return True, selected
