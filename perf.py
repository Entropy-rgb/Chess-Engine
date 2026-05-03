from config import board, Board
from move_generator import move_generator
from game import move

count = 0

def test_move_generator(board=board, depth=1):
    global count
    if depth==0: 
        count+=1
        return
    moves = move_generator(board)
    for pos in moves:
        cpy = Board(board.board.copy(), board.turn , board.en_passant , board.castling_rights , board.half_move_clock , board.rook_moved)
        done = move(pos.initial , pos.final , None, cpy)
        if done is None:
            continue
        test_move_generator(cpy, depth-1)

test_move_generator(board , 4)
print(count)
