import numpy as np

from enum import IntEnum


class Board:
    def __init__(self, board, turn, en_passant, castling_rights: list, half_move_clock):
        self.board = board
        self.turn = turn
        self.en_passant = en_passant
        self.castling_rights = castling_rights
        self.half_move_clock = half_move_clock


class pieces_enum(IntEnum):
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

board = Board(np.array(starting_board), 0, (8, 8), [1, 1, 1, 1], 0)
