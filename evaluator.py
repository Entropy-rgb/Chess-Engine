import numpy as np
from pst import find_pst
import chess


PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 300,
    chess.BISHOP: 300,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}


def pst_score(table: np.ndarray, square: chess.Square) -> int:
    # PST arrays are written rank 8 to rank 1, while python-chess squares
    # are indexed rank 1 to rank 8.
    row = 7 - chess.square_rank(square)
    col = chess.square_file(square)
    return int(table[row][col])


def evals(board: chess.Board) -> int:
    eval_sum = 0
    end_score = endgame_score(board)
    for sq, piece in board.piece_map().items():
        boardxy = piece.piece_type * (-1 if piece.color == chess.WHITE else 1)
        material = PIECE_VALUES[piece.piece_type]
        eval_sum += material if piece.color == chess.WHITE else -material

        piece_mid_pst = find_pst(boardxy, 0)
        piece_end_pst = find_pst(boardxy, 1)
        if piece_mid_pst.size == 0 or piece_end_pst.size == 0:
            continue

        blended_pst = (
            ((256 - end_score) * pst_score(piece_mid_pst, sq))
            + (end_score * pst_score(piece_end_pst, sq))
        ) // 256
        eval_sum += blended_pst if piece.color == chess.WHITE else -blended_pst
    return eval_sum


def endgame_score(board: chess.Board) -> int:
    piece_val = {
        chess.PAWN: 0,
        chess.KNIGHT: 1,
        chess.BISHOP: 1,
        chess.ROOK: 2,
        chess.QUEEN: 4,
        chess.KING: 0,
    }
    sum_pg = 0
    for piece in board.piece_map().values():
        sum_pg += piece_val[piece.piece_type]
    return (256 * (24 - sum_pg)) // 24
