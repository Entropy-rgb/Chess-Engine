import numpy as np
import pygame as pg

from config import board, pieces_enum

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

def promote_pawn(pos:tuple , piece:int):
    board.board[*pos] = piece
    return 0

def call_draw(screen):
    pg.draw.rect(screen,"white",(90, 450, 1260, 540))
    return 0

def call_win(winner, screen):
    pg.draw.rect(screen,"white",(90, 450, 1260, 540))
    pg.
    return 0

def square_in_board(square: tuple) -> int:
    if square[0] < 8 and square[0] >= 0 and square[1] < 8 and square[1] >= 0:
        return 1
    else:
        return 0

def check_for_checkmate():
    if in_check() and not has_legal_moves():
        return board.turn ^ 1
    return None

def stalemate_detect():
    return not in_check() and not has_legal_moves()

def in_check(initial_position=(8,8), final_position=(8,8), valid=0):
    board_copy = board.board.copy()
    if valid:
        if final_position == board.en_passant and (
            board_copy[*initial_position] == 1 or board_copy[*initial_position] == -1
        ):
            if board.turn == 0:
                board_copy[final_position[0] + 1][final_position[1]] = 0
            elif board.turn == 1:
                board_copy[final_position[0] - 1][final_position[1]] = 0
        board_copy[final_position[0]][final_position[1]] = board_copy[initial_position[0]][
            initial_position[1]
        ]
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
    if board.turn == 0:
        for i in range(0, 8):
            for j in range(0, 8):
                if board_copy[i][j] == -6:
                    king_pos = (i, j)
    if board.turn == 1:
        for i in range(0, 8):
            for j in range(0, 8):
                if board_copy[i][j] == 6:
                    king_pos = (i, j)
    if is_attacked(king_pos, board.turn ^ 1, board_copy):
        return 1
    return 0


def is_attacked(square: tuple, attacking_side, only_board = board.board) -> int:
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
                curr = sq_being_analysed
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
                curr = sq_being_analysed
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
                curr = sq_being_analysed
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
                curr = sq_being_analysed
                counter += 1
        return 0
    return 0


def en_passant(initial, final):
    if board.en_passant == (8, 8):
        return 0
    else:
        if (
            board.turn == 0
            and final[0] - initial[0] == -1
            and final == board.en_passant
            and abs(final[1] - initial[1]) == 1
        ):
            return 1
        elif (
            board.turn == 1
            and final[0] - initial[0] == 1
            and final == board.en_passant
            and abs(final[1] - initial[1]) == 1
        ):
            return 1
    return 0


def is_valid_castle(initial, final):
    if board.turn == 1:
        if (
            final == (0, 2)
            and board.board[0][0] == 4
            and board.castling_rights[0] == 1
            and board.rook_moved[0] == 0
            and board.board[0, 1] | board.board[0, 2] | board.board[0, 3] == 0
            and not is_attacked((0,2), board.turn^1)
            and not is_attacked((0,3), board.turn^1)
            and not is_attacked((0,4), board.turn^1)
        ):
            return 3
        if (
            final == (0, 6)
            and board.board[0][7] == 4
            and board.castling_rights[1] == 1
            and board.rook_moved[1] == 0
            and board.board[0, 5] | board.board[0, 6] == 0
            and not is_attacked((0,5), board.turn^1)
            and not is_attacked((0,6), board.turn^1)
            and not is_attacked((0,4), board.turn^1)
        ):
            return 4
    elif board.turn == 0:
        if (
            final == (7, 2)
            and board.board[7][0] == -4
            and board.castling_rights[2] == 1
            and board.rook_moved[2] == 0
            and board.board[7, 1] | board.board[7, 2] | board.board[7, 3] == 0
            and not is_attacked((7,2), board.turn^1)
            and not is_attacked((7,3), board.turn^1)
            and not is_attacked((7,4), board.turn^1)
        ):
            return 5
        if (
            final == (7, 6)
            and board.board[7][7] == -4
            and board.castling_rights[3] == 1
            and board.rook_moved[3] == 0
            and board.board[7, 5] | board.board[7, 6] == 0
            and not is_attacked((7,5), board.turn^1)
            and not is_attacked((7,6), board.turn^1)
            and not is_attacked((7,4), board.turn^1)
        ):
            return 6
    return 0


def is_king_move(initial, final):
    if abs(final[1] - initial[1]) <= 1 and abs(final[0] - initial[0]) <= 1:
        return 1
    return is_valid_castle(initial, final)


def is_bishop_move(initial, final):
    if abs(final[1] - initial[1]) == abs(final[0] - initial[0]):
        a, b = 1, 1
        if final[1] - initial[1] < 0:
            b = -1
        if final[0] - initial[0] < 0:
            a = -1
        for i in range(abs(final[1] - initial[1]) - 1):
            if board.board[initial[0] + ((i + 1) * a)][initial[1] + ((i + 1) * b)] != 0:
                return 0
        return 1
    else:
        return 0


def is_rook_move(initial, final):
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
            if board.board[initial[0] + ((i + 1) * a)][initial[1] + ((i + 1) * b)] != 0:
                return 0
        return 7
    return 0


def is_queen_move(initial, final):
    if is_bishop_move(initial, final) or is_rook_move(initial, final):
        return 1
    else:
        return 0


def is_knight_move(initial, final):
    for move in knight_moves:
        if np.all((np.array(final) - np.array(initial)) == np.array(move)):
            return 1
    return 0


def is_white_pawn_move(initial, final):
    if (
        initial[0] == 6
        and final[0] == 4
        and initial[1] == final[1]
        and board.board[5][initial[1]] == 0
        and board.board[*final] == 0
    ):
        return 2
    elif (
        initial[1] == final[1]
        and final[0] - initial[0] == -1
        and board.board[*final] == 0
    ):
        return 1
    elif (
        abs(final[1] - initial[1]) == 1
        and final[0] - initial[0] == -1
        and board.board[*final] != 0
    ):
        return 1
    elif en_passant(initial, final):
        return 1
    else:
        return 0


def is_black_pawn_move(initial, final):
    if (
        initial[0] == 1
        and final[0] == 3
        and initial[1] == final[1]
        and board.board[2][initial[1]] == 0
        and board.board[*final] == 0
    ):
        return 2
    elif (
        initial[1] == final[1]
        and final[0] - initial[0] == 1
        and board.board[*final] == 0
    ):
        return 1
    elif (
        abs(final[1] - initial[1]) == 1
        and final[0] - initial[0] == 1
        and board.board[*final] != 0
    ):
        return 1
    elif en_passant(initial, final):
        return 1
    else:
        return 0


def is_valid_move(initial, final):
    if board.board[*final] * board.board[*initial] > 0:
        return 0
    if board.board[*initial] == pieces_enum.WHITE_PAWN:
        return is_white_pawn_move(initial, final)
    elif board.board[*initial] == pieces_enum.BLACK_PAWN:
        return is_black_pawn_move(initial, final)
    elif (
        board.board[*initial] == pieces_enum.BLACK_KNIGHT
        or board.board[*initial] == pieces_enum.WHITE_KNIGHT
    ):
        return is_knight_move(initial, final)
    elif (
        board.board[*initial] == pieces_enum.BLACK_BISHOP
        or board.board[*initial] == pieces_enum.WHITE_BISHOP
    ):
        return is_bishop_move(initial, final)
    elif (
        board.board[*initial] == pieces_enum.BLACK_ROOK
        or board.board[*initial] == pieces_enum.WHITE_ROOK
    ):
        return is_rook_move(initial, final)
    elif (
        board.board[*initial] == pieces_enum.BLACK_QUEEN
        or board.board[*initial] == pieces_enum.WHITE_QUEEN
    ):
        return is_queen_move(initial, final)
    elif (
        board.board[*initial] == pieces_enum.BLACK_KING
        or board.board[*initial] == pieces_enum.WHITE_KING
    ):
        return is_king_move(initial, final)
    else:
        return 0


def has_legal_moves():
    for initial_row in range(8):
        for initial_col in range(8):
            piece = board.board[initial_row][initial_col]
            if piece == 0:
                continue
            if board.turn == 0 and piece > 0:
                continue
            if board.turn == 1 and piece < 0:
                continue

            initial = (initial_row, initial_col)
            for final_row in range(8):
                for final_col in range(8):
                    final = (final_row, final_col)
                    if initial == final:
                        continue
                    valid = is_valid_move(initial, final)
                    if (
                        valid
                        and not in_check(initial, final, valid)
                        and abs(board.board[final_row][final_col]) != 6
                    ):
                        return True
    return False


def move(initial_position, final_position, screen):
    checkmate = check_for_checkmate()
    if checkmate is not None:
        return call_win(checkmate,screen)
    if board.half_move_clock == 50 or stalemate_detect():
        return call_draw(screen)
    if initial_position == final_position:
        return None
    if board.board[*initial_position] < 0 and board.turn == 1:
        return None
    elif board.board[*initial_position] > 0 and board.turn == 0:
        return None
    valid = is_valid_move(initial_position, final_position)
    if valid:
        if in_check(initial_position, final_position, valid) or abs(board.board[*final_position])==6:
            return None
        if valid == 7:  # a rook move , so we need to modify the castling rights
            if initial_position == (0, 0) and board.rook_moved[0] == 0:
                board.rook_moved[0] = 1
                board.castling_rights[0] = 0
            elif initial_position == (0, 7) and board.rook_moved[1] == 0:
                board.rook_moved[1] = 1
                board.castling_rights[1] = 0
            elif initial_position == (7, 0) and board.rook_moved[2] == 0:
                board.rook_moved[2] = 1
                board.castling_rights[2] = 0
            elif initial_position == (7, 7) and board.rook_moved[3] == 0:
                board.rook_moved[3] = 1
                board.castling_rights[3] = 0
        if valid == 2:
            if board.turn == 1:
                board.en_passant = (2, initial_position[1])
            elif board.turn == 0:
                board.en_passant = (5, initial_position[1])
        if board.board[*initial_position] == 6 or board.board[*initial_position] == -6:
            if board.turn == 1 and (
                board.castling_rights[0] or board.castling_rights[1]
            ):
                board.castling_rights[0] = 0
                board.castling_rights[1] = 0
            elif board.turn == 0 and (
                board.castling_rights[2] or board.castling_rights[3]
            ):
                board.castling_rights[2] = 0
                board.castling_rights[3] = 0
        if final_position == board.en_passant and (
            board.board[*initial_position] == 1 or board.board[*initial_position] == -1
        ):
            if board.turn == 0:
                board.board[final_position[0] + 1][final_position[1]] = 0
            elif board.turn == 1:
                board.board[final_position[0] - 1][final_position[1]] = 0
        board.turn = board.turn ^ 1
        board.board[final_position[0]][final_position[1]] = board.board[
            initial_position[0]
        ][initial_position[1]]
        board.board[initial_position[0]][initial_position[1]] = 0
        if valid != 2 and board.en_passant != (8, 8):
            board.en_passant = (8, 8)
        if valid >= 3:
            if valid == 3:
                board.board[0][0] = 0
                board.board[0][3] = 4
            elif valid == 4:
                board.board[0][7] = 0
                board.board[0][5] = 4
            elif valid == 5:
                board.board[7][0] = 0
                board.board[7][3] = -4
            elif valid == 6:
                board.board[7][7] = 0
                board.board[7][5] = -4
        board.half_move_clock+=1
        return 1
    else:
        return None
