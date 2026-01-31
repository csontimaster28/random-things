import pygame, sys
from modules import user_system, pack_opening, squad_builder, market

pygame.init()
WIDTH, HEIGHT = 900, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FUT Placeholder")
FONT = pygame.font.SysFont("arial",20)
BIG_FONT = pygame.font.SysFont("arial",30)
GRAY=(200,200,200)
WHITE=(255,255,255)
GOLD=(255,215,0)

CURRENT_USER = None

def draw_button(text,x,y,w,h,color):
    pygame.draw.rect(WIN,color,(x,y,w,h))
    label = FONT.render(text,True,(0,0,0))
    WIN.blit(label,(x+w//2 - label.get_width()//2, y+h//2 - label.get_height()//2))

def login_screen():
    global CURRENT_USER
    username = ""
    password = ""
    input_active = "username"
    clock = pygame.time.Clock()
    running = True
    while running:
        WIN.fill(GRAY)
        WIN.blit(BIG_FONT.render("Login / Register",True,(0,0,0)),(WIDTH//2 - 100,50))
        WIN.blit(FONT.render(f"Username: {username}",True,(0,0,0)),(100,150))
        WIN.blit(FONT.render(f"Password: {'*'*len(password)}",True,(0,0,0)),(100,200))
        draw_button("Login",100,250,150,40,GOLD)
        draw_button("Register",300,250,150,40,WHITE)
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_TAB:
                    input_active = "password" if input_active=="username" else "username"
                elif event.key==pygame.K_BACKSPACE:
                    if input_active=="username":
                        username=username[:-1]
                    else:
                        password=password[:-1]
                elif event.key==pygame.K_RETURN:
                    pass
                else:
                    if input_active=="username":
                        username+=event.unicode
                    else:
                        password+=event.unicode
            if event.type==pygame.MOUSEBUTTONDOWN:
                mx,my = pygame.mouse.get_pos()
                if 100<mx<250 and 250<my<290:
                    success,_ = user_system.login(username,password)
                    if success:
                        CURRENT_USER=username
                        running=False
                if 300<mx<450 and 250<my<290:
                    success,_ = user_system.register(username,password)
                    if success:
                        CURRENT_USER=username
                        running=False
        pygame.display.update()
        clock.tick(60)

def main_menu():
    clock = pygame.time.Clock()
    running=True
    while running:
        WIN.fill(GRAY)
        WIN.blit(BIG_FONT.render(f"Welcome {CURRENT_USER}",True,(0,0,0)),(50,20))
        WIN.blit(FONT.render(f"Coins: {user_system.load_users()[CURRENT_USER]['coins']}",True,(0,0,0)),(50,60))
        draw_button("Buy Pack",50,120,200,50,GOLD)
        draw_button("Squad Builder",50,200,200,50,WHITE)
        draw_button("Market",50,280,200,50,WHITE)
        draw_button("Exit",50,360,200,50,WHITE)
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
            if event.type==pygame.MOUSEBUTTONDOWN:
                mx,my=pygame.mouse.get_pos()
                if 50<mx<250:
                    if 120<my<170:
                        pack_opening.buy_pack(CURRENT_USER, WIN)
                    elif 200<my<250:
                        # Itt kell a UI-t indítani:
                        squad_builder.squad_builder_ui(WIN, CURRENT_USER)
                    elif 280<my<330:
                        pass # market UI majd ide
                    elif 360<my<410:
                        running=False
        pygame.display.update()
        clock.tick(60)

if __name__=="__main__":
    login_screen()
    main_menu()
    pygame.quit()
    sys.exit()
