from evaluator import *
from config import board
import chess

MOVE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 300,
    chess.BISHOP: 300,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}

SEARCH_INF = 10_000_000_000
MATE_SCORE = 1_000_000_000


def move_order_score(inp_board: chess.Board, move: chess.Move) -> int:
    score = 0
    if move.promotion:
        score += MOVE_VALUES[move.promotion]
    if inp_board.is_capture(move):
        captured_piece = inp_board.piece_at(move.to_square)
        if captured_piece is None and inp_board.is_en_passant(move):
            captured_piece = chess.Piece(chess.PAWN, not inp_board.turn)
        attacker = inp_board.piece_at(move.from_square)
        if captured_piece is not None and attacker is not None:
            score += 10 * MOVE_VALUES[captured_piece.piece_type]
            score -= MOVE_VALUES[attacker.piece_type]
    if inp_board.gives_check(move):
        score += 50
    return score


def ordered_moves(inp_board: chess.Board) -> list[chess.Move]:
    return sorted(
        inp_board.legal_moves,
        key=lambda move: move_order_score(inp_board, move),
        reverse=True,
    )


def noisy_moves(inp_board: chess.Board) -> list[chess.Move]:
    if inp_board.is_check():
        return ordered_moves(inp_board)
    return [
        move
        for move in ordered_moves(inp_board)
        if inp_board.is_capture(move) or move.promotion is not None
    ]


def minimax_caller(
    inp_board: chess.Board = board, depth: int = 3, maximizing_player: bool | None = None
)->chess.Move|None:
    if inp_board.outcome(claim_draw=True) is not None:
        return None
    maximizing_player = inp_board.turn == chess.WHITE
    best_eval = -SEARCH_INF if maximizing_player else SEARCH_INF
    best_eval_move = None
    alpha = -SEARCH_INF
    beta = SEARCH_INF
    for pos in ordered_moves(inp_board):
        inp_board.push(pos)
        curr_eval = minimax(inp_board, depth - 1, alpha, beta)
        if maximizing_player and curr_eval > best_eval: 
            best_eval = curr_eval
            best_eval_move = pos
        elif not maximizing_player and curr_eval < best_eval:  
            best_eval = curr_eval
            best_eval_move = pos
        if maximizing_player: 
            alpha = max(alpha, curr_eval)
        else: 
            beta = min(beta, curr_eval)
        inp_board.pop()
        if beta <= alpha:
            break
    return best_eval_move


def minimax(
    inp_board: chess.Board = board,
    depth: int = 3,
    alpha: int = -10_000_000_000,
    beta: int = 10_000_000_000,
):
    outcome = inp_board.outcome(claim_draw=True)
    if outcome is not None:
        if outcome.winner is None:
            return 0
        return MATE_SCORE + depth if outcome.winner == chess.WHITE else -MATE_SCORE - depth
    if depth <= 0:
        return quiescence(inp_board, alpha, beta)
    maximizing_player = inp_board.turn == chess.WHITE
    best_eval = -SEARCH_INF if maximizing_player else SEARCH_INF
    for pos in ordered_moves(inp_board):
        inp_board.push(pos)
        curr_eval = minimax(inp_board, depth - 1, alpha, beta)
        if maximizing_player and curr_eval > best_eval:
            best_eval = curr_eval
        elif not maximizing_player and curr_eval < best_eval:
            best_eval = curr_eval
        if maximizing_player: 
            alpha = max(alpha, curr_eval)
        else: 
            beta = min(beta, curr_eval)
        inp_board.pop()
        if beta <= alpha:
            break
    return best_eval


def quiescence(
    inp_board: chess.Board,
    alpha: int,
    beta: int,
    depth: int = 4,
):
    outcome = inp_board.outcome(claim_draw=True)
    if outcome is not None:
        if outcome.winner is None:
            return 0
        return MATE_SCORE + depth if outcome.winner == chess.WHITE else -MATE_SCORE - depth

    stand_pat = evals(inp_board)
    if depth <= 0:
        return stand_pat

    maximizing_player = inp_board.turn == chess.WHITE
    if maximizing_player:
        best_eval = stand_pat
        if best_eval >= beta:
            return best_eval
        alpha = max(alpha, best_eval)
        for move in noisy_moves(inp_board):
            inp_board.push(move)
            curr_eval = quiescence(inp_board, alpha, beta, depth - 1)
            inp_board.pop()
            if curr_eval > best_eval:
                best_eval = curr_eval
            alpha = max(alpha, curr_eval)
            if beta <= alpha:
                break
        return best_eval

    best_eval = stand_pat
    if best_eval <= alpha:
        return best_eval
    beta = min(beta, best_eval)
    for move in noisy_moves(inp_board):
        inp_board.push(move)
        curr_eval = quiescence(inp_board, alpha, beta, depth - 1)
        inp_board.pop()
        if curr_eval < best_eval:
            best_eval = curr_eval
        beta = min(beta, curr_eval)
        if beta <= alpha:
            break
    return best_eval


def make_engine_move(inp_board: chess.Board = board, depth: int = 3):
    move_to_play = minimax_caller(inp_board, depth)
    if move_to_play is None:
        print("[engine] WARNING: no valid move found, passing turn")
        return -1
    inp_board.push(move_to_play)
    return None
