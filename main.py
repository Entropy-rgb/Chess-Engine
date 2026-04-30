import os

import pygame as pg

from config import board, piece_map
from game import move

pieces = {}
click_list = []

piece_list = tuple(os.walk("./assets/images/"))[-1][-1]
for piece in piece_list:
    pieces[piece] = pg.transform.scale(
        pg.image.load("./assets/images/" + piece), (180, 180)
    )

pg.init()
screen = pg.display.set_mode((1440, 1440))
clock = pg.time.Clock()
running = True
HEIGHT = 180
WIDTH = 180
colour = (234, 181, 99)

while running:
    screen.fill("purple")
    for i in range(0, 8):
        for j in range(0, 8):
            if (i + j) % 2 == 0:
                colour = (234, 181, 99)
            else:
                colour = (84, 42, 0)
            pg.draw.rect(screen, colour, (j * 180, i * 180, WIDTH, HEIGHT))
            if board.board[i][j]:
                image = pieces[piece_map[board.board[i][j]]]
                screen.blit(image, (j * 180, i * 180))
    coordinates = ()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.MOUSEBUTTONDOWN:
            coordinates = event.pos
            coordinates = (coordinates[1] // 180, coordinates[0] // 180)
            if not click_list and board.board[coordinates[0]][coordinates[1]] != 0:
                click_list.append(coordinates)
            elif click_list and board.board[coordinates[0]][coordinates[1]] == 0:
                click_list.append(coordinates)
            elif (
                click_list
                and board.board[click_list[0][0]][click_list[0][1]]
                * board.board[coordinates[0]][coordinates[1]]
                <= 0
            ):
                click_list.append(coordinates)
            else:
                click_list = []
                click_list.append(coordinates)
    if len(click_list) == 2:
        move(*click_list)
        click_list.pop()
        click_list.pop()
    for x in range(0, 8):
        if board.board[0][x] == -1:
            queen = pieces["queen-w.svg"]
            rook = pieces["rook-w.svg"]
            bishop = pieces["bishop-w.svg"]
            knight = pieces["knight-w.svg"]
            pg.draw.rect(screen, "white", (90, 450, 1260, 540))
            pg.draw.rect(screen, (180, 180, 180), (165, 630, 180, 180))
            screen.blit(queen, (165, 630))
            pg.draw.rect(screen, (180, 180, 180), (475, 630, 180, 180))
            screen.blit(rook, (475, 630))
            pg.draw.rect(screen, (180, 180, 180), (785, 630, 180, 180))
            screen.blit(bishop, (785, 630))
            pg.draw.rect(screen, (180, 180, 180), (1095, 630, 180, 180))
            screen.blit(knight, (1095, 630))
            pg.display.flip()
            pawn_promotion = 1
            while pawn_promotion:
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        running = False
                        break
                    if event.type == pg.MOUSEBUTTONDOWN:
                        coordinates = event.pos
                        if (
                            coordinates[0] > 165
                            and coordinates[0] < 165 + 180
                            and coordinates[1] > 630
                            and coordinates[1] < 630 + 180
                        ):
                            board.board[0][x] = -5
                            pawn_promotion = 0
                            break
                        elif (
                            coordinates[0] > 475
                            and coordinates[0] < 475 + 180
                            and coordinates[1] > 630
                            and coordinates[1] < 630 + 180
                        ):
                            board.board[0][x] = -4
                            pawn_promotion = 0
                            break
                        elif (
                            coordinates[0] > 785
                            and coordinates[0] < 785 + 180
                            and coordinates[1] > 630
                            and coordinates[1] < 630 + 180
                        ):
                            board.board[0][x] = -3
                            pawn_promotion = 0
                            break
                        elif (
                            coordinates[0] > 1095
                            and coordinates[0] < 1095 + 180
                            and coordinates[1] > 630
                            and coordinates[1] < 630 + 180
                        ):
                            board.board[0][x] = -2
                            pawn_promotion = 0
                            break
        elif board.board[7][x] == 1:
            queen = pieces["queen-b.svg"]
            rook = pieces["rook-b.svg"]
            bishop = pieces["bishop-b.svg"]
            knight = pieces["knight-b.svg"]
            pg.draw.rect(screen, "white", (90, 450, 1260, 540))
            pg.draw.rect(screen, (180, 180, 180), (165, 630, 180, 180))
            screen.blit(queen, (165, 630))
            pg.draw.rect(screen, (180, 180, 180), (475, 630, 180, 180))
            screen.blit(rook, (475, 630))
            pg.draw.rect(screen, (180, 180, 180), (785, 630, 180, 180))
            screen.blit(bishop, (785, 630))
            pg.draw.rect(screen, (180, 180, 180), (1095, 630, 180, 180))
            screen.blit(knight, (1095, 630))
            pg.display.flip()
            pawn_promotion = 1
            while pawn_promotion:
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        running = False
                        break
                    if event.type == pg.MOUSEBUTTONDOWN:
                        coordinates = event.pos
                        if (
                            coordinates[0] > 165
                            and coordinates[0] < 165 + 180
                            and coordinates[1] > 630
                            and coordinates[1] < 630 + 180
                        ):
                            board.board[7][x] = 5
                            pawn_promotion = 0
                            break
                        elif (
                            coordinates[0] > 475
                            and coordinates[0] < 475 + 180
                            and coordinates[1] > 630
                            and coordinates[1] < 630 + 180
                        ):
                            board.board[7][x] = 4
                            pawn_promotion = 0
                            break
                        elif (
                            coordinates[0] > 785
                            and coordinates[0] < 785 + 180
                            and coordinates[1] > 630
                            and coordinates[1] < 630 + 180
                        ):
                            board.board[7][x] = 3
                            pawn_promotion = 0
                            break
                        elif (
                            coordinates[0] > 1095
                            and coordinates[0] < 1095 + 180
                            and coordinates[1] > 630
                            and coordinates[1] < 630 + 180
                        ):
                            board.board[7][x] = 2
                            pawn_promotion = 0
                            break
    pg.display.flip()
    clock.tick(60)

pg.quit()
