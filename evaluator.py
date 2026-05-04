from pst import find_pst
import numpy as np
from config import Board
from game import check_for_checkmate

def evals(board:Board)->int:
    board_arr = board.board
    vals = [0,9,5,3,3,1,0,-1,-3,-3,-5,-9,0]
    eval_sum = 0
    for x in range(8):
        for y in range(8):
            eval_sum+=vals[board_arr[x][y]+6]
            piece_mid_pst = find_pst(board_arr[x][y],0)
            piece_end_pst = find_pst(board_arr[x][y],1)
            end_score = endgame_score(board)
            if piece_mid_pst and piece_end_pst and board_arr[x][y] > 0:
                eval_sum-=(((256-end_score)*piece_mid_pst[x][y]) + (end_score*(piece_end_pst[x][y])))//256
            if piece_mid_pst and piece_end_pst and board_arr[x][y] < 0:
                eval_sum += (((256 - end_score) * piece_mid_pst[x][y]) + (end_score * (piece_end_pst[x][y]))) // 256
    return  eval_sum

def endgame_score(board:Board)->int:
    board_arr = board.board
    piece_val = [0,1,1,2,4,0]
    sum_pg = 0
    for x in range(8):
        for y in range(8):
            sum_pg+=piece_val[abs(board_arr[x][y])-1]
    return (256*(24-sum_pg))//24