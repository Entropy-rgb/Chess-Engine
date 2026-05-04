from enum import IntEnum
from typing import Self

import numpy as np

DEPTH = 6


class Board:
    def __init__(
        self: Self,
        board: np.typing.NDArray[np.int64],
        turn: int | np.int64,
        en_passant: tuple[int | np.int64, int | np.int64],
        castling_rights: list[int | np.int64],
        half_move_clock: int | np.int64,
        rook_moved: list[int | np.int64],
    ):
        self.board = board
        self.turn = turn
        self.en_passant = en_passant
        self.castling_rights = castling_rights
        self.half_move_clock = half_move_clock
        self.rook_moved = rook_moved


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

starting_board = [
    [
        pieces_enum.BLACK_ROOK,
        pieces_enum.BLACK_KNIGHT,
        pieces_enum.BLACK_BISHOP,
        pieces_enum.BLACK_QUEEN,
        pieces_enum.BLACK_KING,
        pieces_enum.BLACK_BISHOP,
        pieces_enum.BLACK_KNIGHT,
        pieces_enum.BLACK_ROOK,
    ],
    [
        pieces_enum.BLACK_PAWN,
        pieces_enum.BLACK_PAWN,
        pieces_enum.BLACK_PAWN,
        pieces_enum.BLACK_PAWN,
        pieces_enum.BLACK_PAWN,
        pieces_enum.BLACK_PAWN,
        pieces_enum.BLACK_PAWN,
        pieces_enum.BLACK_PAWN,
    ],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [
        pieces_enum.WHITE_PAWN,
        pieces_enum.WHITE_PAWN,
        pieces_enum.WHITE_PAWN,
        pieces_enum.WHITE_PAWN,
        pieces_enum.WHITE_PAWN,
        pieces_enum.WHITE_PAWN,
        pieces_enum.WHITE_PAWN,
        pieces_enum.WHITE_PAWN,
    ],
    [
        pieces_enum.WHITE_ROOK,
        pieces_enum.WHITE_KNIGHT,
        pieces_enum.WHITE_BISHOP,
        pieces_enum.WHITE_QUEEN,
        pieces_enum.WHITE_KING,
        pieces_enum.WHITE_BISHOP,
        pieces_enum.WHITE_KNIGHT,
        pieces_enum.WHITE_ROOK,
    ],
]

board = Board(np.array(starting_board), 0, (8, 8), [1, 1, 1, 1], 0, [0, 0, 0, 0])
