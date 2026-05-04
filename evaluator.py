import numpy as np

from config import Board
from game import check_for_checkmate
from pst import find_pst


def evals(board: Board) -> int:
    board_arr = board.board
    vals = [0, 900, 500, 300, 300, 100, 0, -100, -300, -300, -500, -900, 0]
    eval_sum = 0
    end_score = endgame_score(board)
    for x in range(8):
        for y in range(8):
            eval_sum += vals[board_arr[x][y] + 6]
            piece_mid_pst = find_pst(board_arr[x][y], 0)
            piece_end_pst = find_pst(board_arr[x][y], 1)
            if (
                piece_mid_pst.size > 0
                and piece_end_pst.size > 0
                and board_arr[x][y] > 0
            ):
                eval_sum -= (
                    ((256 - end_score) * piece_mid_pst[x][y])
                    + (end_score * (piece_end_pst[x][y]))
                ) // 256
            if piece_mid_pst.size > 0 > board_arr[x][y] and piece_end_pst.size > 0:
                eval_sum += (
                    ((256 - end_score) * piece_mid_pst[x][y])
                    + (end_score * (piece_end_pst[x][y]))
                ) // 256
    return eval_sum


def endgame_score(board: Board) -> int:
    board_arr = board.board
    piece_val = [0, 1, 1, 2, 4, 0]
    sum_pg = 0
    for x in range(8):
        for y in range(8):
            if (
                board_arr[x][y] != 0
            ):  # skip empty squares; abs(0)-1 == -1 is a silent wrong index
                sum_pg += piece_val[abs(board_arr[x][y]) - 1]
    return (256 * (24 - sum_pg)) // 24
