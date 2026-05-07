import cProfile
import pstats
from engine import make_engine_move
profiler = cProfile.Profile()
profiler.enable()
for i in range(20):
    make_engine_move(depth=3)
profiler.disable()
stats = pstats.Stats(profiler).sort_stats('percall')

stats.dump_stats('profiler.prof')





# import numpy as np
#
# from config import Board, board
# from game import move
# from move_generator import move_generator
#
# DEPTH = 3
# count = 0
# capture = 0
# en_passant = 0
# castle = 0
# promotion = 0
#
# CAPTURE_FLAGS = {1, 3, 12, 14, 16, 18}
# PROMOTION_FLAGS = {11, 12, 13, 14, 15, 16, 17, 18}
#
# test_brd = [
#     [0] * 8,
#     [0, 0, 1, 0, 0, 0, 0, 0],
#     [0, 0, 0, 1, 0, 0, 0, 0],
#     [-6, -1, 0, 0, 0, 0, 0, 4],
#     [0, -4, 0, 0, 0, 1, 0, 6],
#     [0] * 8,
#     [0, 0, 0, 0, -1, 0, -1, 0],
#     [0] * 8,
# ]
#
# test_board = Board(np.array(test_brd), 0, (8, 8), [0, 0, 0, 0], 0, [1, 1, 1, 1])
#
#
# def test_move_generator(inp_board: Board = board, depth: int | np.int64 = 1) -> None:
#     global count, castle, promotion, en_passant, capture
#     if depth == 0:
#         count += 1
#         return
#     moves = move_generator(inp_board)
#     for pos in moves:
#
#         cpy = Board(
#             inp_board.board.copy(),
#             inp_board.turn,
#             inp_board.en_passant,
#             inp_board.castling_rights.copy(),
#             inp_board.half_move_clock,
#             inp_board.rook_moved.copy(),
#         )
#         done = move(pos.initial, pos.final, None, cpy)
#         if done is None:
#             continue
#         if depth == 1:
#             if pos.flag in CAPTURE_FLAGS:
#                 capture += 1
#             if pos.flag == 4:
#                 castle += 1
#             if pos.flag == 3:
#                 en_passant += 1
#             if pos.flag in PROMOTION_FLAGS:
#                 promotion += 1
#         test_move_generator(cpy, depth - 1)
#
#
# test_move_generator(board, DEPTH)
# print(f"{count=} {en_passant=} {castle=} {promotion=} {capture=}")
