import numpy as np
import pygame as pg

from config import Board, board, pieces_enum

knight_moves = [
    (2, 1),
    (1, 2),
    (-2, -1),
    (-1, -2),
    (2, -1),
    (1, -2),
    (-2, 1),
    (-1, 2),
]

possible_directions = [
    (1, 1),
    (-1, -1),
    (1, -1),
    (-1, 1),
    (0, 1),
    (1, 0),
    (-0, -1),
    (-1, -0),
]


def promote_pawn(
    pos: tuple, piece: int | np.int64, inp_board: Board = board
) -> int | np.int64:
    inp_board.board[*pos] = piece
    return 0


def _draw_result_card(screen: pg.Surface, title, subtitle) -> None:
    if not pg.font.get_init():
        pg.font.init()

    overlay = pg.Surface(screen.get_size(), pg.SRCALPHA)
    overlay.fill((20, 18, 16, 170))
    screen.blit(overlay, (0, 0))

    card = pg.Rect(300, 460, 840, 360)
    pg.draw.rect(screen, (244, 238, 226), card, border_radius=8)
    pg.draw.rect(screen, (76, 48, 25), card, width=6, border_radius=8)

    title_font = pg.font.SysFont("arial", 72, bold=True)
    subtitle_font = pg.font.SysFont("arial", 34)
    hint_font = pg.font.SysFont("arial", 28)

    title_surface = title_font.render(title, True, (48, 32, 20))
    subtitle_surface = subtitle_font.render(subtitle, True, (68, 48, 34))
    hint_surface = hint_font.render(
        "Press R for menu or Esc to quit", True, (98, 72, 48)
    )

    screen.blit(title_surface, title_surface.get_rect(center=(720, 565)))
    screen.blit(subtitle_surface, subtitle_surface.get_rect(center=(720, 655)))
    screen.blit(hint_surface, hint_surface.get_rect(center=(720, 735)))


def call_draw(screen: pg.Surface) -> str:
    _draw_result_card(screen, "Draw", "The game ended without a winner.")
    return "draw"


def call_win(winner: int | np.int64, screen: pg.Surface) -> str:
    winner_name = "White" if winner == 0 else "Black"
    _draw_result_card(screen, "Checkmate", f"{winner_name} wins.")
    return "win"


def square_in_board(square: tuple) -> int | np.int64:
    if 8 > square[0] >= 0 and 0 <= square[1] < 8:
        return 1
    else:
        return 0


def check_for_checkmate(inp_board=board) -> None | int | np.int64:
    if in_check(inp_board=inp_board) and not has_legal_moves():
        return inp_board.turn ^ 1
    return None


def stalemate_detect(inp_board=board) -> int | np.int64:
    return not in_check(inp_board=inp_board) and not has_legal_moves(
        inp_board=inp_board
    )


def in_check(
    initial_position: tuple = (8, 8),
    final_position: tuple = (8, 8),
    valid: int | np.int64 = 0,
    inp_board: Board = board,
) -> int | np.int64:
    board_copy = inp_board.board.copy()
    if valid:
        if final_position == inp_board.en_passant and (
            board_copy[*initial_position] == 1 or board_copy[*initial_position] == -1
        ):
            if inp_board.turn == 0:
                board_copy[final_position[0] + 1][final_position[1]] = 0
            elif inp_board.turn == 1:
                board_copy[final_position[0] - 1][final_position[1]] = 0
        board_copy[final_position[0]][final_position[1]] = board_copy[
            initial_position[0]
        ][initial_position[1]]
        board_copy[initial_position[0]][initial_position[1]] = 0
        if valid >= 3:
            if valid == 3:
                board_copy[0][0] = 0
                board_copy[0][3] = 4
            elif valid == 4:
                board_copy[0][7] = 0
                board_copy[0][5] = 4
            elif valid == 5:
                board_copy[7][0] = 0
                board_copy[7][3] = -4
            elif valid == 6:
                board_copy[7][7] = 0
                board_copy[7][5] = -4
    king_pos = (0, 0)
    if inp_board.turn == 0:
        for i in range(0, 8):
            for j in range(0, 8):
                if board_copy[i][j] == -6:
                    king_pos = (i, j)
    if inp_board.turn == 1:
        for i in range(0, 8):
            for j in range(0, 8):
                if board_copy[i][j] == 6:
                    king_pos = (i, j)
    if is_attacked(king_pos, inp_board.turn ^ 1, board_copy):
        return 1
    return 0


def is_attacked(
    square: tuple,
    attacking_side: int | np.int64,
    only_board: np.typing.NDArray = board.board,
) -> int | np.int64:
    if attacking_side == 0:
        # check for pawn attacks
        if (
            square_in_board((square[0] + 1, square[1] + 1))
            and only_board[square[0] + 1][square[1] + 1] == -1
        ) or (
            square_in_board((square[0] + 1, square[1] - 1))
            and only_board[square[0] + 1][square[1] - 1] == -1
        ):
            return 1
        # check for king attacks
        for i in possible_directions:
            if (
                square_in_board((square[0] + i[0], square[1] + i[1]))
                and only_board[square[0] + i[0]][square[1] + i[1]] == -6
            ):
                return 1
        # check for knight attacks
        for i in knight_moves:
            if (
                square_in_board((square[0] + i[0], square[1] + i[1]))
                and only_board[square[0] + i[0]][square[1] + i[1]] == -2
            ):
                return 1
        # check for rook and queen
        for i in possible_directions[4:]:
            curr = 0
            counter = 1
            while curr == 0 and square_in_board(
                (square[0] + (counter * i[0]), square[1] + (counter * i[1]))
            ):
                sq_being_analysed = only_board[square[0] + (counter * i[0])][
                    square[1] + (counter * i[1])
                ]
                if sq_being_analysed == -4 or sq_being_analysed == -5:
                    return 1
                curr = int(sq_being_analysed)
                counter += 1
        # check for bishop and queen
        for i in possible_directions[:4]:
            curr = 0
            counter = 1
            while curr == 0 and square_in_board(
                (square[0] + (counter * i[0]), square[1] + (counter * i[1]))
            ):
                sq_being_analysed = only_board[square[0] + (counter * i[0])][
                    square[1] + (counter * i[1])
                ]
                if sq_being_analysed == -3 or sq_being_analysed == -5:
                    return 1
                curr = int(sq_being_analysed)
                counter += 1
        return 0
    elif attacking_side == 1:
        # check for pawn attacks
        if (
            square_in_board((square[0] - 1, square[1] + 1))
            and only_board[square[0] - 1][square[1] + 1] == 1
        ) or (
            square_in_board((square[0] - 1, square[1] - 1))
            and only_board[square[0] - 1][square[1] - 1] == 1
        ):
            return 1
        # check for king attacks
        for i in possible_directions:
            if (
                square_in_board((square[0] + i[0], square[1] + i[1]))
                and only_board[square[0] + i[0]][square[1] + i[1]] == 6
            ):
                return 1
        # check for knight attacks
        for i in knight_moves:
            if (
                square_in_board((square[0] + i[0], square[1] + i[1]))
                and only_board[square[0] + i[0]][square[1] + i[1]] == 2
            ):
                return 1
        # check for rook and queen
        for i in possible_directions[4:]:
            curr = 0
            counter = 1
            while curr == 0 and square_in_board(
                (square[0] + (counter * i[0]), square[1] + (counter * i[1]))
            ):
                sq_being_analysed = only_board[square[0] + (counter * i[0])][
                    square[1] + (counter * i[1])
                ]
                if sq_being_analysed == 4 or sq_being_analysed == 5:
                    return 1
                curr = int(sq_being_analysed)
                counter += 1
        # check for bishop and queen
        for i in possible_directions[0:4]:
            curr = 0
            counter = 1
            while curr == 0 and square_in_board(
                (square[0] + (counter * i[0]), square[1] + (counter * i[1]))
            ):
                sq_being_analysed = only_board[square[0] + (counter * i[0])][
                    square[1] + (counter * i[1])
                ]
                if sq_being_analysed == 3 or sq_being_analysed == 5:
                    return 1
                curr = int(sq_being_analysed)
                counter += 1
        return 0
    return 0


def en_passant(
    initial: tuple, final: tuple, inp_board: Board = board
) -> int | np.int64:
    if inp_board.en_passant == (8, 8):
        return 0
    else:
        if (
            inp_board.turn == 0
            and final[0] - initial[0] == -1
            and final == inp_board.en_passant
            and abs(final[1] - initial[1]) == 1
        ):
            return 1
        elif (
            inp_board.turn == 1
            and final[0] - initial[0] == 1
            and final == inp_board.en_passant
            and abs(final[1] - initial[1]) == 1
        ):
            return 1
    return 0


def is_valid_castle(
    initial: tuple, final: tuple, inp_board: Board = board
) -> int | np.int64:
    if inp_board.turn == 1:
        if (
            final == (0, 2)
            and inp_board.board[0][0] == 4
            and inp_board.castling_rights[0] == 1
            and inp_board.rook_moved[0] == 0
            and inp_board.board[0, 1] | inp_board.board[0, 2] | inp_board.board[0, 3]
            == 0
            and not is_attacked((0, 2), inp_board.turn ^ 1, inp_board.board)
            and not is_attacked((0, 3), inp_board.turn ^ 1, inp_board.board)
            and not is_attacked((0, 4), inp_board.turn ^ 1, inp_board.board)
        ):
            return 3
        if (
            final == (0, 6)
            and inp_board.board[0][7] == 4
            and inp_board.castling_rights[1] == 1
            and inp_board.rook_moved[1] == 0
            and inp_board.board[0, 5] | inp_board.board[0, 6] == 0
            and not is_attacked((0, 5), inp_board.turn ^ 1, inp_board.board)
            and not is_attacked((0, 6), inp_board.turn ^ 1, inp_board.board)
            and not is_attacked((0, 4), inp_board.turn ^ 1, inp_board.board)
        ):
            return 4
    elif inp_board.turn == 0:
        if (
            final == (7, 2)
            and inp_board.board[7][0] == -4
            and inp_board.castling_rights[2] == 1
            and inp_board.rook_moved[2] == 0
            and inp_board.board[7, 1] | inp_board.board[7, 2] | inp_board.board[7, 3]
            == 0
            and not is_attacked((7, 2), inp_board.turn ^ 1, inp_board.board)
            and not is_attacked((7, 3), inp_board.turn ^ 1, inp_board.board)
            and not is_attacked((7, 4), inp_board.turn ^ 1, inp_board.board)
        ):
            return 5
        if (
            final == (7, 6)
            and inp_board.board[7][7] == -4
            and inp_board.castling_rights[3] == 1
            and inp_board.rook_moved[3] == 0
            and inp_board.board[7, 5] | inp_board.board[7, 6] == 0
            and not is_attacked((7, 5), inp_board.turn ^ 1, inp_board.board)
            and not is_attacked((7, 6), inp_board.turn ^ 1, inp_board.board)
            and not is_attacked((7, 4), inp_board.turn ^ 1, inp_board.board)
        ):
            return 6
    return 0


def is_king_move(
    initial: tuple, final: tuple, inp_board: Board = board
) -> int | np.int64:
    if abs(final[1] - initial[1]) <= 1 and abs(final[0] - initial[0]) <= 1:
        return 1
    return is_valid_castle(initial, final, inp_board=inp_board)


def is_bishop_move(
    initial: tuple, final: tuple, inp_board: Board = board
) -> int | np.int64:
    if abs(final[1] - initial[1]) == abs(final[0] - initial[0]):
        a, b = 1, 1
        if final[1] - initial[1] < 0:
            b = -1
        if final[0] - initial[0] < 0:
            a = -1
        for i in range(abs(final[1] - initial[1]) - 1):
            if (
                inp_board.board[initial[0] + ((i + 1) * a)][initial[1] + ((i + 1) * b)]
                != 0
            ):
                return 0
        return 1
    else:
        return 0


def is_rook_move(
    initial: tuple, final: tuple, inp_board: Board = board
) -> int | np.int64:
    if final[1] - initial[1] == 0 or final[0] - initial[0] == 0:
        a, b = 1, 1
        if final[1] - initial[1] == 0:
            b = 0
        if final[0] - initial[0] == 0:
            a = 0
        if final[0] < initial[0]:
            a = -1
        if final[1] < initial[1]:
            b = -1
        for i in range(max(abs(final[1] - initial[1]), abs(final[0] - initial[0])) - 1):
            if (
                inp_board.board[initial[0] + ((i + 1) * a)][initial[1] + ((i + 1) * b)]
                != 0
            ):
                return 0
        return 7
    return 0


def is_queen_move(
    initial: tuple, final: tuple, inp_board: Board = board
) -> int | np.int64:
    if is_bishop_move(initial, final, inp_board) or is_rook_move(
        initial, final, inp_board
    ):
        return 1
    else:
        return 0


def is_knight_move(initial: tuple, final: tuple) -> int | np.int64:
    for move in knight_moves:
        if np.all((np.array(final) - np.array(initial)) == np.array(move)):
            return 1
    return 0


def is_white_pawn_move(
    initial: tuple, final: tuple, inp_board: Board = board
) -> int | np.int64:
    if (
        initial[0] == 6
        and final[0] == 4
        and initial[1] == final[1]
        and inp_board.board[5][initial[1]] == 0
        and inp_board.board[*final] == 0
    ):
        return 2
    elif (
        initial[1] == final[1]
        and final[0] - initial[0] == -1
        and inp_board.board[*final] == 0
    ):
        return 1
    elif (
        abs(final[1] - initial[1]) == 1
        and final[0] - initial[0] == -1
        and inp_board.board[*final] != 0
    ):
        return 1
    elif en_passant(initial, final, inp_board):
        return 1
    else:
        return 0


def is_black_pawn_move(
    initial: tuple, final: tuple, inp_board: Board = board
) -> int | np.int64:
    if (
        initial[0] == 1
        and final[0] == 3
        and initial[1] == final[1]
        and inp_board.board[2][initial[1]] == 0
        and inp_board.board[*final] == 0
    ):
        return 2
    elif (
        initial[1] == final[1]
        and final[0] - initial[0] == 1
        and inp_board.board[*final] == 0
    ):
        return 1
    elif (
        abs(final[1] - initial[1]) == 1
        and final[0] - initial[0] == 1
        and inp_board.board[*final] != 0
    ):
        return 1
    elif en_passant(initial, final, inp_board):
        return 1
    else:
        return 0


def is_valid_move(
    initial: tuple, final: tuple, inp_board: Board = board
) -> int | np.int64:
    if inp_board.board[*final] * inp_board.board[*initial] > 0:
        return 0
    if inp_board.board[*initial] == pieces_enum.WHITE_PAWN:
        return is_white_pawn_move(initial, final, inp_board)
    elif inp_board.board[*initial] == pieces_enum.BLACK_PAWN:
        return is_black_pawn_move(initial, final, inp_board)
    elif (
        inp_board.board[*initial] == pieces_enum.BLACK_KNIGHT
        or inp_board.board[*initial] == pieces_enum.WHITE_KNIGHT
    ):
        return is_knight_move(initial, final)
    elif (
        inp_board.board[*initial] == pieces_enum.BLACK_BISHOP
        or inp_board.board[*initial] == pieces_enum.WHITE_BISHOP
    ):
        return is_bishop_move(initial, final, inp_board)
    elif (
        inp_board.board[*initial] == pieces_enum.BLACK_ROOK
        or inp_board.board[*initial] == pieces_enum.WHITE_ROOK
    ):
        return is_rook_move(initial, final, inp_board)
    elif (
        inp_board.board[*initial] == pieces_enum.BLACK_QUEEN
        or inp_board.board[*initial] == pieces_enum.WHITE_QUEEN
    ):
        return is_queen_move(initial, final, inp_board)
    elif (
        inp_board.board[*initial] == pieces_enum.BLACK_KING
        or inp_board.board[*initial] == pieces_enum.WHITE_KING
    ):
        return is_king_move(initial, final, inp_board)
    else:
        return 0


def has_legal_moves(inp_board: Board = board) -> bool:
    for initial_row in range(8):
        for initial_col in range(8):
            piece = inp_board.board[initial_row][initial_col]
            if piece == 0:
                continue
            if inp_board.turn == 0 and piece > 0:
                continue
            if inp_board.turn == 1 and piece < 0:
                continue

            initial = (initial_row, initial_col)
            for final_row in range(8):
                for final_col in range(8):
                    final = (final_row, final_col)
                    if initial == final:
                        continue
                    valid = is_valid_move(initial, final, inp_board)
                    if (
                        valid
                        and not in_check(initial, final, valid)
                        and abs(inp_board.board[final_row][final_col]) != 6
                    ):
                        return True
    return False


def move(
    initial_position: tuple, final_position: tuple, screen, inp_board: Board = board
) -> None | int | np.int64 | str:
    checkmate = check_for_checkmate()
    if checkmate is not None:
        return call_win(checkmate, screen)
    if inp_board.half_move_clock == 50 or stalemate_detect(inp_board=inp_board):
        return call_draw(screen)
    if initial_position == final_position:
        return None
    if inp_board.board[*initial_position] < 0 and inp_board.turn == 1:
        return None
    elif inp_board.board[*initial_position] > 0 and inp_board.turn == 0:
        return None
    valid = is_valid_move(initial_position, final_position, inp_board)
    if valid:
        if (
            in_check(initial_position, final_position, valid, inp_board)
            or abs(inp_board.board[*final_position]) == 6
        ):
            return None
        if valid == 7:  # a rook move , so we need to modify the castling rights
            if initial_position == (0, 0) and inp_board.rook_moved[0] == 0:
                inp_board.rook_moved[0] = 1
                inp_board.castling_rights[0] = 0
            elif initial_position == (0, 7) and inp_board.rook_moved[1] == 0:
                inp_board.rook_moved[1] = 1
                inp_board.castling_rights[1] = 0
            elif initial_position == (7, 0) and inp_board.rook_moved[2] == 0:
                inp_board.rook_moved[2] = 1
                inp_board.castling_rights[2] = 0
            elif initial_position == (7, 7) and inp_board.rook_moved[3] == 0:
                inp_board.rook_moved[3] = 1
                inp_board.castling_rights[3] = 0
        if valid == 2:
            if inp_board.turn == 1:
                inp_board.en_passant = (2, initial_position[1])
            elif inp_board.turn == 0:
                inp_board.en_passant = (5, initial_position[1])
        if (
            inp_board.board[*initial_position] == 6
            or inp_board.board[*initial_position] == -6
        ):
            if inp_board.turn == 1 and (
                inp_board.castling_rights[0] or inp_board.castling_rights[1]
            ):
                inp_board.castling_rights[0] = 0
                inp_board.castling_rights[1] = 0
            elif inp_board.turn == 0 and (
                inp_board.castling_rights[2] or inp_board.castling_rights[3]
            ):
                inp_board.castling_rights[2] = 0
                inp_board.castling_rights[3] = 0
        if final_position == inp_board.en_passant and (
            inp_board.board[*initial_position] == 1
            or inp_board.board[*initial_position] == -1
        ):
            if inp_board.turn == 0:
                inp_board.board[final_position[0] + 1][final_position[1]] = 0
            elif inp_board.turn == 1:
                inp_board.board[final_position[0] - 1][final_position[1]] = 0
        inp_board.turn = inp_board.turn ^ 1
        inp_board.board[final_position[0]][final_position[1]] = inp_board.board[
            initial_position[0]
        ][initial_position[1]]
        inp_board.board[initial_position[0]][initial_position[1]] = 0
        if valid != 2 and inp_board.en_passant != (8, 8):
            inp_board.en_passant = (8, 8)
        if valid >= 3:
            if valid == 3:
                inp_board.board[0][0] = 0
                inp_board.board[0][3] = 4
            elif valid == 4:
                inp_board.board[0][7] = 0
                inp_board.board[0][5] = 4
            elif valid == 5:
                inp_board.board[7][0] = 0
                inp_board.board[7][3] = -4
            elif valid == 6:
                inp_board.board[7][7] = 0
                inp_board.board[7][5] = -4
        inp_board.half_move_clock += 1
        return 1
    else:
        return None
