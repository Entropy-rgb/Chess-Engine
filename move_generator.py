from config import board, Board, pieces_enum
import numpy as np
from game import square_in_board

# from game import is_valid_move


class move:
    def __init__(
        self, initial: tuple, final: tuple, piece: int, flag: int, capture: int
    ):
        self.initial = initial
        self.final = final
        self.piece = piece
        self.flag = flag  # flags : 0 for None ; 1 for capture ; 2 for double push ; 3 for en_passant ; 4 for castling ; 11 for queen promotion , 13 for rook , 15 for bishop , 17 for knight, +1 in each for capture
        self.capture = capture


def get_knight_moves(board, sq: tuple):
    knight_valid = [
        (2, 1),
        (1, 2),
        (-1, -2),
        (-2, -1),
        (1, -2),
        (-1, 2),
        (2, -1),
        (-2, 1),
    ]
    knight_moves = []
    for dis in knight_valid:
        final = (sq[0] + dis[0], sq[1] + dis[1])
        if square_in_board(final) and board[*final] * board[*sq] <= 0:
            knight_moves.append(
                move(sq, final, board[*sq], 1 if board[*final] else 0, board[*final])
            )
    return knight_moves


def get_king_moves(board, sq: tuple):
    direction = [(1, 1), (-1, -1), (1, -1), (-1, 1), (1, 0), (0, 1), (-1, 0), (0, -1)]
    king_moves = []
    for dis in direction:
        final = (sq[0] + dis[0], sq[1] + dis[1])
        if square_in_board(final) and board[*sq] * board[*final] <= 0:
            king_moves.append(
                move(sq, final, board[*sq], 1 if board[*final] else 0, board[*final])
            )
    if sq == (0, 4):
        king_moves.append(move(sq, (0, 2), pieces_enum.BLACK_KING, 4, 0))
        king_moves.append(move(sq, (0, 6), pieces_enum.BLACK_KING, 4, 0))
    elif sq == (7, 4):
        king_moves.append(move(sq, (7, 6), pieces_enum.WHITE_KING, 4, 0))
        king_moves.append(move(sq, (7, 2), pieces_enum.WHITE_KING, 4, 0))
    return king_moves


def get_directional_moves(
    board,
    sq: tuple,
    direction=[(1, 1), (-1, -1), (1, -1), (-1, 1), (0, 1), (1, 0), (0, -1), (-1, 0)],
):
    moves = []
    for dir in direction:
        tar = (sq[0] + dir[0], sq[1] + dir[1])
        while square_in_board(tar):
            if board[*tar] == pieces_enum.EMPTY:
                moves.append(move(sq, tar, board[*sq], 0, 0))
                tar = (tar[0] + dir[0], tar[1] + dir[1])
            elif board[*tar] != pieces_enum.EMPTY:
                if board[*tar] * board[*sq] < 0:
                    moves.append(move(sq, tar, board[*sq], 1, board[*tar]))
                break
    return moves


def get_pawn_moves(board, sq: tuple):
    # copy_orig = Board(board.board, board.turn, board.en_passant, board.castling_rights, board.half_move_clock , board.rook_moved)
    cpy_board = board.board
    playable_moves = []
    if cpy_board[*sq] == pieces_enum.WHITE_PAWN:
        if (
            square_in_board((sq[0] - 1, sq[1]))
            and cpy_board[sq[0] - 1][sq[1]] == pieces_enum.EMPTY
        ):
            if sq[0] - 1 == 0:
                for flag in [13, 15, 17, 11]:
                    playable_moves.append(
                        move(sq, (sq[0] - 1, sq[1]), pieces_enum.WHITE_PAWN, flag, 0)
                    )
            else:
                playable_moves.append(
                    move(sq, (sq[0] - 1, sq[1]), pieces_enum.WHITE_PAWN, 0, 0)
                )
                if (
                    square_in_board((sq[0] - 2, sq[1]))
                    and cpy_board[sq[0] - 2][sq[1]] == pieces_enum.EMPTY
                    and sq[0] == 6
                ):
                    playable_moves.append(
                        move(sq, (sq[0] - 2, sq[1]), pieces_enum.WHITE_PAWN, 2, 0)
                    )
        if square_in_board((sq[0] - 1, sq[1] + 1)) and board.en_passant == (
            sq[0] - 1,
            sq[1] + 1,
        ):
            playable_moves.append(
                move(
                    sq,
                    (sq[0] - 1, sq[1] + 1),
                    pieces_enum.WHITE_PAWN,
                    3,
                    cpy_board[sq[0]][sq[1] + 1],
                )
            )
        if square_in_board((sq[0] - 1, sq[1] - 1)) and board.en_passant == (
            sq[0] - 1,
            sq[1] - 1,
        ):
            playable_moves.append(
                move(
                    sq,
                    (sq[0] - 1, sq[1] - 1),
                    pieces_enum.WHITE_PAWN,
                    3,
                    cpy_board[sq[0]][sq[1] - 1],
                )
            )
        if (
            square_in_board((sq[0] - 1, sq[1] + 1))
            and cpy_board[sq[0] - 1][sq[1] + 1] > 0
        ):
            if sq[0] - 1 == 0:
                for flag in [12, 14, 16, 18]:
                    playable_moves.append(
                        move(
                            sq,
                            (sq[0] - 1, sq[1] + 1),
                            pieces_enum.WHITE_PAWN,
                            flag,
                            cpy_board[sq[0] - 1][sq[1] + 1],
                        )
                    )
            else:
                playable_moves.append(
                    move(
                        sq,
                        (sq[0] - 1, sq[1] + 1),
                        pieces_enum.WHITE_PAWN,
                        1,
                        cpy_board[sq[0] - 1][sq[1] + 1],
                    )
                )
        if (
            square_in_board((sq[0] - 1, sq[1] - 1))
            and cpy_board[sq[0] - 1][sq[1] - 1] > 0
        ):
            if sq[0] - 1 == 0:
                for flag in [12, 14, 16, 18]:
                    playable_moves.append(
                        move(
                            sq,
                            (sq[0] - 1, sq[1] - 1),
                            pieces_enum.WHITE_PAWN,
                            flag,
                            cpy_board[sq[0] - 1][sq[1] - 1],
                        )
                    )
            else:
                playable_moves.append(
                    move(
                        sq,
                        (sq[0] - 1, sq[1] - 1),
                        pieces_enum.WHITE_PAWN,
                        1,
                        cpy_board[sq[0] - 1][sq[1] - 1],
                    )
                )
    elif cpy_board[*sq] == pieces_enum.BLACK_PAWN:
        if (
            square_in_board((sq[0] + 1, sq[1]))
            and cpy_board[sq[0] + 1][sq[1]] == pieces_enum.EMPTY
        ):
            if sq[0] + 1 == 7:
                for flag in [11, 13, 15, 17]:
                    playable_moves.append(
                        move(sq, (sq[0] + 1, sq[1]), pieces_enum.BLACK_PAWN, flag, 0)
                    )
            else:
                playable_moves.append(
                    move(sq, (sq[0] + 1, sq[1]), pieces_enum.BLACK_PAWN, 0, 0)
                )
                if (
                    square_in_board((sq[0] + 2, sq[1]))
                    and cpy_board[sq[0] + 2][sq[1]] == pieces_enum.EMPTY
                    and sq[0] == 1
                ):
                    playable_moves.append(
                        move(sq, (sq[0] + 2, sq[1]), pieces_enum.BLACK_PAWN, 2, 0)
                    )
        if square_in_board((sq[0] + 1, sq[1] - 1)) and board.en_passant == (
            sq[0] + 1,
            sq[1] - 1,
        ):
            playable_moves.append(
                move(
                    sq,
                    (sq[0] + 1, sq[1] - 1),
                    pieces_enum.BLACK_PAWN,
                    3,
                    cpy_board[sq[0]][sq[1] - 1],
                )
            )
        if square_in_board((sq[0] + 1, sq[1] + 1)) and board.en_passant == (
            sq[0] + 1,
            sq[1] + 1,
        ):
            playable_moves.append(
                move(
                    sq,
                    (sq[0] + 1, sq[1] + 1),
                    pieces_enum.BLACK_PAWN,
                    3,
                    cpy_board[sq[0]][sq[1] + 1],
                )
            )
        if (
            square_in_board((sq[0] + 1, sq[1] + 1))
            and cpy_board[sq[0] + 1][sq[1] + 1] < 0
        ):
            if sq[0] + 1 == 7:
                for flag in [12, 14, 16, 18]:
                    playable_moves.append(
                        move(
                            sq,
                            (sq[0] + 1, sq[1] + 1),
                            pieces_enum.BLACK_PAWN,
                            flag,
                            cpy_board[sq[0] + 1][sq[1] + 1],
                        )
                    )
            else:
                playable_moves.append(
                    move(
                        sq,
                        (sq[0] + 1, sq[1] + 1),
                        pieces_enum.BLACK_PAWN,
                        1,
                        cpy_board[sq[0] + 1][sq[1] + 1],
                    )
                )
        if (
            square_in_board((sq[0] + 1, sq[1] - 1))
            and cpy_board[sq[0] + 1][sq[1] - 1] < 0
        ):
            if sq[0] + 1 == 7:
                for flag in [12, 14, 16, 18]:
                    playable_moves.append(
                        move(
                            sq,
                            (sq[0] + 1, sq[1] - 1),
                            pieces_enum.BLACK_PAWN,
                            flag,
                            cpy_board[sq[0] + 1][sq[1] - 1],
                        )
                    )
            else:
                playable_moves.append(
                    move(
                        sq,
                        (sq[0] + 1, sq[1] - 1),
                        pieces_enum.BLACK_PAWN,
                        1,
                        cpy_board[sq[0] + 1][sq[1] - 1],
                    )
                )
    return playable_moves


def move_generator(board: Board, turn=-1) -> list:
    if turn == -1:
        turn = board.turn
    valid_moves = []
    copy_board = board.board.copy()
    if turn == 0:
        for x in range(8):
            for y in range(8):
                i = copy_board[x][y]
                # for pawns
                if i == pieces_enum.WHITE_PAWN:
                    valid_moves += get_pawn_moves(board, (x, y))
                # for knights
                if i == pieces_enum.WHITE_KNIGHT:
                    valid_moves += get_knight_moves(copy_board, (x, y))
                # for rooks
                if i == pieces_enum.WHITE_ROOK:
                    valid_moves += get_directional_moves(
                        copy_board, (x, y), [(0, 1), (1, 0), (0, -1), (-1, 0)]
                    )
                # for bishops
                if i == pieces_enum.WHITE_BISHOP:
                    valid_moves += get_directional_moves(
                        copy_board, (x, y), [(1, 1), (1, -1), (-1, -1), (-1, 1)]
                    )
                # for queen
                if i == pieces_enum.WHITE_QUEEN:
                    valid_moves += get_directional_moves(
                        copy_board,
                        (x, y),
                        [
                            (0, 1),
                            (1, 0),
                            (0, -1),
                            (-1, 0),
                            (1, 1),
                            (1, -1),
                            (-1, -1),
                            (-1, 1),
                        ],
                    )
                # for king
                if i == pieces_enum.WHITE_KING:
                    valid_moves += get_king_moves(copy_board, (x, y))
    if turn == 1:
        for x in range(8):
            for y in range(8):
                i = copy_board[x][y]
                # for pawns
                if i == pieces_enum.BLACK_PAWN:
                    valid_moves += get_pawn_moves(board, (x, y))
                # for knights
                if i == pieces_enum.BLACK_KNIGHT:
                    valid_moves += get_knight_moves(copy_board, (x, y))
                # for rooks
                if i == pieces_enum.BLACK_ROOK:
                    valid_moves += get_directional_moves(
                        copy_board, (x, y), [(0, 1), (1, 0), (0, -1), (-1, 0)]
                    )
                # for bishops
                if i == pieces_enum.BLACK_BISHOP:
                    valid_moves += get_directional_moves(
                        copy_board, (x, y), [(1, 1), (1, -1), (-1, -1), (-1, 1)]
                    )
                # for queen
                if i == pieces_enum.BLACK_QUEEN:
                    valid_moves += get_directional_moves(
                        copy_board,
                        (x, y),
                        [
                            (0, 1),
                            (1, 0),
                            (0, -1),
                            (-1, 0),
                            (1, 1),
                            (1, -1),
                            (-1, -1),
                            (-1, 1),
                        ],
                    )
                # for king
                if i == pieces_enum.BLACK_KING:
                    valid_moves += get_king_moves(copy_board, (x, y))
    return valid_moves
