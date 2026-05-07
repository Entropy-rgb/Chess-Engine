from enum import IntEnum
import chess
from typing import Self

import numpy as np

DEPTH = 6

# Rook moved : (0,0) (0,7) (7,0) (7,7)
# CASTLE convention  : [QB] [KB] [QW] [KW]


class pieces_enum(IntEnum):
    EMPTY = 0
    BLACK_PAWN = 1
    BLACK_KNIGHT = 2
    BLACK_BISHOP = 3
    BLACK_ROOK = 4
    BLACK_QUEEN = 5
    BLACK_KING = 6
    WHITE_PAWN = -1
    WHITE_KNIGHT = -2
    WHITE_BISHOP = -3
    WHITE_ROOK = -4
    WHITE_QUEEN = -5
    WHITE_KING = -6


piece_map = {}
for x in pieces_enum:
    if x == 0:
        continue
    a, b = x.name.split("_")
    s = "w"
    if "B" in a:
        s = "b"
    image_var = f"{b.lower()}-{s}.svg"
    piece_map[x] = image_var

board = chess.Board()
