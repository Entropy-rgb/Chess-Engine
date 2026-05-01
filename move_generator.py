from config import board, Board
import numpy as np
# from game import is_valid_move

class move():
    def __init__(self, initial:tuple , final:tuple , piece:int, flag:int, capture:int):
        self.initial = initial
        self.final = final
        self.piece = piece
        self.flag = flag
        self.capture = capture

def move_generator(board:Board.board, turn=board.turn)->list:
    valid_moves = ["demo_move"]
    copy_board = board.copy()
    if turn == 0:
        for i in copy_board.ravel():
            ...
        # for pawns
        # for knights
        # for rooks
        # for bishops 
        # for queen
        # for king
        ...
    if turn == 1:
        # for pawns
        # for knights
        # for rooks
        # for bishops 
        # for queen
        # for king
        ...
    return valid_moves