; -----------------------------------------
; Pong 16-bit DOS VGA 13h
; Fut: DOSBox / EMU8086
; Minden pixel 320x200 256 szín
; -----------------------------------------

org 100h         ; .COM kezdés

; ---------- VGA mód 13h ----------
mov ax, 0013h
int 10h

; ---------- változók ----------
; VGA memória: segment 0A000h
VGA_SEG  equ 0A000h

; képernyő méret
SCREEN_WIDTH  equ 320
SCREEN_HEIGHT equ 200

; labda
ballX  db 160
ballY  db 100
ballDX db 1
ballDY db 1

; ütők
paddleLY db 90
paddleRY db 90
PADDLE_HEIGHT equ 20
PADDLE_WIDTH  equ 4

; score
scoreL db 0
scoreR db 0

; színek
BALL_COLOR equ 15
PADDLE_COLOR equ 12
BG_COLOR equ 0

; ---------- kezdő ciklus ----------
jmp main_loop

; ---------- rutinek ----------

; rajzol egy pixel
draw_pixel:
    ; alapon: esik dx=szám, dy=szám, szín=al
    push ax
    push bx
    push es
    mov ax,VGA_SEG
    mov es,ax
    mov al,[bp+6]   ; szín
    mov bx,[bp+4]   ; offset
    mov es:[bx],al
    pop es
    pop bx
    pop ax
    ret

; törlés
clear_screen:
    mov cx, SCREEN_WIDTH*SCREEN_HEIGHT
    mov di,0
    mov ax,VGA_SEG
    mov es,ax
    mov al,BG_COLOR
.clear_loop:
    mov es:[di],al
    inc di
    loop .clear_loop
    ret

; rajzol ütő
draw_paddle:
    ; ax=topY, bx=x pozíció
    ; rajzol egy függőleges téglalapot PADDLE_HEIGHT
    push ax
    push bx
    push cx
    push dx
    mov cx, PADDLE_HEIGHT
    mov dx, bx
.loop_paddle:
    ; offset = (y*320)+x
    mov si, ax
    mov di, si
    imul di, SCREEN_WIDTH
    add di, dx
    mov al,PADDLE_COLOR
    mov es, VGA_SEG
    mov es:[di],al
    inc ax
    loop .loop_paddle
    pop dx
    pop cx
    pop bx
    pop ax
    ret

; rajzol labda
draw_ball:
    ; x=ballX, y=ballY
    mov al,BALL_COLOR
    mov bx,ballX
    mov ax,ballY
    ; egyszerű pont pixel
    ; (egyszerűség kedvéért)
    ; itt demo, részletesebb labda = 2x2 pixel
    ret

; labda mozgás
move_ball:
    ; update ballX/ballY a ballDX/DY alapján
    ; ütközés fal
    ret

; ütő input (DOS int 16h)
read_input:
    ret

; ---------- fő ciklus ----------
main_loop:
    call clear_screen
    call draw_paddle
    call draw_ball
    call move_ball
    call read_input
    jmp main_loop

; ---------- kilépés ----------
exit_game:
    mov ax, 0003h
    int 10h
    ret
