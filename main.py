import os

import numpy as np
import pygame as pg

from config import board, piece_map, starting_board
from engine import make_engine_move
from game import (call_draw, call_win, check_for_checkmate, move, promote_pawn,
                  stalemate_detect)

SCREEN_SIZE = 1440
TILE_SIZE = 180
FPS = 60

LIGHT_SQUARE = (234, 181, 99)
DARK_SQUARE = (84, 42, 0)
MENU_BG = (35, 29, 24)
PANEL = (242, 235, 222)
PANEL_DARK = (70, 48, 32)
TEXT = (42, 30, 22)

MODES = [
    ("pvp", "Play vs Player", "Two local players"),
    ("pva", "Play vs AI", "AI hook for Phase 2"),
    ("ava", "AI vs AI", "Simulation hook for Phase 2"),
]


def load_pieces():
    pieces = {}
    image_dir = os.path.join(os.path.dirname(__file__), "assets", "images")
    for piece in os.listdir(image_dir):
        image = pg.image.load(os.path.join(image_dir, piece))
        pieces[piece] = pg.transform.scale(image, (TILE_SIZE, TILE_SIZE))
    return pieces


def reset_game():
    board.board = np.array(starting_board)
    board.turn = 0
    board.en_passant = (8, 8)
    board.castling_rights = [1, 1, 1, 1]
    board.half_move_clock = 0
    board.rook_moved = [0, 0, 0, 0]


def draw_centered_text(screen, text, font, color, center):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, text_surface.get_rect(center=center))


def draw_button(screen, rect, title, subtitle, hovered):
    bg = (255, 249, 236) if hovered else PANEL
    border = (126, 84, 45) if hovered else PANEL_DARK
    pg.draw.rect(screen, bg, rect, border_radius=8)
    pg.draw.rect(screen, border, rect, width=4, border_radius=8)

    title_font = pg.font.SysFont("arial", 42, bold=True)
    subtitle_font = pg.font.SysFont("arial", 24)
    draw_centered_text(screen, title, title_font, TEXT, (rect.centerx, rect.y + 38))
    draw_centered_text(
        screen, subtitle, subtitle_font, (92, 67, 45), (rect.centerx, rect.y + 78)
    )


def draw_start_screen(screen, pieces, mouse_pos):
    screen.fill(MENU_BG)

    for row in range(8):
        for col in range(8):
            color = (64, 48, 35) if (row + col) % 2 == 0 else (40, 31, 25)
            pg.draw.rect(
                screen, color, (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            )

    overlay = pg.Surface((SCREEN_SIZE, SCREEN_SIZE), pg.SRCALPHA)
    overlay.fill((20, 16, 12, 120))
    screen.blit(overlay, (0, 0))

    if "king-w.svg" in pieces:
        screen.blit(pieces["king-w.svg"], (230, 245))
    if "king-b.svg" in pieces:
        screen.blit(pieces["king-b.svg"], (1030, 245))

    title_font = pg.font.SysFont("arial", 86, bold=True)
    subtitle_font = pg.font.SysFont("arial", 32)
    draw_centered_text(screen, "Chess Engine", title_font, (250, 241, 223), (720, 265))
    draw_centered_text(
        screen, "Choose a game mode", subtitle_font, (220, 203, 180), (720, 350)
    )

    buttons = []
    for index, (mode, title, subtitle) in enumerate(MODES):
        rect = pg.Rect(430, 500 + index * 145, 580, 105)
        draw_button(screen, rect, title, subtitle, rect.collidepoint(mouse_pos))
        buttons.append((rect, mode))

    hint_font = pg.font.SysFont("arial", 26)
    draw_centered_text(
        screen,
        "AI options open the board now; engine moves come in Phase 2.",
        hint_font,
        (206, 190, 169),
        (720, 1015),
    )

    return buttons


def draw_board(screen, pieces, selected_square=None):
    for row in range(8):
        for col in range(8):
            color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
            pg.draw.rect(
                screen, color, (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            )
            if selected_square == (row, col):
                pg.draw.rect(
                    screen,
                    (250, 236, 92),
                    (
                        col * TILE_SIZE + 6,
                        row * TILE_SIZE + 6,
                        TILE_SIZE - 12,
                        TILE_SIZE - 12,
                    ),
                    width=6,
                    border_radius=4,
                )
            if board.board[row][col]:
                image = pieces[piece_map[board.board[row][col]]]
                screen.blit(image, (col * TILE_SIZE, row * TILE_SIZE))


def update_caption(mode):
    mode_name = dict((mode_key, title) for mode_key, title, _ in MODES).get(mode, "")
    turn_name = "White" if board.turn == 0 else "Black"
    pg.display.set_caption(f"Chess Engine - {mode_name} - {turn_name} to move")


def board_square_from_mouse(pos):
    row = pos[1] // TILE_SIZE
    col = pos[0] // TILE_SIZE
    if 0 <= row < 8 and 0 <= col < 8:
        return (row, col)
    return None


def choose_square(click_list, square):
    if square is None:
        return

    piece = board.board[*square]
    if not click_list:
        if piece != 0:
            click_list.append(square)
        return

    selected_piece = board.board[*click_list[0]]
    if piece != 0 and selected_piece * piece > 0:
        click_list.clear()
        click_list.append(square)
    else:
        click_list.append(square)


def draw_promotion_menu(screen, pieces, options):
    overlay = pg.Surface((SCREEN_SIZE, SCREEN_SIZE), pg.SRCALPHA)
    overlay.fill((20, 18, 16, 170))
    screen.blit(overlay, (0, 0))

    card = pg.Rect(210, 455, 1020, 390)
    pg.draw.rect(screen, (244, 238, 226), card, border_radius=8)
    pg.draw.rect(screen, (76, 48, 25), card, width=6, border_radius=8)

    title_font = pg.font.SysFont("arial", 54, bold=True)
    draw_centered_text(screen, "Promote Pawn", title_font, TEXT, (720, 535))

    rects = []
    for index, (image_name, _) in enumerate(options):
        rect = pg.Rect(275 + index * 225, 620, TILE_SIZE, TILE_SIZE)
        pg.draw.rect(screen, (214, 204, 188), rect, border_radius=8)
        pg.draw.rect(screen, (92, 67, 45), rect, width=4, border_radius=8)
        screen.blit(pieces[image_name], rect.topleft)
        rects.append(rect)

    pg.display.flip()
    return rects


def handle_pawn_promotion(screen, pieces, clock):
    for col in range(8):
        if board.board[0][col] == -1:
            options = [
                ("queen-w.svg", -5),
                ("rook-w.svg", -4),
                ("bishop-w.svg", -3),
                ("knight-w.svg", -2),
            ]
            rects = draw_promotion_menu(screen, pieces, options)
            return wait_for_promotion_choice((0, col), options, rects, clock)

        if board.board[7][col] == 1:
            options = [
                ("queen-b.svg", 5),
                ("rook-b.svg", 4),
                ("bishop-b.svg", 3),
                ("knight-b.svg", 2),
            ]
            rects = draw_promotion_menu(screen, pieces, options)
            return wait_for_promotion_choice((7, col), options, rects, clock)

    return True


def wait_for_promotion_choice(pos, options, rects, clock):
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return False
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                for index, rect in enumerate(rects):
                    if rect.collidepoint(event.pos):
                        promote_pawn(pos, options[index][1])
                        return True
        clock.tick(FPS)


def current_game_result():
    winner = check_for_checkmate()
    if winner is not None:
        return ("win", winner)
    if board.half_move_clock == 50 or stalemate_detect():
        return ("draw", None)
    return None


def draw_game_result(screen, result):
    result_type, winner = result
    if result_type == "win":
        call_win(winner, screen)
    elif result_type == "draw":
        call_draw(screen)


def main():
    pg.init()
    screen = pg.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
    clock = pg.time.Clock()
    pieces = load_pieces()

    running = True
    state = "menu"
    game_mode = None
    game_result = None
    click_list = []

    while running:
        mouse_pos = pg.mouse.get_pos()

        if state == "menu":
            buttons = draw_start_screen(screen, pieces, mouse_pos)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    running = False
                elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    for rect, mode in buttons:
                        if rect.collidepoint(event.pos):
                            reset_game()
                            click_list.clear()
                            game_result = None
                            game_mode = mode
                            state = "game"

            pg.display.flip()
            clock.tick(FPS)
            continue

        update_caption(game_mode)
        draw_board(screen, pieces, click_list[0] if click_list else None)

        if game_result is not None:
            draw_game_result(screen, game_result)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                elif event.key == pg.K_r and game_result is not None:
                    state = "menu"
                    game_mode = None
                    game_result = None
                    click_list.clear()
            elif (
                event.type == pg.MOUSEBUTTONDOWN
                and event.button == 1
                and game_result is None
            ):
                choose_square(click_list, board_square_from_mouse(event.pos))

        if game_mode == "pvp":
            if len(click_list) == 2 and game_result is None:
                move_result = move(*click_list, screen)
                click_list.clear()
                if move_result == 1:
                    running = handle_pawn_promotion(screen, pieces, clock)
                    if running:
                        game_result = current_game_result()
                elif move_result in ("win", "draw"):
                    game_result = current_game_result()
        elif game_mode == "pva":
            if board.turn == 1:
                make_engine_move()
            else:
                if len(click_list) == 2 and game_result is None:
                    move_result = move(*click_list, screen)
                    click_list.clear()
                    if move_result == 1:
                        running = handle_pawn_promotion(screen, pieces, clock)
                        if running:
                            game_result = current_game_result()
                    elif move_result in ("win", "draw"):
                        game_result = current_game_result()
        elif game_mode == "ava":
            make_engine_move()
            pg.time.wait(500)
        pg.display.flip()
        clock.tick(FPS)

    pg.quit()


if __name__ == "__main__":
    main()
