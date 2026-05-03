from config import board, Board
from move_generator import move_generator
from game import move, promote_pawn
from config import pieces_enum
import numpy as np
from pprint import pprint
DEPTH = 4
count = 0
capture = 0
en_pasant = 0
castle = 0
promotion = 0

CAPTURE_FLAGS = {1, 3, 12, 14, 16, 18}
PROMOTION_FLAGS = {11, 12, 13, 14, 15, 16, 17, 18}

test_brd = [
    [0]*8,
    [0,0,1,0,0,0,0,0],
    [0,0,0,1,0,0,0,0],
    [-6,-1,0,0,0,0,0,4],
    [0,-4,0,0,0,1,0,6],
    [0]*8,
    [0,0,0,0,-1,0,-1,0],
    [0]*8,
]

test_board = Board(np.array(test_brd), 0, (8, 8), [0,0,0,0], 0, [1,1,1,1])


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
            continue
        if depth == 1:
            if pos.flag in CAPTURE_FLAGS:
                capture += 1
            if pos.flag == 4:
                castle += 1
            if pos.flag == 3:
                en_pasant += 1
            if pos.flag in PROMOTION_FLAGS:
                promotion += 1
        test_move_generator(cpy, depth - 1)


test_move_generator(board, DEPTH)
print(f"{count=} {en_pasant=} {castle=} {promotion=} {capture=}")
