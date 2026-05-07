import os
from datetime import datetime
from pathlib import Path
import pygame as pg
from concurrent.futures import ThreadPoolExecutor, Future
import cProfile
import chess
import chess.pgn

from config import board
from engine import minimax_caller

SCREEN_SIZE = 1440
TILE_SIZE = 180
SIDE_PANEL_WIDTH = 420
SCREEN_WIDTH = SCREEN_SIZE + SIDE_PANEL_WIDTH
SCREEN_HEIGHT = SCREEN_SIZE
FPS = 60

LIGHT_SQUARE = (174, 164, 139)
DARK_SQUARE = (70, 86, 92)
BOARD_EDGE = (13, 18, 22)
MENU_BG = (11, 14, 18)
PANEL = (22, 29, 35)
PANEL_DARK = (9, 13, 17)
PANEL_SOFT = (31, 40, 48)
TEXT = (236, 231, 218)
MUTED_TEXT = (164, 154, 137)
ACCENT = (228, 183, 84)
GREEN = (86, 178, 126)
RED = (204, 86, 86)

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
    board.reset()


def draw_centered_text(screen, text, font, color, center):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, text_surface.get_rect(center=center))


def draw_button(screen, rect, title, subtitle, hovered):
    bg = (41, 52, 60) if hovered else PANEL
    border = ACCENT if hovered else (74, 91, 102)
    pg.draw.rect(screen, bg, rect, border_radius=8)
    pg.draw.rect(screen, border, rect, width=4, border_radius=8)

    title_font = pg.font.SysFont("arial", 42, bold=True)
    subtitle_font = pg.font.SysFont("arial", 24)
    draw_centered_text(screen, title, title_font, TEXT, (rect.centerx, rect.y + 38))
    draw_centered_text(
        screen, subtitle, subtitle_font, MUTED_TEXT, (rect.centerx, rect.y + 78)
    )


def draw_start_screen(screen, pieces, mouse_pos):
    screen.fill(MENU_BG)
    center_x = SCREEN_WIDTH // 2

    for row in range(SCREEN_HEIGHT // TILE_SIZE):
        for col in range((SCREEN_WIDTH // TILE_SIZE) + 1):
            color = (35, 44, 51) if (row + col) % 2 == 0 else (18, 24, 30)
            pg.draw.rect(
                screen, color, (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            )

    overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
    overlay.fill((5, 8, 12, 110))
    screen.blit(overlay, (0, 0))

    if "king-w.svg" in pieces:
        screen.blit(pieces["king-w.svg"], (center_x - 490, 245))
    if "king-b.svg" in pieces:
        screen.blit(pieces["king-b.svg"], (center_x + 310, 245))

    title_font = pg.font.SysFont("arial", 86, bold=True)
    subtitle_font = pg.font.SysFont("arial", 32)
    draw_centered_text(screen, "Chess Engine", title_font, TEXT, (center_x, 265))
    draw_centered_text(
        screen, "Choose a game mode", subtitle_font, MUTED_TEXT, (center_x, 350)
    )

    buttons = []
    for index, (mode, title, subtitle) in enumerate(MODES):
        rect = pg.Rect(center_x - 290, 470 + index * 145, 580, 100)
        draw_button(screen, rect, title, subtitle, rect.collidepoint(mouse_pos))
        buttons.append((rect, mode))

    hint_font = pg.font.SysFont("arial", 26)
    draw_centered_text(
        screen,
        "Press R after a result to return to this menu.",
        hint_font,
        MUTED_TEXT,
        (center_x, 1015),
    )

    return buttons


def draw_board(
    screen,
    pieces,
    selected_square=None,
    flipped=False,
    dragged_square=None,
):
    pg.draw.rect(screen, BOARD_EDGE, (0, 0, SCREEN_SIZE, SCREEN_SIZE))
    last_move = board.peek() if board.move_stack else None
    legal_targets = legal_targets_for_selected(selected_square, flipped)
    for row in range(8):
        for col in range(8):
            color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
            pg.draw.rect(
                screen, color, (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            )
            draw_square = pg.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if last_move is not None:
                square = square_from_board_coords(row, col, flipped)
                if square in (last_move.from_square, last_move.to_square):
                    highlight = pg.Surface((TILE_SIZE, TILE_SIZE), pg.SRCALPHA)
                    highlight.fill((228, 183, 84, 96))
                    screen.blit(highlight, draw_square.topleft)
            if selected_square == (row, col):
                pg.draw.rect(
                    screen,
                    ACCENT,
                    (
                        col * TILE_SIZE + 6,
                        row * TILE_SIZE + 6,
                        TILE_SIZE - 12,
                        TILE_SIZE - 12,
                    ),
                    width=6,
                    border_radius=4,
                )
            if (row, col) in legal_targets:
                target = board.piece_at(square_from_board_coords(row, col, flipped))
                if target is None:
                    pg.draw.circle(screen, (20, 25, 28, 125), draw_square.center, 20)
                else:
                    pg.draw.rect(
                        screen,
                        (228, 183, 84),
                        draw_square.inflate(-18, -18),
                        width=8,
                        border_radius=8,
                    )
            piece = board.piece_at(square_from_board_coords(row, col, flipped))
            if piece is not None and dragged_square != (row, col):
                image = pieces[piece_image_name(piece)]
                screen.blit(image, (col * TILE_SIZE, row * TILE_SIZE))


def update_caption(mode):
    mode_name = dict((mode_key, title) for mode_key, title, _ in MODES).get(mode, "")
    turn_name = "White" if board.turn == chess.WHITE else "Black"
    pg.display.set_caption(f"Chess Engine - {mode_name} - {turn_name} to move")


def board_square_from_mouse(pos):
    if pos[0] >= SCREEN_SIZE or pos[1] >= SCREEN_SIZE:
        return None
    row = pos[1] // TILE_SIZE
    col = pos[0] // TILE_SIZE
    if 0 <= row < 8 and 0 <= col < 8:
        return (row, col)
    return None


def is_current_turn_piece(piece):
    return piece.color == board.turn


def is_human_turn(mode):
    if mode == "pvp":
        return True
    if mode == "pva":
        return board.turn == chess.WHITE
    if mode == "avp":
        return board.turn == chess.BLACK
    return False


def is_ai_turn(mode):
    if mode == "ava":
        return True
    if mode == "pva":
        return board.turn == chess.BLACK
    if mode == "avp":
        return board.turn == chess.WHITE
    return False


def square_from_board_coords(row, col, flipped=False):
    if flipped:
        return chess.square(7 - col, row)
    return chess.square(col, 7 - row)


def board_coords_from_square(square, flipped=False):
    file_index = chess.square_file(square)
    rank_index = chess.square_rank(square)
    if flipped:
        return rank_index, 7 - file_index
    return 7 - rank_index, file_index


def piece_image_name(piece):
    names = {
        chess.PAWN: "pawn",
        chess.KNIGHT: "knight",
        chess.BISHOP: "bishop",
        chess.ROOK: "rook",
        chess.QUEEN: "queen",
        chess.KING: "king",
    }
    color = "w" if piece.color == chess.WHITE else "b"
    return f"{names[piece.piece_type]}-{color}.svg"


def legal_targets_for_selected(selected_square, flipped=False):
    if selected_square is None:
        return set()

    from_square = square_from_board_coords(*selected_square, flipped)
    return {
        board_coords_from_square(move.to_square, flipped)
        for move in board.legal_moves
        if move.from_square == from_square
    }


def choose_square(click_list, square, flipped=False):
    if square is None:
        return

    chess_square = square_from_board_coords(*square, flipped)
    piece = board.piece_at(chess_square)
    if not click_list:
        if piece is not None and is_current_turn_piece(piece):
            click_list.append(square)
        return

    selected_piece = board.piece_at(square_from_board_coords(*click_list[0], flipped))
    if (
        piece is not None
        and selected_piece is not None
        and selected_piece.color == piece.color
        and is_current_turn_piece(piece)
    ):
        click_list.clear()
        click_list.append(square)
    else:
        click_list.append(square)


def draw_promotion_menu(screen, pieces, options):
    overlay = pg.Surface((SCREEN_SIZE, SCREEN_SIZE), pg.SRCALPHA)
    overlay.fill((5, 8, 12, 190))
    screen.blit(overlay, (0, 0))

    card = pg.Rect(210, 455, 1020, 390)
    pg.draw.rect(screen, PANEL, card, border_radius=8)
    pg.draw.rect(screen, ACCENT, card, width=5, border_radius=8)

    title_font = pg.font.SysFont("arial", 54, bold=True)
    draw_centered_text(screen, "Promote Pawn", title_font, TEXT, (720, 535))

    rects = []
    for index, (image_name, _) in enumerate(options):
        rect = pg.Rect(275 + index * 225, 620, TILE_SIZE, TILE_SIZE)
        pg.draw.rect(screen, PANEL_SOFT, rect, border_radius=8)
        pg.draw.rect(screen, (86, 104, 116), rect, width=4, border_radius=8)
        screen.blit(pieces[image_name], rect.topleft)
        rects.append(rect)

    pg.display.flip()
    return rects


def handle_pawn_promotion(screen, pieces, clock):
    color = "w" if board.turn == chess.WHITE else "b"
    options = [
        (f"queen-{color}.svg", chess.QUEEN),
        (f"rook-{color}.svg", chess.ROOK),
        (f"bishop-{color}.svg", chess.BISHOP),
        (f"knight-{color}.svg", chess.KNIGHT),
    ]
    rects = draw_promotion_menu(screen, pieces, options)
    return wait_for_promotion_choice(options, rects, clock)


def wait_for_promotion_choice(options, rects, clock):
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return None
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return None
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                for index, rect in enumerate(rects):
                    if rect.collidepoint(event.pos):
                        return options[index][1]
        clock.tick(FPS)


def current_game_result():
    outcome = board.outcome(claim_draw=True)
    if outcome is None:
        return None
    if outcome.winner is None:
        return ("draw", None)
    return ("win", outcome.winner)


def draw_game_result(screen, result, saved_path=None):
    result_type, winner = result
    overlay = pg.Surface((SCREEN_SIZE, SCREEN_SIZE), pg.SRCALPHA)
    overlay.fill((5, 8, 12, 190))
    screen.blit(overlay, (0, 0))

    panel = pg.Rect(330, 560, 780, 250)
    pg.draw.rect(screen, PANEL, panel, border_radius=8)
    pg.draw.rect(screen, ACCENT, panel, width=5, border_radius=8)

    title_font = pg.font.SysFont("arial", 58, bold=True)
    body_font = pg.font.SysFont("arial", 28)
    if result_type == "win":
        winner_name = "White" if winner == chess.WHITE else "Black"
        title = f"{winner_name} wins"
    elif result_type == "draw":
        title = "Draw"
    else:
        title = "Game over"

    draw_centered_text(screen, title, title_font, TEXT, (720, 635))
    draw_centered_text(screen, "Press R to return to the menu", body_font, MUTED_TEXT, (720, 700))
    if saved_path is not None:
        draw_centered_text(screen, f"Saved: {saved_path}", body_font, GREEN, (720, 745))


def draw_sidebar(screen, mouse_pos, mode, saved_path, flipped, ai_thinking, elapsed_seconds):
    panel = pg.Rect(SCREEN_SIZE, 0, SIDE_PANEL_WIDTH, SCREEN_HEIGHT)
    pg.draw.rect(screen, (13, 18, 23), panel)
    pg.draw.line(screen, (54, 70, 82), (SCREEN_SIZE, 0), (SCREEN_SIZE, SCREEN_HEIGHT), 3)

    title_font = pg.font.SysFont("arial", 34, bold=True)
    body_font = pg.font.SysFont("arial", 24)
    small_font = pg.font.SysFont("arial", 20)
    tiny_font = pg.font.SysFont("arial", 18)
    draw_centered_text(screen, "Analysis Board", title_font, TEXT, (SCREEN_SIZE + SIDE_PANEL_WIDTH // 2, 46))

    turn_name = "White" if board.turn == chess.WHITE else "Black"
    if board.is_check():
        status = f"{turn_name} in check"
        status_color = RED
    elif ai_thinking:
        status = "AI thinking"
        status_color = ACCENT
    else:
        status = f"{turn_name} to move"
        status_color = TEXT
    mode_name = dict((mode_key, title) for mode_key, title, _ in MODES).get(mode, "")
    screen.blit(body_font.render(mode_name, True, MUTED_TEXT), (SCREEN_SIZE + 30, 88))
    screen.blit(body_font.render(status, True, status_color), (SCREEN_SIZE + 30, 122))

    minutes = elapsed_seconds // 60
    seconds = elapsed_seconds % 60
    stats = [
        ("Clock", f"{minutes:02}:{seconds:02}"),
        ("Ply", str(len(board.move_stack))),
        ("Legal", str(board.legal_moves.count())),
        ("Material", material_balance_text()),
    ]
    for index, (label, value) in enumerate(stats):
        x = SCREEN_SIZE + 30 + (index % 2) * 180
        y = 164 + (index // 2) * 58
        pg.draw.rect(screen, PANEL, (x, y, 158, 44), border_radius=8)
        screen.blit(tiny_font.render(label, True, MUTED_TEXT), (x + 12, y + 5))
        screen.blit(body_font.render(value, True, TEXT), (x + 12, y + 20))

    buttons = {}
    button_specs = [
        ("flip", "Flip Board", 302),
        ("save", "Save PGN", 366),
        ("undo", "Undo Move", 430),
    ]
    for key, label, y in button_specs:
        rect = pg.Rect(SCREEN_SIZE + 30, y, SIDE_PANEL_WIDTH - 60, 48)
        hovered = rect.collidepoint(mouse_pos)
        pg.draw.rect(screen, PANEL_SOFT if hovered else PANEL, rect, border_radius=8)
        pg.draw.rect(screen, ACCENT if hovered else (62, 78, 89), rect, width=2, border_radius=8)
        draw_centered_text(screen, label, body_font, TEXT, rect.center)
        buttons[key] = rect

    flip_label = "Black at bottom" if flipped else "White at bottom"
    screen.blit(small_font.render(flip_label, True, MUTED_TEXT), (SCREEN_SIZE + 30, 492))
    if saved_path is not None:
        screen.blit(tiny_font.render(f"Saved: {saved_path}", True, GREEN), (SCREEN_SIZE + 30, 522))

    pg.draw.line(screen, (62, 78, 89), (SCREEN_SIZE + 30, 568), (SCREEN_WIDTH - 30, 568), 2)
    screen.blit(title_font.render("Moves", True, TEXT), (SCREEN_SIZE + 30, 602))

    moves = move_history_rows()
    visible_rows = moves[-20:]
    y = 654
    for move_number, white_move, black_move in visible_rows:
        number_text = small_font.render(f"{move_number}.", True, MUTED_TEXT)
        white_text = small_font.render(white_move, True, TEXT)
        black_text = small_font.render(black_move, True, TEXT)
        screen.blit(number_text, (SCREEN_SIZE + 30, y))
        screen.blit(white_text, (SCREEN_SIZE + 82, y))
        screen.blit(black_text, (SCREEN_SIZE + 230, y))
        y += 30

    pg.draw.line(screen, (62, 78, 89), (SCREEN_SIZE + 30, 1270), (SCREEN_WIDTH - 30, 1270), 2)
    screen.blit(small_font.render("Shortcuts", True, TEXT), (SCREEN_SIZE + 30, 1300))
    screen.blit(tiny_font.render("F flip  |  S save  |  U undo  |  R menu after game", True, MUTED_TEXT), (SCREEN_SIZE + 30, 1332))
    fen = board.fen()
    clipped_fen = fen[:43] + "..." if len(fen) > 46 else fen
    screen.blit(tiny_font.render("FEN", True, TEXT), (SCREEN_SIZE + 30, 1370))
    screen.blit(tiny_font.render(clipped_fen, True, MUTED_TEXT), (SCREEN_SIZE + 30, 1398))

    return buttons


def move_history_rows():
    replay = chess.Board()
    rows = []
    current_number = 1
    white_move = ""
    for move in board.move_stack:
        san = replay.san(move)
        if replay.turn == chess.WHITE:
            current_number = replay.fullmove_number
            white_move = san
        else:
            rows.append((current_number, white_move, san))
            white_move = ""
        replay.push(move)

    if white_move:
        rows.append((current_number, white_move, ""))
    return rows


def material_balance_text():
    values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0,
    }
    score = 0
    for piece in board.piece_map().values():
        value = values[piece.piece_type]
        score += value if piece.color == chess.WHITE else -value
    if score == 0:
        return "Equal"
    side = "W" if score > 0 else "B"
    return f"{side} +{abs(score)}"


def matching_legal_moves(from_square, to_square):
    return [
        legal_move
        for legal_move in board.legal_moves
        if legal_move.from_square == from_square and legal_move.to_square == to_square
    ]


def apply_human_move(screen, pieces, clock, from_ui_square, to_ui_square, flipped=False):
    from_square = square_from_board_coords(*from_ui_square, flipped)
    to_square = square_from_board_coords(*to_ui_square, flipped)
    moves = matching_legal_moves(from_square, to_square)

    if not moves:
        return None, True

    promotion_moves = [candidate for candidate in moves if candidate.promotion is not None]
    if promotion_moves:
        promotion = handle_pawn_promotion(screen, pieces, clock)
        if promotion is None:
            return None, False
        move_to_play = next(
            candidate for candidate in promotion_moves if candidate.promotion == promotion
        )
    else:
        move_to_play = moves[0]

    board.push(move_to_play)
    return current_game_result(), True


def finish_human_turn(screen, pieces, clock, click_list, flipped=False):
    if len(click_list) != 2:
        return None, True

    from_ui_square, to_ui_square = click_list
    click_list.clear()
    return apply_human_move(screen, pieces, clock, from_ui_square, to_ui_square, flipped)


def finish_ai_turn(position):
    return minimax_caller(position, depth=3)


def save_game_pgn(mode, result=None):
    data_dir = Path(__file__).resolve().parent / "data"
    data_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = data_dir / f"{timestamp}.pgn"

    game = chess.pgn.Game.from_board(board)
    mode_name = dict((mode_key, title) for mode_key, title, _ in MODES).get(mode, mode or "Unknown")
    game.headers["Event"] = mode_name
    game.headers["Site"] = "Chess-Engine"
    game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
    game.headers["Round"] = "-"
    game.headers["White"] = "Human" if mode in ("pvp", "pva") else "AI"
    game.headers["Black"] = "Human" if mode == "pvp" else "AI"
    game.headers["Result"] = board.result(claim_draw=True) if result is not None else "*"

    with path.open("w", encoding="utf-8") as pgn_file:
        print(game, file=pgn_file, end="\n\n")

    return path.relative_to(Path(__file__).resolve().parent)


def draw_thinking_overlay(screen: pg.Surface) -> None:
    """Draw a non-blocking pulsing overlay while the AI is searching."""
    elapsed = pg.time.get_ticks()
    # Pulse alpha between 150 and 210 using a sine-like triangle wave
    cycle = (elapsed % 900) / 900.0  # 0.0 → 1.0 every 900 ms
    alpha = int(150 + 60 * (1 - abs(cycle * 2 - 1)))

    overlay = pg.Surface((SCREEN_SIZE, SCREEN_SIZE), pg.SRCALPHA)
    overlay.fill((5, 8, 12, alpha // 2))
    screen.blit(overlay, (0, 0))

    # Pill-shaped background for the text
    pill = pg.Rect(0, 0, 460, 74)
    pill.center = (SCREEN_SIZE // 2, SCREEN_SIZE // 2)
    pg.draw.rect(screen, (13, 18, 23, 230), pill, border_radius=37)
    pg.draw.rect(screen, ACCENT, pill, width=3, border_radius=37)

    # Animated dots:  "AI Thinking" / "AI Thinking." / "AI Thinking.."
    dots = "." * ((elapsed // 400) % 4)
    font = pg.font.SysFont("arial", 38, bold=True)
    text = font.render(f"AI Thinking{dots}", True, (250, 241, 223))
    screen.blit(text, text.get_rect(center=pill.center))


def draw_dragged_piece(screen, pieces, drag_state, mouse_pos):
    if drag_state is None:
        return

    image = pieces[piece_image_name(drag_state["piece"])]
    rect = image.get_rect(center=mouse_pos)
    shadow = pg.Surface((TILE_SIZE, TILE_SIZE), pg.SRCALPHA)
    pg.draw.ellipse(shadow, (0, 0, 0, 80), shadow.get_rect().inflate(-28, -44))
    screen.blit(shadow, (rect.x + 12, rect.y + 20))
    screen.blit(image, rect.topleft)


def start_drag(square, flipped=False):
    if square is None:
        return None

    chess_square = square_from_board_coords(*square, flipped)
    piece = board.piece_at(chess_square)
    if piece is None or not is_current_turn_piece(piece):
        return None
    return {"square": square, "piece": piece}


def undo_last_move(mode):
    if not board.move_stack:
        return

    board.pop()
    if mode == "pva" and board.move_stack and board.turn == chess.BLACK:
        board.pop()


def main():
    pg.init()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pg.time.Clock()
    pieces = load_pieces()

    running = True
    state = "menu"
    game_mode = None
    game_result = None
    pgn_saved_path = None
    flipped = False
    last_ply_count = 0
    game_started_at = 0
    click_list = []
    sidebar_buttons = {}
    drag_state = None

    # Persistent executor + future for non-blocking AI search
    executor = ThreadPoolExecutor(max_workers=1)
    ai_future: Future[chess.Move | None] | None = None
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
                            pgn_saved_path = None
                            last_ply_count = 0
                            game_started_at = pg.time.get_ticks()
                            ai_future = None
                            drag_state = None
                            game_mode = mode
                            state = "game"

            pg.display.flip()
            clock.tick(FPS)
            continue

        # ------------------------------------------------------------------
        # Event handling (always responsive, even while AI is thinking)
        # ------------------------------------------------------------------
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                elif event.key == pg.K_f:
                    flipped = not flipped
                    click_list.clear()
                    drag_state = None
                elif event.key == pg.K_u and ai_future is None and game_result is None:
                    undo_last_move(game_mode)
                    click_list.clear()
                    drag_state = None
                elif event.key == pg.K_r and game_result is not None:
                    state = "menu"
                    game_mode = None
                    game_result = None
                    pgn_saved_path = None
                    ai_future = None
                    click_list.clear()
                    drag_state = None
                elif event.key == pg.K_s and game_mode is not None:
                    pgn_saved_path = save_game_pgn(game_mode, game_result)
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if sidebar_buttons.get("flip") and sidebar_buttons["flip"].collidepoint(event.pos):
                    flipped = not flipped
                    click_list.clear()
                    drag_state = None
                elif sidebar_buttons.get("save") and sidebar_buttons["save"].collidepoint(event.pos):
                    pgn_saved_path = save_game_pgn(game_mode, game_result)
                elif (
                    sidebar_buttons.get("undo")
                    and sidebar_buttons["undo"].collidepoint(event.pos)
                    and ai_future is None
                    and game_result is None
                ):
                    undo_last_move(game_mode)
                    click_list.clear()
                    drag_state = None
                elif (
                    game_result is None
                    and ai_future is None  # ignore clicks while AI thinks
                ):
                    clicked_square = board_square_from_mouse(event.pos)
                    if click_list:
                        clicked_piece = None
                        if clicked_square is not None:
                            clicked_piece = board.piece_at(
                                square_from_board_coords(*clicked_square, flipped)
                            )
                        if clicked_piece is None or clicked_piece.color != board.turn:
                            choose_square(click_list, clicked_square, flipped)
                        else:
                            drag_state = start_drag(clicked_square, flipped)
                    else:
                        drag_state = start_drag(clicked_square, flipped)
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if drag_state is not None and game_result is None and ai_future is None:
                    release_square = board_square_from_mouse(event.pos)
                    if release_square is None:
                        drag_state = None
                    elif release_square == drag_state["square"]:
                        choose_square(click_list, release_square, flipped)
                        drag_state = None
                    else:
                        result, running = apply_human_move(
                            screen,
                            pieces,
                            clock,
                            drag_state["square"],
                            release_square,
                            flipped,
                        )
                        drag_state = None
                        click_list.clear()
                        if result is not None:
                            game_result = result

        # ------------------------------------------------------------------
        # Draw the board (always, every frame)
        # ------------------------------------------------------------------
        update_caption(game_mode)
        selected_square = drag_state["square"] if drag_state is not None else (click_list[0] if click_list else None)
        draw_board(
            screen,
            pieces,
            selected_square,
            flipped,
            drag_state["square"] if drag_state is not None else None,
        )

        # ------------------------------------------------------------------
        # AI future — collect the calculated move and apply it on the main
        # thread so the search never mutates the live board while drawing.
        # ------------------------------------------------------------------
        if ai_future is not None and ai_future.done():
            try:
                ai_move = ai_future.result()
                if ai_move is not None and ai_move in board.legal_moves:
                    board.push(ai_move)
                game_result = current_game_result()
            except Exception as exc:
                print(f"[main] AI move failed: {exc}")
                game_result = None
            ai_future = None

        # ------------------------------------------------------------------
        # AI turn — kick off background search if needed
        # ------------------------------------------------------------------
        if ai_future is None and game_result is None and is_ai_turn(game_mode):
            ai_future = executor.submit(finish_ai_turn, board.copy(stack=False))

        # Show thinking overlay while AI is working
        if ai_future is not None and not ai_future.done() and game_mode!="ava":
            draw_thinking_overlay(screen)

        # ------------------------------------------------------------------
        # Human turn
        # ------------------------------------------------------------------
        if ai_future is None and game_result is None and is_human_turn(game_mode):
            result, running = finish_human_turn(screen, pieces, clock, click_list, flipped)
            if result is not None:
                game_result = result

        if len(board.move_stack) != last_ply_count:
            pgn_saved_path = None
            last_ply_count = len(board.move_stack)

        if game_result is not None and pgn_saved_path is None:
            pgn_saved_path = save_game_pgn(game_mode, game_result)

        elapsed_seconds = 0
        if game_started_at:
            elapsed_seconds = (pg.time.get_ticks() - game_started_at) // 1000
        sidebar_buttons = draw_sidebar(
            screen,
            mouse_pos,
            game_mode,
            pgn_saved_path,
            flipped,
            ai_future is not None and not ai_future.done(),
            elapsed_seconds,
        )

        draw_dragged_piece(screen, pieces, drag_state, mouse_pos)

        if game_result is not None:
            draw_game_result(screen, game_result, pgn_saved_path)

        pg.display.flip()
        clock.tick(FPS)
    executor.shutdown(wait=False)
    pg.quit()


if __name__ == "__main__":
    main()
