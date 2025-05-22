#TODO:
#En Passant, King cannot castle through check, Underpromotion
#All pieces of a colour must block or capture checking piece
#Checkmate and Stalemate
#50 move draw, draw by repetition, draw by insufficient material
#Timer
#Borders & Customization
#Main Menu
#Multiplayer
#AI Engine

import pygame as pg
import copy
import os
import math
from typing import List

#dimensions and sizes
WIDTH: int = 800
HEIGHT: int = 800
square_side: int = WIDTH/8
piece_width = 80
piece_height = 80

#colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
OFF_WHITE = (240, 233, 220)
DARK_GRAY = (45, 45, 45)
MID_GRAY = (61, 61, 61)
RED = (255, 0, 0)
LIGHT_RED = (221, 60, 60)

#board lists
START_POS: List[str] = [
    ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
    ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
    ['']*8,
    ['']*8,
    ['']*8,
    ['']*8,
    ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
    ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]
boardlist: List[str] = START_POS.copy()
'''[
    ['bR', '', '', '', 'bK', '', '', 'bR'],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['wR', '', '', '', 'wK', '', '', 'wR']
]
'''

#customization
piece_set = 'cardinal' #cardinal, caifornia(65:80), maestro(, staunty, tatiana 
DARK_COLOUR = MID_GRAY
LIGHT_COLOUR = OFF_WHITE
DOT_COLOUR = LIGHT_RED

#flags
turn: str = 'w'
selected: tuple = ()
dragging: tuple = ()
check = ''
win = ''

white_queenside_castle: bool = True
white_kingside_castle: bool = True
black_queenside_castle: bool = True
black_kingside_castle: bool = True

#creating screen
pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Chess")
screen.fill(WHITE)

code_dir = os.path.dirname(__file__)
images_dir = os.path.join(code_dir, 'piece', piece_set)

class Board():
    def __init__(self, boardlist) -> None:
        global screen
        self.surf = screen
        self.boardlist = boardlist

    # Draws out the chess board
    def draw_squares(self) -> None:
        for row in range(8):
            for col in range(8):
                if (row % 2 == 0) and (col % 2 == 0):
                    square_colour = LIGHT_COLOUR
                elif (row % 2 == 1) and (col % 2 == 1):
                    square_colour = LIGHT_COLOUR
                else:
                    square_colour = DARK_COLOUR

                square_rect = pg.Rect(col*square_side, row*square_side,
                               square_side, square_side)

                pg.draw.rect(self.surf, square_colour, square_rect)
                if selected == (row, col):
                    pg.draw.rect(self.surf, DOT_COLOUR, square_rect, 5)

    
    def draw_pieces(self) -> None:
        global dragging, piece_set, images_dir
        for row in range(8):
            for col in range(8):
                piece_name = boardlist[row][col]
                if piece_name and (row, col) != dragging:
                    img_path = os.path.join(images_dir, piece_name+'.svg')

                    img = pg.image.load(img_path)
                    img = pg.transform.smoothscale(img, (piece_width, piece_height))

                    square_rect = pg.Rect(col*square_side, row*square_side, square_side, square_side)
                    piece_rect = img.get_rect(center = square_rect.center)
                    self.surf.blit(img, piece_rect)
    
    def draw_legal_moves(self) -> None:
        global selected, turn
        if selected:
            colour = get_colour(get_piece(self.boardlist, selected))
            if colour == turn:
                all_valid_moves = valid_moves(self.boardlist, selected)

                for move in all_valid_moves:
                    row, col = move
                    center = (col*square_side+square_side//2, row*square_side+square_side//2)
                    pg.draw.circle(screen, DOT_COLOUR, center, 10)

    def draw_dragging_piece(self, mouse_pos):
        global dragging, images_dir
        row, col = dragging
        mx, my = mouse_pos

        piece_name = get_piece(self.boardlist, dragging)

        img_path = os.path.join(images_dir, piece_name+'.svg')
        img = pg.image.load(img_path)
        img = pg.transform.smoothscale(img, (80, 80))

        img_rect = img.get_rect()
        img_rect.center = (mx, my)
        
        self.surf.blit(img, img_rect)


#-----Utility Functions-----#  
# Converts absolute coordinates to relative coordinates of square eg. (132, 273) -> (1, 2)         
def convert_coords(abs_coords: tuple) -> tuple:
    ax, ay = abs_coords
    relative_coords = (math.floor(ax/100), math.floor(ay/100))
    return relative_coords

def opp_colour(colour) -> None:
    return 'w' if colour == 'b' else 'b'

def get_piece(boardlist, pos: tuple) -> str:
    row, col = pos
    try:
        return boardlist[row][col]
    except IndexError:
        return None
    
def get_colour(piece: str) -> str:
    return piece[0] if piece else ''

def get_piecetype(piece: str) -> str:
    return piece[1] if piece else ''

def within_limits(pos: tuple) -> bool:
    if (0 <= pos[0] <= 7) and (0 <= pos[1] <= 7):
        return True
    else:
        return False

#-----Functions to return all legal moves in a certain direction----#
class Directions():
    def __init__(self, boardlist, start_pos: tuple, colour: str) -> None:
        self.start_pos = start_pos
        self.start_row, self.start_col = self.start_pos
        self.colour = colour
        self.boardlist = boardlist

    def n(self, limit: int) -> List[tuple]:
        all_valid_moves = []
        row = self.start_row-1
        col = self.start_col
        distance = 0

        while row >= 0:

            piece = self.boardlist[row][col]
            distance = self.start_row - row

            #Blocked or limit exceeded
            if get_colour(piece) == self.colour or distance > limit:
                break
            #Capturing piece
            elif get_colour(piece) == opp_colour(self.colour):
                all_valid_moves.append((row, col))
                break
            #Empty square
            else:
                all_valid_moves.append((row, col))

            row-=1

        return all_valid_moves

    def s(self, limit: int) -> List[tuple]:
        all_valid_moves = []
        row = self.start_row+1
        col = self.start_col
        distance = 0

        while row <= 7:
            piece = self.boardlist[row][col]
            distance = row - self.start_row
            #Blocked or limit exceeded
            if get_colour(piece) == self.colour or distance > limit:
                break
            #Capturing piece
            elif get_colour(piece) == opp_colour(self.colour):
                all_valid_moves.append((row, col))
                break
            #Empty square
            else:
                all_valid_moves.append((row, col))

            row+=1

        return all_valid_moves

    def e(self, limit: int) -> List[tuple]:
        all_valid_moves = []
        row = self.start_row
        col = self.start_col+1
        distance = 0

        while col <= 7:
            
            piece = self.boardlist[row][col]
            distance = col - self.start_col
            #Blocked or limit exceeded
            if get_colour(piece) == self.colour or distance > limit:
                break
            #Capturing piece
            elif get_colour(piece) == opp_colour(self.colour):
                all_valid_moves.append((row, col))
                break
            #Empty square
            else:
                all_valid_moves.append((row, col))
            col+=1
            
        return all_valid_moves

    def w(self, limit: int) -> List[tuple]:
        all_valid_moves = []
        row = self.start_row
        col = self.start_col-1
        distance = 0

        while col >= 0:
            
            piece = self.boardlist[row][col]
            distance = self.start_col - col
            #Blocked or limit exceeded
            if get_colour(piece) == self.colour or distance > limit:
                break
            #Capturing piece
            elif get_colour(piece) == opp_colour(self.colour):
                all_valid_moves.append((row, col))
                break
            #Empty square
            else:
                all_valid_moves.append((row, col))
            col-=1
            
        return all_valid_moves

    def ne(self, limit: int) -> List[tuple]:
        all_valid_moves = []
        row = self.start_row-1
        col = self.start_col+1
        distance = 0

        while row >= 0 and col <= 7:
            piece = self.boardlist[row][col]
            distance = col - self.start_col
            #Blocked or limit exceeded
            if get_colour(piece) == self.colour or distance > limit:
                break
            #Capturing piece
            elif get_colour(piece) == opp_colour(self.colour):
                all_valid_moves.append((row, col))
                break
            #Empty square
            else:
                all_valid_moves.append((row, col))
            row-=1
            col+=1
            
        return all_valid_moves

    def nw(self, limit: int) -> List[tuple]:
        all_valid_moves = []
        row = self.start_row-1
        col = self.start_col-1
        distance = 0

        while row >= 0 and col >= 0:
            
            piece = self.boardlist[row][col]
            distance =  self.start_row - row
            #Blocked or limit exceeded
            if get_colour(piece) == self.colour or distance > limit:
                break
            #Capturing piece
            elif get_colour(piece) == opp_colour(self.colour):
                all_valid_moves.append((row, col))
                break
            #Empty square
            else:
                all_valid_moves.append((row, col))
            row-=1
            col-=1
            
        return all_valid_moves

    def sw(self, limit: int) -> List[tuple]:
        all_valid_moves = []
        row = self.start_row+1
        col = self.start_col-1
        distance = 0

        while row <= 7 and col >= 0:
            
            piece = self.boardlist[row][col]
            distance = row - self.start_row
            #Blocked or limit exceeded
            if get_colour(piece) == self.colour or distance > limit:
                break
            #Capturing piece
            elif get_colour(piece) == opp_colour(self.colour):
                all_valid_moves.append((row, col))
                break
            #Empty square
            else:
                all_valid_moves.append((row, col))
            row+=1
            col-=1
            
        return all_valid_moves

    def se(self, limit: int) -> List[tuple]:
        all_valid_moves = []
        row = self.start_row+1
        col = self.start_col+1
        distance = 0

        while row <= 7 and col <= 7:
            
            piece = self.boardlist[row][col]
            distance = row - self.start_row
            #Blocked or limit exceeded
            if get_colour(piece) == self.colour or distance > limit:
                break
            #Capturing piece
            elif get_colour(piece) == opp_colour(self.colour):
                all_valid_moves.append((row, col))
                break
            #Empty square
            else:
                all_valid_moves.append((row, col))
            row+=1
            col+=1
            
        return all_valid_moves

#-----Functions to return all legal moves for each piece type-----#
class PieceManager():
    def __init__(self, pos: tuple, colour: str) -> List[tuple]:
        self.pos = pos
        self.row, self.col = self.pos
        self.colour = colour

    def valid_pawn_moves(self, boardlist) -> List[tuple]:
        #TODO: en passant
        all_valid_moves = []

        if self.colour == 'w':
            n1 = (self.row-1, self.col)
            n2 = (self.row-2, self.col)
            ne = (self.row-1, self.col+1)
            nw = (self.row-1, self.col-1)

            if not get_piece(boardlist, n1):
                all_valid_moves.append(n1)

                if not get_piece(boardlist, n2) and self.row == 6:
                    all_valid_moves.append(n2)

            if get_colour(get_piece(boardlist, ne)) == opp_colour(self.colour):
                all_valid_moves.append(ne)

            if get_colour(get_piece(boardlist, nw)) == opp_colour(self.colour):
                all_valid_moves.append(nw)
            
        if self.colour == 'b':
            s1 = (self.row+1, self.col)
            s2 = (self.row+2, self.col)
            se = (self.row+1, self.col+1)
            sw = (self.row+1, self.col-1)

            if not get_piece(boardlist, s1):
                all_valid_moves.append(s1)

                if not get_piece(boardlist, s2) and self.row == 1:
                    all_valid_moves.append(s2)

            if get_colour(get_piece(boardlist, se)) == opp_colour(self.colour):
                all_valid_moves.append(se)

            if get_colour(get_piece(boardlist, sw)) == opp_colour(self.colour):
                all_valid_moves.append(sw)

        return all_valid_moves

    def valid_knight_moves(self, boardlist) -> List[tuple]:
        all_valid_moves = []
              
        for row_change in [1, -1, 2, -2]:
            col_change = 3-abs(row_change) 
            for sign in [1, -1]:
                new_pos = (self.row + row_change, self.col + sign*col_change)
                if within_limits(new_pos) and get_colour(get_piece(boardlist, new_pos)) != self.colour:
                    all_valid_moves.append(new_pos)

        return all_valid_moves

    def valid_bishop_moves(self, boardlist) -> List[tuple]:

        all_valid_moves = []
        directions = Directions(boardlist, self.pos, self.colour)

        all_valid_moves+=directions.ne(8)+directions.sw(8)+directions.nw(8)+directions.se(8)

        return all_valid_moves

    def valid_rook_moves(self, boardlist) -> List[tuple]:
        all_valid_moves = []
        directions = Directions(boardlist, self.pos, self.colour)

        all_valid_moves+=directions.n(8)+directions.s(8)+directions.w(8)+directions.e(8)

        return all_valid_moves
        
    def valid_queen_moves(self, boardlist) -> List[tuple]:

        all_valid_moves = []
        directions = Directions(boardlist, self.pos, self.colour)

        all_valid_moves+=directions.n(8)+directions.s(8)+directions.w(8)+directions.e(8)
        all_valid_moves+=directions.ne(8)+directions.sw(8)+directions.nw(8)+directions.se(8)

        return all_valid_moves

    def valid_king_moves(self, boardlist) -> List[tuple]:

        global white_kingside_castle, white_queenside_castle, black_kingside_castle, black_queenside_castle
        all_valid_moves = []

        directions = Directions(boardlist, self.pos, self.colour)

        all_valid_moves+=directions.n(1)+directions.s(1)+directions.w(1)+directions.e(1)
        all_valid_moves+=directions.ne(1)+directions.sw(1)+directions.nw(1)+directions.se(1)

        #Castling
        if self.colour == 'w':
            if len(directions.e(3)) == 2 and white_kingside_castle:
                all_valid_moves.append((self.row, self.col+2))
            if len(directions.w(4)) == 3 and white_queenside_castle:
                all_valid_moves.append((self.row, self.col-2))

        if self.colour == 'b':
            if len(directions.e(3)) == 2 and black_kingside_castle:
                all_valid_moves.append((self.row, self.col+2))
            if len(directions.w(4)) == 3 and black_queenside_castle:
                all_valid_moves.append((self.row, self.col-2))

        return all_valid_moves

def possible_moves(boardlist, start_pos):
    piece = get_piece(boardlist, start_pos)
    colour = get_colour(piece)
    piecetype = get_piecetype(piece)
    all_valid_moves = []

    piece_manager = PieceManager(start_pos, colour)
    match piecetype:
        case '': return[]
        case 'P': return piece_manager.valid_pawn_moves(boardlist)
        case 'N': return piece_manager.valid_knight_moves(boardlist)
        case 'B': return piece_manager.valid_bishop_moves(boardlist)
        case 'R': return piece_manager.valid_rook_moves(boardlist)
        case 'Q': return piece_manager.valid_queen_moves(boardlist)
        case 'K': return piece_manager.valid_king_moves(boardlist)
    
    return []

#Checks if a move is valid given starting and ending position of move
def valid_moves(boardlist, start_pos: tuple) -> List[tuple]:
    global turn
    
    piece = get_piece(boardlist, start_pos)
    colour = get_colour(piece)
    piecetype = get_piecetype(piece)

    if colour != turn:
        return []
    
    moves = possible_moves(boardlist, start_pos)
    all_valid_moves = legal_check_moves(boardlist, start_pos, colour, moves)
    return all_valid_moves

def promotion_check() -> None:
    global boardlist
    for col, piece in enumerate(boardlist[0]):
        if piece == 'wP':
            boardlist[0][col] = 'wQ'
    
    for col, piece in enumerate(boardlist[7]):
        if piece == 'bP':
            boardlist[7][col] = 'bQ'

def castling_move_check(piece: str, pos: tuple) -> None:
    #Local vars, not global
    white_kingside_castle, white_queenside_castle, black_kingside_castle, black_queenside_castle = True, True, True, True
    if get_piecetype(piece) == 'R':
        match pos:
            case (0,0): black_queenside_castle = False
            case (0,7): black_kingside_castle = False
            case (7,0): white_queenside_castle = False
            case (7,7): white_kingside_castle = False

    if piece == 'wK':
        white_kingside_castle = False
        white_queenside_castle = False
    if piece == 'bK':
        black_kingside_castle = False
        black_queenside_castle = False

    return white_kingside_castle, white_queenside_castle, black_kingside_castle, black_queenside_castle

def check_for_checks(boardlist) -> str:
    for row in range(8):
        for col in range(8):
            pos = (row, col)
            piece = get_piece(boardlist, pos)
            moves = possible_moves(boardlist, pos)
            for move in moves:
                if get_piece(boardlist, move) == 'wK': return 'w'
                if get_piece(boardlist, move) == 'bK': return 'b'
    return ''

def legal_check_moves(boardlist: List[str], pos: tuple, colour: str, possible_moves: List[tuple]):
    all_valid_moves = []
    for possible_move in possible_moves:
            simulated_board = [row[:] for row in boardlist] #Deep copy
            simulated_board = move(simulated_board, pos, possible_move) #Make the move
            if check_for_checks(simulated_board) != colour: #Move is legal if you are not in check after it
                all_valid_moves.append(possible_move)
    return all_valid_moves

#Moves a piece from one position to another in boardlist
def move(boardlist: List[str], start_pos: tuple, end_pos: tuple) -> None:
    start_row, start_col = start_pos
    end_row, end_col = end_pos

    piece_to_move = get_piece(boardlist, start_pos)

    #Castling
    castling_move_check(piece_to_move, start_pos)
    if get_piecetype(piece_to_move) == 'K':
        match (end_col - start_col):

            case 2: boardlist = move(boardlist, (start_row, 7), (start_row, end_col-1)) #Kingside
            case -2: boardlist = move(boardlist, (start_row, 0), (start_row, end_col+1)) #Queenside

    boardlist[end_row][end_col] = piece_to_move #Make ending position the piece
    boardlist[start_row][start_col] = '' #Remove the piece from starting position

    return boardlist

def handle_event(event, board) -> None:
    global boardlist, selected, dragging, turn

    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
        #Get coordinates of the clicked square
        mouse_pos = pg.mouse.get_pos()
        col, row = convert_coords(mouse_pos)

        selected = (row, col)
        if get_piece(boardlist, selected):
            dragging = (row, col)

    if event.type == pg.MOUSEBUTTONUP and event.button == 1:
        dragging = ()
        mouse_pos = pg.mouse.get_pos()
        col, row = convert_coords(mouse_pos)
        end_pos = (row, col)

        colour = get_colour(get_piece(boardlist, selected))
        all_valid_moves = valid_moves(boardlist, selected)

        if end_pos in all_valid_moves and turn == colour:
            boardlist = move(boardlist, selected, end_pos)
            turn = opp_colour(turn)

def main():
    global boardlist, check
    running = True
    board = Board(boardlist)

    while running:
        promotion_check()
        check = check_for_checks(boardlist)                     
        board.draw_squares()
        board.draw_pieces()
        board.draw_legal_moves()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            handle_event(event, board)
        
        if dragging:
            if get_piece(boardlist, dragging):
                mouse_pos = pg.mouse.get_pos()
                board.draw_dragging_piece(mouse_pos)

        pg.display.flip()
    pg.quit()


if __name__ == '__main__':
    main()