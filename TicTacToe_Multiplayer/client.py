import pygame
from pygame import mixer
from grid import Grid
import os

# Intialize the pygame
pygame.init()

os.environ['SDL VIDEO WINDOW POS'] = '850,100'

surface = pygame.display.set_mode((600, 800))
# Title and Icon
pygame.display.set_caption('Tic Tac Toe Client')
icon = pygame.image.load('ufo.png')
pygame.display.set_icon(icon)

# Background
background = pygame.image.load('bg1.jpg')

# Background sound
mixer.init()
mixer.music.load('background.wav')
mixer.music.play(-1)

#new timer
clock = pygame.time.Clock()
time_limit = 30
counter, text = 30, '30'.rjust(3)
pygame.time.set_timer(pygame.USEREVENT, 1000)

# Game over Text
over_font = pygame.font.Font('freesansbold.ttf', 64)
font = pygame.font.Font('freesansbold.ttf', 32)

def game_over_text():
    if player == 'o' and turn:
        over_text = over_font.render("YOU LOST!! ", True, (255, 0, 0))
        surface.blit(over_text, (105, 170))
    else:
        over_text = over_font.render("YOU WON!! ", True, (255, 0, 0))
        surface.blit(over_text, (115, 170))

    sbar = font.render("Press SPCACEBAR to reload.", True, (0, 255, 0))
    surface.blit(sbar, (80, 375))

# create a separate thread to send and receive data from the client
import threading
def create_thread(target):
    thread = threading.Thread(target = target)
    thread.daemon = True
    thread.start()

# creating a TCP socket for the server
import socket

HOST = '127.0.0.1'
PORT = 65432

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # ipv4 and tcp respectively
sock.connect((HOST, PORT))

def receive_data():
    global turn
    while True:
        data = sock.recv(1024).decode() # receive data from the client, it is a blocking method
        data = data.split('-')  # the format of the data after splitting is: ['x', 'y', 'yourturn', 'playing']
        x, y = int(data[0]), int(data[1])
        if data[2] == 'yourturn':
            turn = True
        if data[3] == 'False':
            grid.game_over = True
        if grid.get_cell_value(x,y) == 0:
            grid.set_cell_value(x,y,'X')
        print(data)

# run the blocking functions in a separate thread
create_thread(receive_data)

grid = Grid()

running = True
player = "o"
turn = False
playing = 'True'

while running:
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and not grid.game_over:
            # print(pygame.mouse.get_pressed())
            if pygame.mouse.get_pressed()[0]:
                if turn and not grid.game_over:
                    pos = pygame.mouse.get_pos()
                    cellX, cellY = pos[0] // 200, pos[1] // 200
                    grid.get_mouse( cellX,cellY,player)
                    if grid.game_over:
                        playing = 'False'
                        game_over_text()

                    send_data='{}-{}-{}-{}'.format(cellX,cellY,'yourturn',playing).encode()
                    sock.send(send_data)
                    turn = False

                counter = 30
                # if grid.switch_player:
                #     if player == "X":
                #         player = "o"
                #     else:
                #         player = "X"

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and grid.game_over:
                grid.clear_grid()
                grid.game_over = False
                playing = 'True'
            elif event.key == pygame.K_ESCAPE:
                running = False
        if event.type == pygame.QUIT:
            running = False

        if player == 'o' and turn:
            if event.type == pygame.USEREVENT:
                counter -= 1
                text = str(counter).rjust(3) if counter > 0 else 'Time Up! YOU LOST'
            # if e.type == pygame.QUIT: break
            else:
                surface.blit(font.render(text, True, (0, 255, 0)), (32, 700))
                print(text, end=" ")
                pygame.display.flip()
                clock.tick(60)
                continue
            if counter < 0:
                print("Game over!")
                running = False

    surface.fill((0, 0, 0))

    # background image
    surface.blit(background, (0, 0))
    if grid.game_over:
        game_over_text()

    grid.draw(surface)

    pygame.display.flip()
