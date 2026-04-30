import numpy as np

from config import board, pieces_enum


# BLACK_PAWN = 1
# BLACK_KNIGHT = 2
# BLACK_BISHOP = 3
# BLACK_ROOK = 4
# BLACK_QUEEN = 5
# BLACK_KING = 6
# WHITE_PAWN = -1
# WHITE_KNIGHT = -2
# WHITE_BISHOP = -3
# WHITE_ROOK = -4
# WHITE_QUEEN = -5
# WHITE_KING = -6
def en_passant(initial, final):  # FIXME : implement the real logic for en passant
    return 0

def is_knight_move(initial, final):
    knight_moves = [(2,1),(1,2),(-2,-1),(-1,-2),(2,-1),(1,-2),(-2,1),(1,-2)]
    for move in knight_moves:
        if np.all((np.array(final)-np.array(initial) )==np.array(move)):
            return 1
    return 0


def is_white_pawn_move(initial, final):
    if initial[0] == 6 and final[0] == 4 and initial[1] == final[1]:
        return 1
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
    if initial[0] == 1 and final[0] == 3 and initial[1] == final[1]:
        return 1
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
    if board.board[*initial] == -1:
        return is_white_pawn_move(initial, final)
    elif board.board[*initial] == 1:
        return is_black_pawn_move(initial, final)
    elif board.board[*initial] == pieces_enum.BLACK_KNIGHT or board.board[*initial] == pieces_enum.WHITE_KNIGHT:
        return is_knight_move(initial, final)


def move(
    initial_position, final_position
):  # FIXME: here , i need to implement if move is valid and then only allow it
    if board.board[*initial_position] < 0 and board.turn == 1:
        return
    elif board.board[*initial_position] > 0 and board.turn == 0:
        return

    if is_valid_move(initial_position, final_position):
        board.board[final_position[0]][final_position[1]] = board.board[
            initial_position[0]
        ][initial_position[1]]
        board.board[initial_position[0]][initial_position[1]] = 0
        board.turn = board.turn ^ 1
    else:
        return
