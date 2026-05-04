from evaluator import *
from game import move, check_for_checkmate
from config import Board, board
from move_generator import move_generator
from move_generator import move as Move
from tqdm import tqdm


def promo_piece_detector(the_flag=0, turn=0):
    promo_piece = None
    if the_flag == 11 or the_flag == 12:
        promo_piece = -5 if turn == 0 else 5
    elif the_flag == 13 or the_flag == 14:
        promo_piece = -4 if turn == 0 else 4
    elif the_flag == 15 or the_flag == 16:
        promo_piece = -3 if turn == 0 else 3
    elif the_flag == 17 or the_flag == 18:
        promo_piece = -2 if turn == 0 else 2
    return promo_piece


def minimax_caller(
    inp_board: Board = board, depth: int = 3, maximizing_player: int = 1
):
    # maximizing_player=1 → Black (positive eval is good); starts at -INF, wants highest score
    # maximizing_player=0 → White (negative eval is good); starts at +INF, wants lowest score
    INF = 10_000_000_000
    best_eval = -INF if maximizing_player else INF
    best_eval_move = Move((8, 8), (8, 8), 10, -1, 10)
    moves = move_generator(inp_board)
    alpha = -INF
    beta = INF
    for pos in tqdm(moves):
        cpy = Board(
            inp_board.board.copy(),
            inp_board.turn,
            inp_board.en_passant,
            inp_board.castling_rights.copy(),
            inp_board.half_move_clock,
            inp_board.rook_moved.copy(),
        )
        promo_piece = promo_piece_detector(pos.flag, cpy.turn)
        done = move(pos.initial, pos.final, None, cpy, promo_piece)
        if done is None:
            continue
        curr_eval = minimax(cpy, depth - 1, maximizing_player ^ 1, alpha, beta)
        if maximizing_player and curr_eval > best_eval:  # Black: pick highest
            best_eval = curr_eval
            best_eval_move = pos
        elif not maximizing_player and curr_eval < best_eval:  # White: pick lowest
            best_eval = curr_eval
            best_eval_move = pos
        if maximizing_player:  # Black is the maximizer → update alpha
            alpha = max(alpha, curr_eval)
        else:  # White is the minimizer → update beta
            beta = min(beta, curr_eval)
        if beta <= alpha:
            break
    return best_eval_move


def minimax(
    inp_board: Board = board,
    depth: int = 3,
    maximizing_player: int = 1,
    alpha: int = -10_000_000_000,
    beta: int = 10_000_000_000,
):
    if depth == 0:
        return evals(inp_board)
    INF = 10_000_000_000
    best_eval = -INF if maximizing_player else INF
    moves = move_generator(inp_board)
    for pos in moves:
        cpy = Board(
            inp_board.board.copy(),
            inp_board.turn,
            inp_board.en_passant,
            inp_board.castling_rights.copy(),
            inp_board.half_move_clock,
            inp_board.rook_moved.copy(),
        )
        promo_piece = promo_piece_detector(pos.flag, int(cpy.turn))
        done = move(pos.initial, pos.final, None, cpy, promo_piece)
        if done is None:
            continue
        curr_eval = minimax(cpy, depth - 1, maximizing_player ^ 1, alpha, beta)
        if maximizing_player and curr_eval > best_eval:  # Black maximizes
            best_eval = curr_eval
        elif not maximizing_player and curr_eval < best_eval:  # White minimizes
            best_eval = curr_eval
        if maximizing_player:  # update alpha for maximizer
            alpha = max(alpha, curr_eval)
        else:  # update beta for minimizer
            beta = min(beta, curr_eval)
        if beta <= alpha:
            break
    return best_eval


def make_engine_move(inp_board: Board = board, depth: int = 3):
    move_to_play = minimax_caller(inp_board, depth)
    promo_piece = promo_piece_detector(move_to_play.flag, inp_board.turn)
    move(move_to_play.initial, move_to_play.final, None, inp_board, promo_piece)
    return move_to_play.flag
