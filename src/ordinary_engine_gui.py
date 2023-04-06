import pygame
import math
import pickle
import multiprocessing
import time as time
import random

class Node(): 

    def __init__(self, data):
        self.data = data
        self.children = []
    
    def add_child(self, child):
        self.children.append(child)


class Piece:

    def __init__(self, color, x, y, type):
        
        # The type instance variable is not given in enum form for speed reasons, 
        # enums were used so often that the program runs ~20-30% faster without enums. 
        # The following scheme was used for piece types:

        # KING = 1
        # QUEEN = 2
        # KNIGHT = 3
        # BISHOP = 4
        # PAWN = 5
        # ROOK = 6
        # NONE = 7

        # NONE type means an empty square, same with color = 'N'
        
        self.color = color # Either 'w' 'b' or 'N' (white, black, None)
        self.x = x
        self.y = y
        self.moved = False
        self.type = type
        self.value = 0


class Rook(Piece):

    def __init__(self, color, x, y, type):
        super().__init__(color, x, y, type)
        self.value = 500
    
    def valid_move(self, target, board, move_num):
        # All move methods have the board and move_num passed so that the type of the piece 
        # does not need to be checked in the board move method, as some move methods 
        # require the board and move_num, while others neither
        return self.valid_hori_move(target, board)

    def valid_hori_move(self, target, board):
        # For a rook, either the x or y position of a move must be the same as the rook
        if target.x != self.x and target.y != self.y: 
            return False
        if target.color == self.color:
            return False

        if target.x == self.x: 
            # target is down
            if target.y > self.y: 
                y = self.y + 1
                count = abs(target.y - y) # number of sq between the rook and target
                while count > 0:
                    cur_square = board[self.x][y]
                    if cur_square.type != 7 and cur_square != target:
                        return False # Checking if there is any piece between the rook and the target
                    count -= 1
                    y += 1
                return True

            # target is up
            if target.y < self.y: 
                y = self.y - 1
                count = abs(target.y - y)
                while count > 0:
                    cur_square = board[self.x][y]
                    if cur_square.type != 7 and cur_square != target:
                        return False
                    count -= 1
                    y -= 1
                return True

        # target is right
        if target.x > self.x:
            x = self.x + 1
            count = abs(target.x - x)
            while count > 0:
                cur_square = board[x][self.y]
                if cur_square.type != 7 and cur_square != target:
                    return False
                count -= 1
                x += 1
            return True
        
        # target is left
        x = self.x - 1 
        count = abs(target.x - x)
        while count > 0:
            cur_square = board[x][self.y]
            if cur_square.type != 7 and cur_square != target:
                return False
            count -= 1
            x -= 1
        return True


class Bishop(Piece):

    def __init__(self, color, x, y, type):
        super().__init__(color, x, y, type)
        self.value = 330
    
    def valid_move(self, target, board, move_num):
        return self.valid_diag_move(target, board)

    def valid_diag_move(self, target, board):
        # For a bishop, all moves have a different x and y value compared to the bishop
        if target.x == self.x or target.y == self.y: 
            return False
        if target.color == self.color:
            return False
        if abs(self.x - target.x) != abs(self.y - target.y): # checks for diagonal movement
            return False

        if target.y > self.y:
            # target is down to the right
            if target.x > self.x :
                x = self.x + 1
                y = self.y + 1
                count = abs(self.x - target.x) # number of squares to move
                while count > 0:
                    cur_square = board[x][y]
                    if cur_square.type != 7 and cur_square != target:
                        return False # check if a piece is in between the bishop and the target
                    count -= 1
                    x += 1
                    y += 1
                return True

            # target is down to the left
            if target.x < self.x:
                x = self.x - 1
                y = self.y + 1
                count = abs(self.x - target.x)
                while count > 0:
                    cur_square = board[x][y]
                    if cur_square.type != 7 and cur_square != target:
                        return False
                    count -= 1
                    x -= 1
                    y += 1
                return True

        # target is up to the right
        if target.x > self.x: 
            x = self.x + 1
            y = self.y - 1
            count = abs(self.x - target.x)
            while count > 0:
                cur_square = board[x][y]
                if cur_square.type != 7 and cur_square != target:
                    return False
                count -= 1
                x += 1
                y -= 1
            return True

        # target is up to the left
        x = self.x - 1
        y = self.y - 1
        count = abs(self.x - target.x)
        while count > 0:
            cur_square = board[x][y]
            if cur_square.type != 7 and cur_square != target:
                return False
            count -= 1
            x -= 1
            y -= 1
        return True


class Queen(Rook, Bishop):

    def __init__(self, color, x, y, type):
        super().__init__(color, x, y, type)
        self.value = 900
    
    def valid_move(self, target, board, move_num):
    # A queen is just a bishop-rook so the valid_move method of the queen 
    # is simply the rook and bishop move methods
        return self.valid_diag_move(target, board) or self.valid_hori_move(target, board)

    
class Knight(Piece):

    def __init__(self, color, x, y, type):
        super().__init__(color, x, y, type)
        self.value = 320
    
    def valid_move(self, target, board, move_num):
        if target.color == self.color:
            return False
        # 2 square in x or y, 1 square in the other direction. 1 * 2 = 2
        if abs(target.x - self.x) * abs(target.y - self.y) == 2: 
            return True
        return False


class Pawn(Piece):

    def __init__(self, color, x, y, type):
        super().__init__(color, x, y, type)
        self.has_moved_double = False
        self.double_move_num = 0
        self.value = 100
    
    def valid_move(self, target, board, move_num):
        if self.valid_capture(target, board, move_num):
            return True
        if target.type != 7:
            return False
        if self.x != target.x:
            return False
        if self.color == 'b':
            if target.y == self.y + 1: # black single square move
                return target.type == 7
            if target.y == 3 and self.y == 1 and board[self.x][2].type == 7: # bl double sq
                return target.type == 7
        if self.color == 'w':
            if target.y == self.y - 1: # white single square move
                return target.type == 7
            if target.y == 4 and self.y == 6 and board[self.x][5].type == 7: # w double sq
                return target.type == 7
        return False

    def valid_capture(self, target, board, move_num):
        # pawn has different move for capturing and moving so it requires a second method
        if self.can_en_passant(target, board, move_num):
            return True
        if target.type == 7 or target.color == self.color:
            return False
        if self.color == 'b':
            return abs(self.x - target.x) == 1 and target.y - self.y == 1 
        if self.color == 'w':
            return abs(self.x - target.x) == 1 and self.y - target.y == 1 

    def can_en_passant(self, target, board, move_num):
        if target.color == self.color:
            return False
        # target at this point is the square that the pawn is moving to
        if self.color == 'b':
            if abs(self.x - target.x) != 1 or target.y - self.y != 1:
                return False
            target = board[target.x][target.y - 1]
        elif self.color == 'w':
            if abs(self.x - target.x) != 1 or self.y - target.y != 1:
                return False
            target = board[target.x][target.y + 1]
        # target is now the piece the pawn is taking
        if target.color == self.color or target.type != 5:
            return False
        if target.has_moved_double == False or target.double_move_num != move_num - 1 :
            return False
        return True


class King(Piece):

    def __init__(self, color, x, y, type):
        super().__init__(color, x, y, type)
        self.value = 20000
        self.has_castled = False
    
    def valid_move(self, target, board, move_num):
        if target.color == self.color:
            return False
        if (self.valid_k_side_castle(target, board, move_num) or 
            self.valid_q_side_castle(target, board, move_num)):
            return True
        if target.x == self.x and target.y == self.y + 1: # down
            return True
        if target.x == self.x + 1 and target.y == self.y + 1: # down right
            return True
        if target.x == self.x + 1 and target.y == self.y: # right
            return True
        if target.x == self.x + 1 and target.y == self.y - 1: # up right
            return True
        if target.x == self.x and target.y == self.y - 1: # up
            return True
        if target.x == self.x - 1 and target.y == self.y - 1: # up left
            return True
        if target.x == self.x - 1 and target.y == self.y: # left
            return True
        if target.x == self.x - 1 and target.y == self.y + 1: # down left
            return True
        return False

    def valid_k_side_castle(self, target, board, move_num):
        if self.moved:
            return False
        if target.type != 7:
            return False
        # king side castles take place on the same rank and 7th file (not using 0 indexing)
        if target.x != 6 or target.y != self.y: 
            return False
        # checking if squares crossed while castling are empty
        if board[self.x + 1][self.y].type != 7 or board[self.x + 2][self.y].type != 7: 
            return False
        if self.in_check(board, move_num): 
            return False
        # ensuring king is not in check during castlle or at final destination
        dummy_king = King(self.color, self.x + 1, self.y, 1) 
        if dummy_king.in_check(board, move_num):
            return False
        dummy_king.x = dummy_king.x + 1
        if dummy_king.in_check(board, move_num):
            return False
        rook = board[7][self.y]
        return rook.type == 6 and rook.moved == False  

    def valid_q_side_castle(self, target, board, move_num):
        if self.moved:
            return False
        if target.type != 7:
            return False
        if target.x != 2 or target.y != self.y:# queen side castles take place on the same rank and 3nd file
            return False
        if board[self.x - 1][self.y].type != 7 or board[self.x - 2][self.y].type != 7:
            return False
        if self.in_check(board, move_num):
            return False
        dummy_king = King(self.color, self.x - 1, self.y, 1)
        if dummy_king.in_check(board, move_num):
            return False
        dummy_king.x = dummy_king.x - 1
        if dummy_king.in_check(board, move_num):
            return False
        rook = board[0][self.y]
        if board[1][self.y].type != 7:
            return False
        return rook.type == 6 and rook.moved == False  

    def in_check(self, board, move_num):
        # if a piece can target the kings location, the king is in check
        color = self.color
        opp_color = 'b'
        if color == 'b':
            opp_color = 'w'
        for x in range(8):
            for y in range(8):
                if board[x][y].color == opp_color and board[x][y].valid_move(self, board, move_num):
                    return True
        return False


class Chess_Board:

    '''Class that contains the board and all board related functions'''

    def __init__(self):
        # top left of board is 0,0 bottom right is 7,7 
        self.board = [[Rook('b',0,0,6),Pawn('b',0,1,5),Piece('N',0,2,7),Piece('N',0,3,7),Piece('N',0,4,7),Piece('N',0,5,7),Pawn('w',0,6,5),Rook('w',0,7,6)],
                    [Knight('b',1,0,3),Pawn('b',1,1,5),Piece('N',1,2,7),Piece('N',1,3,7),Piece('N',1,4,7),Piece('N',1,5,7),Pawn('w',1,6,5),Knight('w',1,7,3)],
                    [Bishop('b',2,0,4),Pawn('b',2,1,5),Piece('N',2,2,7),Piece('N',2,3,7),Piece('N',2,4,7),Piece('N',2,5,7),Pawn('w',2,6,5),Bishop('w',2,7,4)],
                    [Queen('b',3,0,2),Pawn('b',3,1,5),Piece('N',3,2,7),Piece('N',3,3,7),Piece('N',3,4,7),Piece('N',3,5,7),Pawn('w',3,6,5),Queen('w',3,7,2)],
                    [King('b',4,0,1),Pawn('b',4,1,5),Piece('N',4,2,7),Piece('N',4,3,7),Piece('N',4,4,7),Piece('N',4,5,7),Pawn('w',4,6,5),King('w',4,7,1)],
                    [Bishop('b',5,0,4),Pawn('b',5,1,5),Piece('N',5,2,7),Piece('N',5,3,7),Piece('N',5,4,7),Piece('N',5,5,7),Pawn('w',5,6,5),Bishop('w',5,7,4)],
                    [Knight('b',6,0,3),Pawn('b',6,1,5),Piece('N',6,2,7),Piece('N',6,3,7),Piece('N',6,4,7),Piece('N',6,5,7),Pawn('w',6,6,5),Knight('w',6,7,3)],
                    [Rook('b',7,0,6),Pawn('b',7,1,5),Piece('N',7,2,7),Piece('N',7,3,7),Piece('N',7,4,7),Piece('N',7,5,7),Pawn('w',7,6,5),Rook('w',7,7,6)]]
        
        # Piece square tables taken, with very very minor 
        # adjustments, from https://www.chessprogramming.org/Simplified_Evaluation_Function
        self.w_pawn_table = [[0,50,10,5,0,5,5,0],
                             [0,50,10,5,0,-5,10,0],
                             [0,50,20,10,0,-10,10,0],
                             [0,50,30,25,24,0,-20,0],
                             [0,50,30,25,24,0,-20,0],
                             [0,50,20,10,0,-10,10,0],
                             [0,50,10,5,0,-5,10,0],
                             [0,50,10,5,0,5,5,0]]
        
        self.b_pawn_table = [[0,5,5,0,5,10,50,0],
                             [0,10,-5,0,5,10,50,0],
                             [0,10,-10,0,10,20,50,0],
                             [0,-20,0,24,25,30,50,0],
                             [0,-20,0,24,25,30,50,0],
                             [0,10,-10,0,10,20,50,0],
                             [0,10,-5,0,5,10,50,0],
                             [0,5,5,0,5,10,50,0]]
        
        self.w_knight_table = [[-50,-40,-30,-30,-30,-30,-40,-50],
                               [-40,-20,0,5,0,5,-20,-40],
                               [-30,0,10,15,15,10,0,-30],
                               [-30,0,15,20,20,15,5,-30],
                               [-30,0,15,20,20,15,5,-30],
                               [-30,0,10,15,15,10,0,-30],
                               [-40,-20,0,5,0,5,-20,-40],
                               [-50,-40,-30,-30,-30,-30,-40,-50]]
        
        self.b_knight_table = [[-50,-40,-30,-30,-30,-30,-40,-50],
                               [-40,-20,5,0,5,0,-20,-40],
                               [-30,0,10,15,15,10,0,-30],
                               [-30,5,15,20,20,15,0,-30],
                               [-30,5,15,20,20,15,0,-30],
                               [-30,0,10,15,15,10,0,-30],
                               [-40,-20,5,0,5,0,-20,-40],
                               [-50,-40,-30,-30,-30,-30,-40,-50]]
        
        self.w_bishop_table = [[-20,-10,-10,-10,-10,-10,-10,-20],
                               [-10,0,0,5,0,10,5,-10],
                               [-10,0,5,5,10,10,0,-10],
                               [-10,0,10,10,10,10,0,-10],
                               [-10,0,10,10,10,10,0,-10],
                               [-10,0,5,5,10,10,0,-10],
                               [-10,0,0,5,0,10,5,-10],
                               [-20,-10,-10,-10,-10,-10,-10,-20]]
        
        self.b_bishop_table = [[-20,-10,-10,-10,-10,-10,-10,-20],
                               [-10,5,10,0,5,0,0,-10],
                               [-10,0,10,10,5,5,0,-10],
                               [-10,0,10,10,10,10,0,-10],
                               [-10,0,10,10,10,10,0,-10],
                               [-10,0,10,10,5,5,0,-10],
                               [-10,5,10,0,5,0,0,-10],
                               [-20,-10,-10,-10,-10,-10,-10,-20]]
        
        self.w_rook_table = [[0,5,-5,-5,-5,-5,-5,0],
                             [0,10,0,0,0,0,0,0],
                             [0,10,0,0,0,0,0,0],
                             [0,10,0,0,0,0,0,5],
                             [0,10,0,0,0,0,0,5],
                             [0,10,0,0,0,0,0,0],
                             [0,10,0,0,0,0,0,0],
                             [0,5,-5,-5,-5,-5,-5,0]]
        
        self.b_rook_table = [[0,5,-5,-5,-5,-5,-5,0],
                             [0,0,0,0,0,0,10,0],
                             [0,0,0,0,0,0,10,0],
                             [5,0,0,0,0,0,10,0],
                             [5,0,0,0,0,0,10,0],
                             [0,0,0,0,0,0,10,0],
                             [0,0,0,0,0,0,10,0],
                             [0,5,-5,-5,-5,-5,-5,0]]
        
        self.w_queen_table = [[-20,-10,-10,-5,0,-10,-10,-20],
                              [-10,0,0,0,0,5,0,-10],
                              [-10,0,5,5,5,5,5,-10],
                              [-5,0,5,5,5,5,0,-5],
                              [-5,0,5,5,5,5,0,-5],
                              [-10,0,5,5,5,5,0,-10],
                              [-10,0,0,0,0,0,0,-10],
                              [-20,-10,-10,-5,-5,-10,-10,-20]]
        
        self.b_queen_table = [[-20,-10,-10,-5,-5,-10,-10,-20],
                              [-10,0,0,0,0,0,0,-10],
                              [-10,0,5,5,5,5,0,-10],
                              [-5,0,5,5,5,5,0,-5],
                              [-5,0,5,5,5,5,0,-5],
                              [-10,0,5,5,5,5,5,-10],
                              [-10,0,0,0,0,5,0,-10],
                              [-20,-10,-10,-5,0,-10,-10,-20]]
        
        self.w_king_table = [[-30,-30,-30,-30,-20,-10,20,20],
                             [-40,-40,-40,-40,-30,-20,20,30],
                             [-40,-40,-40,-40,-30,-20,0,10],
                             [-50,-50,-50,-50,-40,-20,0,0],
                             [-50,-50,-50,-50,-40,-20,0,0],
                             [-40,-40,-40,-40,-30,-20,0,10],
                             [-40,-40,-40,-40,-30,-20,20,30],
                             [-30,-30,-30,-30,-20,-10,20,20]]
        
        self.b_king_table = [[20,20,-10,-20,-30,-30,-30,-30],
                             [30,20,-20,-30,-40,-40,-40,-40],
                             [10,0,-20,-30,-40,-40,-40,-40],
                             [0,0,-20,-40,-50,-50,-50,-50],
                             [0,0,-20,-40,-50,-50,-50,-50],
                             [10,0,-20,-30,-40,-40,-40,-40],
                             [30,20,-20,-30,-40,-40,-40,-40],
                             [20,20,-10,-20,-30,-30,-30,-30]]

        self.w_king_end_table = [[-50,-30,-30,-30,-30,-30,-30,-50],
                                 [-40,-20,-10,-10,-10,-10,-30,-30],
                                 [-30,-10,20,30,30,20,0,-30],
                                 [-20,0,30,40,40,30,0,-30],
                                 [-20,0,30,40,40,30,0,-30],
                                 [-30,-10,20,30,30,20,0,-30],
                                 [-40,-20,-10,-10,-10,-10,-30,-30],
                                 [-50,-30,-30,-30,-30,-30,-30,-50]]

        self.b_king_end_table = [[-50,-30,-30,-30,-30,-30,-30,-50],
                                 [-30,-30,-10,-10,-10,-10,-20,-40],
                                 [-30,0,20,30,30,20,-10,-30],
                                 [-30,0,30,40,40,30,0,-20],
                                 [-30,0,30,40,40,30,0,-20],
                                 [-30,0,20,30,30,20,-10,-30],
                                 [-30,-30,-10,-10,-10,-10,-20,-40],
                                 [-50,-30,-30,-30,-30,-30,-30,-50]]

        self.move_num = 0
        self.turn = True
        self.undo_list = [] 
        self.opening_book = None
        self.init_opening_book()

    def init_opening_book(self):
        e2e4 = Node([4,6,' ',4,4])

        e7e5 = Node([4,1,' ',4,3]) # bishop doesnt pin
        g1f3 = Node([6,7,' ',5,5])
        b8c6 = Node([1,0,' ',2,2])
        f1c4 = Node([5,7,' ',2,4])
        f8c5 = Node([5,0,' ',2,3])
        e1g1 = Node([4,7,' ',6,7])
        g8f6 = Node([6,0,' ',5,2])
        f1e1 = Node([5,7,' ',4,7])

        f1b5 = Node([5,7,' ',1,3]) # bishop pins
        g8f6_5 = Node([6,0,' ',5,2])
        d2d3 = Node([3,6,' ',3,5])
        f8c5_2 = Node([5,0,' ',2,3])
        c2c3 = Node([2,6,' ',2,5])
        e8g8 = Node([4,0,' ',6,0])
        e1g1_2 = Node([4,7,' ',6,7])

        c7c6 = Node([2,1,' ',2,2]) # karo kan
        d2d4 = Node([3,6,' ',3,4])
        d7d5 = Node([3,1,' ',3,3])
        e4d5 = Node([4,4,' ',3,3])
        c6d5 = Node([2,2,' ',3,3])
        f1d3 = Node([5,7,' ',3,5])
        b8c6_2 = Node([1,0,' ',2,2])
        c2c3_2 = Node([2,6,' ',2,5])
        g8f6_2 = Node([6,0,' ',5,2])
        c1f4 = Node([2,7,' ',5,4])

        d2d4_2 = Node([3,6,' ',3,4])  # queens gambit
        d7d5_2 = Node([3,1,' ',3,3])
        c2c4 = Node([2,6,' ',2,4])

        d5c4 = Node([3,3,' ',2,4]) # queens gambit accepted
        e2e4_2 = Node([4,6,' ',4,4])
        e7e6 = Node([4,1,' ',4,2])
        f1c4_2 = Node([5,7,' ',2,4])

        g8f6_3 = Node([6,0,' ',5,2]) # queens gambit accepted with knight
        e4e5 = Node([4,4,' ',4,3])
        f6d5 = Node([5,2,' ',3,3])
        b1c3_2 = Node([1,7,' ',2,5])

        c7c6_2 = Node([2,1,' ',2,2]) # slav
        g1f3_4 = Node([6,7,' ',5,5])
        g8f6_6 = Node([6,0,' ',5,2])
        b1c3_4 = Node([1,7,' ',2,5])

        e7e6_2 = Node([4,1,' ',4,2]) # declined
        b1c3 = Node([1,7,' ',2,5])
        g8f6_4 = Node([6,0,' ',5,2])
        c4d5 = Node([2,4,' ',3,3])

        e6d5 = Node([4,2,' ',3,3]) # take with pawn
        c1g5 = Node([2,7,' ',6,3])

        f6d5_2 = Node([5,2,' ',3,3]) # take with knight
        g1f3_2 = Node([6,7,' ',5,5])

        c7c5 = Node([2,1,' ',2,3]) # sicilian
        g1f3_3 = Node([6,7,' ',5,5])
        d7d6 = Node([3,1,' ',3,2])
        b1c3_3 = Node([1,7,' ',2,5])

        e2e4.add_child(c7c5) # sicilian
        c7c5.add_child(g1f3_3) 
        g1f3_3.add_child(d7d6)
        d7d6.add_child(b1c3_3)

        d2d4.add_child(d7d5_2) # queens gambit accepted
        d7d5_2.add_child(c2c4)
        c2c4.add_child(d5c4)
        d5c4.add_child(e2e4_2)
        e2e4_2.add_child(e7e6)
        e7e6.add_child(f1c4_2)
        f1c4_2.add_child(g8f6_3)
        g8f6_3.add_child(e4e5)
        e4e5.add_child(f6d5)
        f6d5.add_child(b1c3_2)

        c2c4.add_child(e7e6_2) # queens gambit declined
        e7e6_2.add_child(b1c3)
        b1c3.add_child(g8f6_4)
        g8f6_4.add_child(c4d5)

        c4d5.add_child(e6d5) # take back with pawn
        e6d5.add_child(c1g5)

        c4d5.add_child(f6d5_2) # take back with knight
        f6d5_2.add_child(g1f3_2)

        c2c4.add_child(c7c6_2) # slav
        c7c6_2.add_child(g1f3_4)
        g1f3_4.add_child(g8f6_6)
        g8f6_6.add_child(b1c3_4)

        e2e4.add_child(e7e5) # 4 knights 
        e7e5.add_child(g1f3)
        g1f3.add_child(b8c6)
        b8c6.add_child(f1c4)
        f1c4.add_child(f8c5)
        f8c5.add_child(e1g1)
        e1g1.add_child(g8f6)
        g8f6.add_child(f1e1)

        b8c6.add_child(f1b5) # 4 knights bishop pin
        f1b5.add_child(g8f6_5)
        g8f6_5.add_child(d2d3)
        d2d3.add_child(f8c5_2)
        f8c5_2.add_child(c2c3)
        c2c3.add_child(e8g8)
        e8g8.add_child(e1g1_2)

        e2e4.add_child(c7c6) # karo kan
        c7c6.add_child(d2d4_2)
        d2d4_2.add_child(d7d5)
        d7d5.add_child(e4d5)
        e4d5.add_child(c6d5)
        c6d5.add_child(f1d3)
        f1d3.add_child(b8c6_2)
        b8c6_2.add_child(c2c3_2)
        c2c3_2.add_child(g8f6_2)
        g8f6_2.add_child(c1f4)

        self.opening_book = Node(0)
        self.opening_book.add_child(e2e4)
        self.opening_book.add_child(d2d4)

    def provisional_move(self, x1, y1, x2, y2):
        '''Portion of making a move that does not check for game 
        ending board states like checkmate and stalemate. Done to prevent 
        recursion when checking for checkmate and stalemate'''
        piece = self.board[x1][y1]
        target = self.board[x2][y2]

        if piece.color == 'w' and not self.turn:
            return False
        if piece.color == 'b' and self.turn:
            return False

        if piece.type == 7: 
            return False
        if not piece.valid_move(target, self.board, self.move_num):
            return False
        
        # used in castling to store empty square the king moves to
        # and in en passnat to store the pawn being captured
        prev_special_target = None 
        prev_special_piece = None # involved in castling to store the rook
        moving_double = False 
        castling = False 

        if piece.type == 5: # en passant
            if piece.can_en_passant(target, self.board, self.move_num):
                if piece.color == 'w':
                    special_tar = self.board[target.x][target.y + 1]
                else:
                    special_tar = self.board[target.x][target.y - 1]
                # pickle is used for deepcopy, faster than copy.deepcopy
                prev_special_target = pickle.loads(pickle.dumps(special_tar)) 
                self.board[special_tar.x][special_tar.y] = Piece('N', special_tar.x, special_tar.y, 7)
            elif abs(target.y - piece.y) == 2:
                moving_double = True

        elif piece.type == 1: # castling
            if piece.valid_q_side_castle(target, self.board, self.move_num):
                castling = True
                special_piece = self.board[0][piece.y]
                special_tar = self.board[3][piece.y]
                prev_special_piece = pickle.loads(pickle.dumps(special_piece))
                prev_special_target = pickle.loads(pickle.dumps(special_tar))
                self.board[special_piece.x][special_piece.y] = Piece('N', special_piece.x, special_piece.y, 7)
                self.board[3][piece.y] = special_piece
                special_piece.x = 3
                special_piece.y = piece.y
                special_piece.moved = True
            elif piece.valid_k_side_castle(target, self.board, self.move_num):
                castling = True
                special_piece = self.board[7][piece.y]
                special_tar = self.board[5][piece.y]
                prev_special_piece = pickle.loads(pickle.dumps(special_piece))
                prev_special_target = pickle.loads(pickle.dumps(special_tar))
                self.board[special_piece.x][special_piece.y] = Piece('N', special_piece.x, special_piece.y, 7)
                self.board[5][piece.y] = special_piece
                special_piece.x = 5
                special_piece.y = piece.y
                special_piece.moved = True

        # pieces appended to the undolist for future use in case a move is invalid.
        # A list, instead of single variables, of prev_pieces, targets, ect is needed for 
        # loops that use provisional_move
        prev_piece = pickle.loads(pickle.dumps(piece))
        prev_target = pickle.loads(pickle.dumps(target))
        self.undo_list.append([prev_piece, prev_target, prev_special_piece, prev_special_target])
        if moving_double:
            piece.has_moved_double = True
            piece.double_move_num = self.move_num
        elif castling:
            piece.has_castled = True

        self.board[piece.x][piece.y] = Piece('N', piece.x, piece.y, 7)
        piece.x = target.x
        piece.y = target.y
        self.board[target.x][target.y] = piece

        if piece.color == 'w':
            king = self.get_white_king()
        else:
            king = self.get_black_king()
        if king.in_check(self.board, self.move_num):
            self.partial_undo() 
            return False

        self.check_promote(piece)     
        piece.moved = True
        self.move_num += 1
        self.turn = not self.turn
        return True

    def make_move(self, x1, y1, x2 ,y2):
        '''Move method that checks for checkmate and stalemate'''
        global game_over
        color = self.board[x1][y1].color
        if self.provisional_move(x1, y1, x2, y2):
            if color == 'w':
                opp_color = 'b'
                print_color = 'White'
            else:
                opp_color = 'w'
                print_color = 'Black'
            if self.in_checkmate(opp_color):
                print(print_color,'Wins!')
                game_over = True
            if self.in_stalemate(opp_color):
                print('Draw by stalemate')
                game_over = True
            return True
        return False

    def partial_undo(self):
        '''Undo that does not revert move_num or player turn'''
        prev_piece = self.undo_list[self.move_num][0]
        prev_target = self.undo_list[self.move_num][1]
        prev_special_piece = self.undo_list[self.move_num][2]
        prev_special_target = self.undo_list[self.move_num][3]
        self.board[prev_piece.x][prev_piece.y] = prev_piece
        self.board[prev_target.x][prev_target.y] = prev_target
        if prev_special_piece != None:
            self.board[prev_special_piece.x][prev_special_piece.y] = prev_special_piece
        if prev_special_target != None:
            self.board[prev_special_target.x][prev_special_target.y] = prev_special_target
        del self.undo_list[self.move_num]

    def get_white_king(self):
        for x in range(8):
            for y in range(8):
                if self.board[x][y].type == 1 and self.board[x][y].color == 'w':
                    return self.board[x][y]

    def get_black_king(self):
        for x in range(8):
            for y in range(8):
                if self.board[x][y].type == 1 and self.board[x][y].color == 'b':
                    return self.board[x][y]

    def in_checkmate(self, color):
        if color == 'w':
            king = self.get_white_king()
        else:
            king = self.get_black_king()
        if not king.in_check(self.board, self.move_num):
            return False
        for x1 in range(8):
            for y1 in range(8):
                cur = self.board[x1][y1]
                if cur.color == color:
                    for x2 in range(8):
                        for y2 in range(8):
                            if self.provisional_move(x1,y1,x2,y2):
                                self.undo_move()
                                return False
        return True

    def in_stalemate(self, color):
        if color == 'w':
            king = self.get_white_king()
        else:
            king = self.get_black_king()
        if king.in_check(self.board, self.move_num):
            return False
        for x1 in range(8):
            for y1 in range(8):
                cur = self.board[x1][y1]
                if cur.color == color:
                    for x2 in range(8):
                        for y2 in range(8):
                            if self.provisional_move(x1,y1,x2,y2):
                                self.undo_move()
                                return False
        return True

    def check_promote(self, piece):
        # Engine only promotes to queen for simplicity. 
        # without further method implementation the player can also only promote to queen as of 
        # now. Change would not be too difficult as lichess does convey what piece the player 
        # promoted to, but this will be implemented in the future. 
        if piece.type == 5:
            x = piece.x
            y = piece.y
            if piece.y == 0 and piece.color == 'w':
                self.board[x][y] = Queen('w',x,y,2)  
                '''choice = input('choice Q, K, R, B')
                self.board[x][y] = Queen('w',x,y,2)
                if choice == 'Q':
                    self.board[x][y] = Queen('w',x,y,2)
                elif choice == 'K':
                    self.board[x][y] = Knight('w',x,y,3)
                elif choice == 'R':
                    self.board[x][y] = Rook('w',x,y,6)
                elif choice == 'B':
                    self.board[x][y] = Bishop('w',x,y,4)'''
            elif piece.y == 7 and piece.color == 'b':
                self.board[x][y] = Queen('b',x,y,2) 
                '''choice = input('choice Q, K, R, B')
                if choice == 'Q':
                    self.board[x][y] = Queen('b',x,y,2)
                elif choice == 'K':
                    self.board[x][y] = Knight('b',x,y,3)
                elif choice == 'R':
                    self.board[x][y] = Rook('b',x,y,6)
                elif choice == 'B':
                    self.board[x][y] = Bishop('b',x,y,4)'''

    def print_board(self): 
        # useful for debugging. Does not provide the best model of the 
        # board as ' ' is a differing size to other characters.
        for x in range(8): 
            for y in range(8):
                cur = self.board[y][x]
                if cur.color == 'w':
                    if cur.type == 4:
                        print('♗', end='')
                    if cur.type == 6:
                        print('♖', end='')
                    if cur.type == 2:
                        print('♕', end='')
                    if cur.type == 1:
                        print('♔', end='')
                    if cur.type == 3:
                        print('♘', end='')
                    if cur.type == 5:
                        print('♙', end='')
                elif cur.color == 'b':
                    if cur.type == 4:
                        print('♝', end='')
                    if cur.type == 6:
                        print('♜', end='')
                    if cur.type == 2:
                        print('♛', end='')
                    if cur.type == 1:
                        print('♚', end='')
                    if cur.type == 3:
                        print('♞', end='')
                    if cur.type == 5:
                        print('♟︎', end='')
                else:
                    print(' ', end='')
            print('')

    def list_moves(self, color):
        '''Creates a list of moves, the index of each being a list in the form of 
        [piece_x,piece_y,' ',target_x,target_y]. ' ' is added for ease of reading.'''
        moves = []
        for x1 in range(8):
            for y1 in range(8):
                cur = self.board[x1][y1]
                if cur.color == color:
                    for x2 in range(8):
                        for y2 in range(8):
                            if self.provisional_move(x1,y1,x2,y2):
                                moves.append([x1,y1,' ',x2,y2])
                                self.undo_move() 
        return moves

    def undo_move(self):
        '''Undo method that returns turn and move_num to prev values'''
        self.move_num -= 1
        self.turn = not self.turn
        self.partial_undo()
        return True

    def evaluate(self, color):
        '''
        Evaluate returns a value relative to how good a position is for a given color, meaning 
        this function does not work in a negamax algorithm. For example, if black was up 
        1 pawn with all other positional aspects equal, the function would return 100, 
        the value of a pawn, not -100 as commonly associated with chess engines. 
        Given the same situation with white, 100 would also be returned. 
        If black/white was down a pawn, -100 would be returned. 
        '''
        opp_color = 'b'
        if color == 'b':
            opp_color = 'w'
        eval = 0
        opp_eval = 0
        piece_eval = 0
        opp_piece_eval = 0
        king_loc = []
        opp_king_loc = []
        for x in range(8):
            for y in range(8):
                cur = self.board[x][y]
                if cur.color == color:
                    piece_eval += cur.value
                    eval += cur.value
                    if cur.color == 'w':
                        if cur.type == 4:
                            eval += self.w_bishop_table[x][y]
                        if cur.type == 1:
                            king_loc = [cur.x, cur.y]
                        if cur.type == 3:
                            eval += self.w_knight_table[x][y]
                        if cur.type == 5:
                            piece_eval -= 100
                            eval += self.w_pawn_table[x][y]
                        if cur.type == 2:
                            eval += self.w_queen_table[x][y]
                        else:
                            eval += self.w_rook_table[x][y]
                    else:
                        if cur.type == 4:
                            eval += self.b_bishop_table[x][y]
                        if cur.type == 1:
                            king_loc = [cur.x, cur.y]
                        if cur.type == 3:
                            eval += self.b_knight_table[x][y]
                        if cur.type == 5:
                            piece_eval -= 100
                            eval += self.b_pawn_table[x][y]
                        if cur.type == 2:
                            eval += self.b_queen_table[x][y]
                        else:
                            eval += self.b_rook_table[x][y]
                elif cur.color == opp_color:
                    opp_piece_eval += cur.value
                    opp_eval += cur.value
                    if cur.color == 'w':
                        if cur.type == 4:
                            opp_eval += self.w_bishop_table[x][y]
                        if cur.type == 1:
                            opp_king_loc = [cur.x, cur.y]
                        if cur.type == 3:
                            opp_eval += self.w_knight_table[x][y]
                        if cur.type == 5:
                            opp_piece_eval -= 100
                            opp_eval += self.w_pawn_table[x][y]
                        if cur.type == 2:
                            opp_eval += self.w_queen_table[x][y]
                        else:
                            opp_eval += self.w_rook_table[x][y]
                    else:
                        if cur.type == 4:
                            opp_eval += self.b_bishop_table[x][y]
                        if cur.type == 1:
                            opp_king_loc = [cur.x, cur.y]
                        if cur.type == 3:
                            opp_eval += self.b_knight_table[x][y]
                        if cur.type == 5:
                            opp_piece_eval -= 100
                            opp_eval += self.b_pawn_table[x][y]
                        if cur.type == 2:
                            opp_eval += self.b_queen_table[x][y]
                        else:
                            opp_eval += self.b_rook_table[x][y]
        if piece_eval < 21331 and opp_eval < 21331: 
            # If both player have at maximum, 2 rooks and a bishop excluding pawns,
            # I consider it the endgame. This comes out to be 500 + 500 + 330 + 20000 (king)
            # = 21330. This switched the king piece square tables to the endgame focused one. 
            if color == 'w':
                eval += self.w_king_end_table[king_loc[0]][king_loc[1]]
                opp_eval += self.b_king_end_table[opp_king_loc[0]][opp_king_loc[1]]
            else:
                eval += self.b_king_end_table[king_loc[0]][king_loc[1]]
                opp_eval += self.w_king_end_table[opp_king_loc[0]][opp_king_loc[1]]
        else:
            if color == 'w':
                eval += self.w_king_table[king_loc[0]][king_loc[1]]
                opp_eval += self.b_king_table[opp_king_loc[0]][opp_king_loc[1]]
            else:
                eval += self.b_king_table[king_loc[0]][king_loc[1]]
                opp_eval += self.w_king_table[opp_king_loc[0]][opp_king_loc[1]]
        return eval - opp_eval

    def minimax(self, alpha, beta, remain_depth, color, moves, best_moves, procnum):
        # The entry point of the minimax algorithm. Useful to separate 
        # from maximize for easier incorporation of processes, but generally the 
        # same purpose as maximize. 
        best_move = None
        opp_color = 'w'
        if color == 'w':
            opp_color = 'b'
        for move in moves:
            for i in range(1, 5, 1):
                if best_moves[i] != [] and best_moves[i][0] > alpha:
                    alpha = best_moves[i][0]
                    best_move = best_moves[i][1]
            self.provisional_move(move[0],move[1],move[3],move[4])
            score = self.minimize(alpha, beta, remain_depth - 1, opp_color)[0]
            self.undo_move()
            if score >= beta:
                best_moves[procnum] = beta, best_move
                return beta, best_move
            if score > alpha:
                alpha = score
                best_move = move
                best_moves[procnum] = alpha, best_move
        best_moves[procnum] = alpha, best_move
        best_moves[4+procnum] = []
        return alpha, best_move

    def maximize(self, alpha, beta, remain_depth, color):
        # return the best move and the accompaning score with said move
        best_move = None
        opp_color = 'w'
        if color == 'w':
            opp_color = 'b'
        if remain_depth == 0:
            return self.evaluate(color), best_move
        moves = self.list_moves(color)  
        for move in moves:
            self.provisional_move(move[0],move[1],move[3],move[4])
            score = self.minimize(alpha, beta, remain_depth - 1, opp_color)[0]
            self.undo_move()
            if score >= beta:
                return beta, best_move
            if score > alpha:
                alpha = score
                best_move = move
        return alpha, best_move

    def minimize(self, alpha, beta, remain_depth, color):
        # return the move that minimizes the score.
        # This function will always be called after maximize, 
        # meaning that this function finds what the engine deems to be
        # the opponents best response to the engine's move
        best_move = None
        opp_color = 'w'
        if color == 'w':
            opp_color = 'b'
        if remain_depth == 0:
            return -self.evaluate(color), best_move
        moves = self.list_moves(color)
        for move in moves:
            self.provisional_move(move[0],move[1],move[3],move[4])
            score = self.maximize(alpha, beta, remain_depth - 1, opp_color)[0]
            self.undo_move()
            if score <= alpha:
                return alpha, best_move
            if score < beta:
                beta = score
                best_move = move
        if best_move == None and beta == 1000000: # game ending move
            if self.in_stalemate(color): # don't stalemate the opponent
                return alpha, best_move
            beta -= 10 - remain_depth # prefer a checkmate in less moves
        return beta, best_move

def index_to_lich(move):
    '''Converts a move in this program, ex. [4,6,' ',4,4] to the form lichess uses, e2e4'''
    x1 = str(chr(int(move[0]) + 97))
    y1 = str(abs(8 - int(move[1])))
    x2 = str(chr(int(move[3]) + 97))
    y2 = str(abs(8 - int(move[4])))
    return x1 + y1 + x2 + y2


def draw_board(window):
    '''Draw the chess board'''
    white = False
    for x in range(100, 900, 100):
        white = not white
        for y in range(100, 900, 100):
            pygame.draw.rect(window,('white' if white else 'gray'),(x,y,100,100))
            white = not white

def list_pieces(piece_imgs, board):
    '''Create an image for each piece in the board to be drawn later'''
    global flip_board
    pieces = []
    for x in range(8):
        row = []
        for y in range(8):
            piece = board[x][y]
            if piece.type != 7:
                if piece.color == 'w':
                    if piece.type == 1:
                        img = piece_imgs[0]
                    elif piece.type == 2:
                        img = piece_imgs[1]
                    elif piece.type == 3:
                        img = piece_imgs[2]
                    elif piece.type == 4:
                        img = piece_imgs[3]
                    elif piece.type == 5:
                        img = piece_imgs[4]
                    elif piece.type == 6:
                        img = piece_imgs[5]
                else:
                    if piece.type == 1:
                        img = piece_imgs[6]
                    elif piece.type == 2:
                        img = piece_imgs[7]
                    elif piece.type == 3:
                        img = piece_imgs[8]
                    elif piece.type == 4:
                        img = piece_imgs[9]
                    elif piece.type == 5:
                        img = piece_imgs[10]
                    elif piece.type == 6:
                        img = piece_imgs[11]
                if flip_board:
                    img_rect = img.get_rect(x=abs(900-brd_to_gui(piece.x)),
                                            y=abs(900-brd_to_gui(piece.y)))
                else:
                    img_rect = img.get_rect(x=brd_to_gui(piece.x),y=brd_to_gui(piece.y))
                row.append([img, img_rect])
            else:
                row.append(0)
        pieces.append(row)
    return pieces

def draw_pieces(window, pieces):
    '''Draw each piece within the list of pieces on the window'''
    global flip_board
    for x in range(8):
        for y in range(8):
            piece = pieces[x][y]
            if piece != 0:
                window.blit(piece[0], piece[1])

def round(x): 
    '''Round to the nearest 100'''
    if x % 100 < 50:
        return int(math.floor(x / 100.0)) * 100
    return int(math.ceil(x / 100.0)) * 100

def round_down(x): 
    '''Round dow to the nearest 100'''
    return int(math.floor(x / 100.0)) * 100

def clamp(x):
    '''Keep value between 100 and 800'''
    if x > 800:
        return 800
    if x < 100:
        return 100
    return x

def gui_to_brd(x):
    return int(x / 100 - 1) 

def brd_to_gui(x):
    return (x + 1) * 100

def init_imgs():
    return [pygame.image.load('../res/whiteKing.png'),
            pygame.image.load('../res/whiteQueen.png'),
            pygame.image.load('../res/whiteKnight.png'),
            pygame.image.load('../res/whiteBishop.png'),
            pygame.image.load('../res/whitePawn.png'),
            pygame.image.load('../res/whiteRook.png'),
            pygame.image.load('../res/blackKing.png'),
            pygame.image.load('../res/blackQueen.png'),
            pygame.image.load('../res/blackKnight.png'),
            pygame.image.load('../res/blackBishop.png'),
            pygame.image.load('../res/blackPawn.png'),
            pygame.image.load('../res/blackRook.png')]

def main():
    global game_over
    global flip_board
    game_over = False
    flip_board = False
    pygame.init()
    window = pygame.display.set_mode((1000,1000))
    piece_imgs = init_imgs()
    drag = False
    quit = False
    break_flag = False
    pos = None
    cur_img = None
    prev_loc = None
    prev_move = None
    check_obook = True
    chess_board = Chess_Board()
    cur_node = chess_board.opening_book
    pieces = list_pieces(piece_imgs, chess_board.board)

    # *****Engine Depth***************
    max_depth = 4
    # ********************************

    # color selection text
    font = pygame.font.Font('freesansbold.ttf', 60)
    white_txt = font.render('White',True,'White','Black')
    white_rect = white_txt.get_rect()
    white_rect.topleft = (200,500)
    black_txt = font.render('Black',True,'White','Black')
    black_rect = white_txt.get_rect()
    black_rect.topleft = (600,500)
    select_txt = font.render('Choose a color to play as',True,'White','Black')
    select_rect = white_txt.get_rect()
    select_rect.topleft = (150,100)
    window.blit(white_txt,white_rect)
    window.blit(black_txt,black_rect)
    window.blit(select_txt,select_rect)
    pygame.display.update()

    clicked_white = False
    clicked_black = False
    break_flag = False

    while True: # choosing color to play as
        if break_flag:
            break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if (pos[0] >= white_rect.x and pos[1] >= white_rect.y 
                    and pos[0] <= white_rect.x + white_rect.width and 
                    pos[1] <= white_rect.y + white_rect.height):
                    clicked_white = True
                elif (pos[0] >= black_rect.x and pos[1] >= black_rect.y 
                    and pos[0] <= black_rect.x + black_rect.width and 
                    pos[1] <= black_rect.y + black_rect.height):
                    clicked_black = True
            elif event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if (clicked_white and pos[0] >= white_rect.x and pos[1] >= white_rect.y 
                    and pos[0] <= white_rect.x + white_rect.width and 
                    pos[1] <= white_rect.y + white_rect.height):
                        bot_color = 'b'
                        bot_move = False
                        break_flag = True
                        break
                elif (clicked_black and pos[0] >= black_rect.x and pos[1] >= black_rect.y 
                    and pos[0] <= black_rect.x + black_rect.width and 
                    pos[1] <= black_rect.y + black_rect.height):
                        bot_color = 'w'
                        bot_move = True
                        break_flag = True
                        flip_board = True
                        break
                else:
                    clicked_black = clicked_white = False

    while not quit: # game loop
        if game_over:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        exit(0)
        if bot_move: 
            start = time.time()
            move = None
            if check_obook: # opening book
                if prev_move == None:
                    # randomly choose an opening variation
                    choice = random.randint(0,len(chess_board.opening_book.children)-1) 
                    cur_node = chess_board.opening_book.children[choice]
                    move = [0,cur_node.data]
                else:
                    for node in cur_node.children: # continue opening from prev node
                        if node.data == prev_move:
                            if len(node.children) > 0:
                                choice = random.randint(0,len(node.children)-1)
                                cur_node = node.children[choice]
                                move = [0,cur_node.data]
                                break
                            check_obook = False
                    else:
                            check_obook = False

            if move == None: # no opening move in move tree
                moves = chess_board.list_moves(bot_color)
                if len(moves) > 1: # divide moves between the processes if there are 2 or more moves
                    first = []
                    second = []
                    third = []
                    fourth = []
                    count = 0
                    for i in range(len(moves)):
                        if count == 0:
                            first.append(moves[i])
                        elif count == 1:
                            second.append(moves[i])
                        elif count == 2:
                            third.append(moves[i])
                        if count == 3:
                            fourth.append(moves[i])
                            count = 0
                        else:
                            count += 1

                    manager = multiprocessing.Manager()
                    best_moves = manager.dict() # best move from each process is stored here
                    best_moves[1] = best_moves[2] = best_moves[3] = best_moves[4] = []

                    first_eval = multiprocessing.Process(target=chess_board.minimax, 
                                                         args=(-1000000, 1000000, max_depth, 
                                                         bot_color, first, best_moves, 1))
                    second_eval = multiprocessing.Process(target=chess_board.minimax, 
                                                          args=(-1000000, 1000000, max_depth, 
                                                          bot_color, second, best_moves, 2))
                    third_eval = multiprocessing.Process(target=chess_board.minimax, 
                                                         args=(-1000000, 1000000, max_depth, 
                                                         bot_color, third, best_moves, 3))
                    fourth_eval = multiprocessing.Process(target=chess_board.minimax, 
                                                          args=(-1000000, 1000000, max_depth, 
                                                          bot_color, fourth, best_moves, 4))
                    first_eval.start()
                    second_eval.start()
                    third_eval.start()
                    fourth_eval.start()

                    while len(best_moves) != 8:
                        # pygame requires an event to be called every few seconds or the OS
                        # will think the program crashed. Doubles as a join-like function between
                        # the processes as pygame.event.pump() cannot be called in a different process
                        pygame.event.pump()

                    move = [-1000000, None]
                    for i in range(1, 5, 1): # find the best move between each process
                        if best_moves[i][0] > move[0] and best_moves[i][1] != None:
                            move = best_moves[i]
                else:
                    move = [0,moves[0]] # if there is only one legal move, do said move

            chess_board.make_move(move[1][0],move[1][1],move[1][3],move[1][4]) 
            eval = move[0]
            move = index_to_lich(move[1])
            print(eval, move)
            print(time.time() - start,'\n')
            bot_move = not bot_move

        else: # player move
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit = True

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    break_flag = False
                    pos = pygame.mouse.get_pos()
                    x = round_down(pos[0])
                    y = round_down(pos[1])
                    for i in range(8): # find the piece you selected
                        if break_flag:
                            break
                        for j in range(8):
                            img = pieces[i][j]
                            if img != 0:
                                loc = img[1].topleft
                                if x == loc[0] and y == loc[1]:
                                    cur_img = img[1]
                                    prev_loc = loc[0], loc[1]
                                    break_flag = True
                                    drag = True
                                    break
                elif event.type == pygame.MOUSEBUTTONUP: 
                    loc = cur_img.topleft
                    x = clamp(round(loc[0]))
                    y = clamp(round(loc[1]))
                    move = [gui_to_brd(prev_loc[0]), gui_to_brd(prev_loc[1]), gui_to_brd(x), gui_to_brd(y)]
                    if flip_board:
                        move = [abs(7-i) for i in move]
                    if chess_board.make_move(move[0], move[1], move[2], move[3]):
                        prev_move = [move[0], move[1], ' ', move[2], move[3]]
                        bot_move = True
                        break_flag = True
                    drag = False
                elif event.type == pygame.MOUSEMOTION:
                    if drag:
                        cur_img.move_ip(event.rel)
                
        draw_board(window)
        if not drag: # dont redraw pieces while one is being moved
            pieces = list_pieces(piece_imgs, chess_board.board) 
        draw_pieces(window, pieces)
        pygame.display.update()

if __name__ == '__main__':
    main()