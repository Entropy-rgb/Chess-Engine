import numpy as np

from config import board, pieces_enum

def en_passant(initial, final):  # FIXME : implement the real logic for en passant
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


def is_king_move(initial, final):
    if abs(final[1] - initial[1]) <= 1 and abs(final[0] - initial[0]) <= 1:
        return 1
    else:
        return 0


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
        return 1
    return 0


def is_queen_move(initial, final):
    if is_bishop_move(initial, final) or is_rook_move(initial, final):
        return 1
    else:
        return 0


def is_knight_move(initial, final):
    knight_moves = [
        (2, 1),
        (1, 2),
        (-2, -1),
        (-1, -2),
        (2, -1),
        (1, -2),
        (-2, 1),
        (1, -2),
    ]
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
    ):
        board.en_passant = (5, initial[1])
        return 2
    elif initial[1] == final[1] and final[0] - initial[0] == -1:
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
    ):
        board.en_passant = (2, initial[1])
        return 2
    elif initial[1] == final[1] and final[0] - initial[0] == 1:
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


def is_valid_move(initial, final):  # FIXME
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


def move(
    initial_position, final_position
):  # FIXME: here , i need to implement if move is valid and then only allow it
    if initial_position == final_position:
        return
    if board.board[*initial_position] < 0 and board.turn == 1:
        return
    elif board.board[*initial_position] > 0 and board.turn == 0:
        return
    valid = is_valid_move(initial_position, final_position)
    if valid:
        board.board[final_position[0]][final_position[1]] = board.board[
            initial_position[0]
        ][initial_position[1]]
        board.board[initial_position[0]][initial_position[1]] = 0
        if final_position == board.en_passant:
            if board.turn == 0:
                board.board[final_position[0] + 1][final_position[1]] = 0
            elif board.turn == 1:
                board.board[final_position[0] - 1][final_position[1]] = 0
        board.turn = board.turn ^ 1
        if valid != 2 and board.en_passant != (8, 8):
            board.en_passant = (8, 8)
    else:
        return
