from config import board, Board
from move_generator import move_generator
from game import move, promote_pawn
from config import pieces_enum
import numpy as np

count = 0
capture = 0
en_pasant = 0
castle = 0
promotion = 0

test_brd = [
    [pieces_enum.BLACK_ROOK, 0, 0, 0, 6, 0, 0, 4],
    [1, 0, 1, 1, 5, 1, 3, 0],
    [3, 2, 0, 0, 1, 2, 1, 0],
    [0, 0, 0, -1, -2, 0, 0, 0],
    [0, 1, 0, 0, -1, 0, 0, 0],
    [0, 0, -2, 0, 0, -5, 0, 1],
    [-1, -1, -1, -3, -3, -1, -1, -1],
    [-4, 0, 0, 0, -6, 0, 0, -4],
]

test_board = Board(np.array(test_brd), 0, (8, 8), [1, 1, 1, 1], 0, [0, 0, 0, 0])


def test_move_generator(board=board, depth=1):
    global count,castle,promotion,en_pasant,capture
    if depth == 0:
        count += 1
        return
    moves = move_generator(board)
    for pos in moves:

        cpy = Board(
            board.board.copy(),
            board.turn,
            board.en_passant,
            board.castling_rights.copy(),
            board.half_move_clock,
            board.rook_moved.copy(),
        )
        done = move(pos.initial, pos.final, None, cpy)
        if done is None:
            if pos.flag == 4:
                castle+=1
            continue
        if pos.flag == 1:
            capture+=1
        if pos.flag == 4:
            castle+=1
        if pos.flag == 3:
            en_pasant+=1
        if pos.flag in [11,12,13,14,15,16,17,18]:
            promotion+=1
        test_move_generator(cpy, depth - 1)


test_move_generator(test_board, 1)
print(f"{count=} {en_pasant=} {castle=} {promotion=} {capture=}")
