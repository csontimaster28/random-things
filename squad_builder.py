import pygame, os, json
from modules import user_system

CARD_WIDTH, CARD_HEIGHT = 100,150
PLAYER_SPACING = 10

SQUADS_FILE = "data/squads.json"
PLAYERS_FILE = "data/players.json"

FORMATION_POSITIONS = [
    "GK",
    "LB", "CB1", "CB2", "RB",
    "LM", "CM1", "CM2", "RM",
    "ST1", "ST2"
]

# --- JSON load/save ---
def load_players():
    if not os.path.exists(PLAYERS_FILE):
        return []
    with open(PLAYERS_FILE,"r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def load_squad(username):
    if not os.path.exists(SQUADS_FILE) or os.path.getsize(SQUADS_FILE)==0:
        with open(SQUADS_FILE,"w") as f:
            json.dump({},f)
        return {}
    with open(SQUADS_FILE,"r") as f:
        try:
            squads = json.load(f)
        except json.JSONDecodeError:
            squads = {}
    return squads.get(username, {})

def save_squad(username, squad):
    if not os.path.exists(SQUADS_FILE) or os.path.getsize(SQUADS_FILE)==0:
        squads = {}
    else:
        with open(SQUADS_FILE,"r") as f:
            try:
                squads = json.load(f)
            except json.JSONDecodeError:
                squads = {}
    squads[username] = squad
    with open(SQUADS_FILE,"w") as f:
        json.dump(squads,f, indent=4)

# --- Quick Sell ---
def quick_sell(username, player):
    coin_value = player.get("rating",50)*10
    users = user_system.load_users()
    users[username]["coins"] += coin_value
    user_system.save_users(users)

    # Remove from squad if exists
    squad = load_squad(username)
    for k,v in squad.items():
        if isinstance(v, list):
            squad[k] = [p for p in v if p!=player]
        elif v==player:
            squad[k]=None
    save_squad(username, squad)

# --- Squad Builder UI ---
def squad_builder_ui(WIN, username):
    pygame.font.init()
    FONT = pygame.font.SysFont("arial",18)
    BIG_FONT = pygame.font.SysFont("arial",25)
    clock = pygame.time.Clock()
    running=True

    players = load_players()
    squad = load_squad(username)

    # Formáció setup
    formation = {pos: squad.get(pos,None) for pos in FORMATION_POSITIONS}
    formation["BENCH"] = squad.get("BENCH",[None]*7)

    # Load images
    for p in players:
        try:
            surf = pygame.image.load(p["img"]).convert_alpha()
            p["surface"] = pygame.transform.scale(surf,(CARD_WIDTH,CARD_HEIGHT))
        except:
            p["surface"] = None

    scroll_y = 0
    max_scroll = max(0,len(players)* (CARD_HEIGHT+PLAYER_SPACING) - WIN.get_height() + 150)

    selected_player = None  # a játékos kijelölve a mezőbe rakáshoz

    while running:
        WIN.fill((200,200,200))

        # Title
        WIN.blit(BIG_FONT.render("Squad Builder",True,(0,0,0)),(WIN.get_width()//2-80,10))

        # Coin display
        users = user_system.load_users()
        coins = users.get(username,{}).get("coins",0)
        WIN.blit(FONT.render(f"Coins: {coins}",True,(0,0,0)),(WIN.get_width()-150,20))

        # --- Player List ---
        y_offset = 80 - scroll_y
        for i,p in enumerate(players):
            x, y = 20, y_offset + i*(CARD_HEIGHT+PLAYER_SPACING)
            rect = pygame.Rect(x,y,CARD_WIDTH,CARD_HEIGHT)
            color = (255,255,255)
            pygame.draw.rect(WIN,color,rect)
            if p.get("surface"):
                WIN.blit(p["surface"],(x,y))
            WIN.blit(FONT.render(p.get("name","Unknown"),True,(0,0,0)),(x+5,y+CARD_HEIGHT-40))
            WIN.blit(FONT.render(f"{p.get('rating',0)} {p.get('tier','bronze').capitalize()}",True,(0,0,0)),(x+5,y+CARD_HEIGHT-20))

            # Quick Sell gomb
            sell_rect = pygame.Rect(x+CARD_WIDTH-25,y,25,25)
            pygame.draw.rect(WIN,(255,0,0),sell_rect)
            WIN.blit(FONT.render("X",True,(255,255,255)),(x+CARD_WIDTH-20,y))

            p["rect"]=rect
            p["sell_rect"]=sell_rect

        # --- Formation Grid ---
        start_x = 200
        start_y = 100
        grid_w = 120
        grid_h = 160
        spacing_x = 10
        spacing_y = 10

        rects_list = []  # (rect, pos_name)
        for idx,pos in enumerate(FORMATION_POSITIONS):
            col = idx % 4
            row = idx // 4
            x = start_x + col*(grid_w + spacing_x)
            y = start_y + row*(grid_h + spacing_y)
            rect = pygame.Rect(x, y, grid_w, grid_h)
            pygame.draw.rect(WIN, (180,180,180), rect)
            player = formation.get(pos)
            if player and player.get("surface"):
                WIN.blit(player["surface"], (x, y))
                WIN.blit(FONT.render(player.get("name",""), True, (0,0,0)), (x, y+grid_h-20))
            pygame.draw.rect(WIN, (0,0,0), rect, 2)
            rects_list.append((rect,pos))

        # --- Bench ---
        bench_x = start_x
        bench_y = start_y + 4*(grid_h+spacing_y)
        bench_rects_list = []  # (rect, index)
        for i in range(7):
            rect = pygame.Rect(bench_x+i*(grid_w+spacing_x), bench_y, grid_w, grid_h)
            pygame.draw.rect(WIN,(150,150,150),rect)
            player = formation["BENCH"][i]
            if player and player.get("surface"):
                WIN.blit(player["surface"],(rect.x,rect.y))
                WIN.blit(FONT.render(player.get("name",""),True,(0,0,0)),(rect.x,rect.y+grid_h-20))
            pygame.draw.rect(WIN,(0,0,0),rect,2)
            bench_rects_list.append((rect,i))

        # --- Save Button ---
        save_rect = pygame.Rect(WIN.get_width()-200, WIN.get_height()-70, 150,50)
        pygame.draw.rect(WIN,(255,215,0),save_rect)
        WIN.blit(FONT.render("Save Squad",True,(0,0,0)),(save_rect.x+15,save_rect.y+15))

        # --- Events ---
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
            if event.type==pygame.MOUSEBUTTONDOWN:
                mx,my = pygame.mouse.get_pos()
                # Scroll
                if event.button==4: scroll_y = max(0, scroll_y-40)
                if event.button==5: scroll_y = min(max_scroll, scroll_y+40)

                # Quick Sell
                for p in players:
                    if p["sell_rect"].collidepoint(mx,my):
                        quick_sell(username,p)
                        # Remove from formation if exists
                        for k,v in formation.items():
                            if isinstance(v,list):
                                formation[k] = [x for x in v if x!=p]
                            elif v==p:
                                formation[k]=None

                # Select player from list
                for p in players:
                    if p["rect"].collidepoint(mx,my):
                        selected_player = p

                # Place player in formation
                for rect,pos in rects_list:
                    if rect.collidepoint(mx,my) and selected_player:
                        formation[pos] = selected_player
                        selected_player=None

                # Place player on bench
                for rect,idx in bench_rects_list:
                    if rect.collidepoint(mx,my) and selected_player:
                        formation["BENCH"][idx] = selected_player
                        selected_player=None

                # Save squad
                if save_rect.collidepoint(mx,my):
                    save_squad(username,formation)

        pygame.display.update()
        clock.tick(60)
