#TODO:
#En Passant
#King cannot castle through check
#Underpromotion
#Checkmate and Stalemate
#50 move draw, draw by repetition, draw by insufficient material
#Timer
#Borders & Customization
#Main Menu
#Multiplayer
#AI Engine

import pygame as pg
import os
import math
from typing import List
from typing import Final

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
START_POS: Final[List[str]] = [
    ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
    ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
    ['']*8,
    ['']*8,
    ['']*8,
    ['']*8,
    ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
    ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]

board_list: List[str] = START_POS.copy()

#customization
PIECE_SET = 'cardinal' #cardinal, caifornia(65:80), maestro, staunty, tatiana 
DARK_COLOUR = MID_GRAY
LIGHT_COLOUR = OFF_WHITE
DOT_COLOUR = LIGHT_RED

#flags
turn: str = 'w' #white starts first so initialized as w
selected: tuple[int, int] = () #coordinates of selected square
dragging: tuple[int, int] = ()
check: str = '' #'w' if white is in check, 'b' if black is in check, '' if no check
win: str = '' #'w' if white wins, 'b' if black wins, '' if draw

#whether castling is still available for a colour and side
white_queenside_castle: bool = True
white_kingside_castle: bool = True
black_queenside_castle: bool = True
black_kingside_castle: bool = True

#creating screen
pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Chess")
screen.fill(WHITE)

CODE_DIR = os.path.dirname(__file__)
IMAGES_DIR = os.path.join(CODE_DIR, 'piece', PIECE_SET)

class Board():
    def __init__(self, screen, board_list: List[int]) -> None:
        self.surf = screen
        self.board_list = board_list

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

    
    def draw_pieces(self, dragging: tuple[int, int]) -> None:
        global PIECE_SET, IMAGES_DIR, piece_width, piece_height, square_side
        for row in range(8):
            for col in range(8):
                piece_name = board_list[row][col]
                if piece_name and (row, col) != dragging:
                    img_path = os.path.join(IMAGES_DIR, piece_name+'.svg')

                    img = pg.image.load(img_path)
                    img = pg.transform.smoothscale(img, (piece_width, piece_height))

                    square_rect = pg.Rect(col*square_side, row*square_side, square_side, square_side)
                    piece_rect = img.get_rect(center = square_rect.center)
                    self.surf.blit(img, piece_rect)
    
    def draw_legal_moves(self, selected: tuple[int, int], turn: str) -> None:
        global DOT_COLOUR, square_side
        if selected:
            #fetch colour of selected piece
            colour = get_colour(get_piece(self.board_list, selected))
            #draw dots on all legal moves if piece belongs to player whose turn it is
            if colour == turn:
                all_valid_moves = valid_moves(self.board_list, selected)

                for move in all_valid_moves:
                    row, col = move
                    center = convert_coords_relative_to_abs((row, col))
                    pg.draw.circle(screen, DOT_COLOUR, center, 10)

    def draw_dragging_piece(self, dragging: tuple[int, int], mouse_pos: tuple[int, int]) -> None:
        global IMAGES_DIR
        row, col = dragging
        mx, my = mouse_pos

        piece_name = get_piece(self.board_list, dragging)

        img_path = os.path.join(IMAGES_DIR, piece_name+'.svg')
        img = pg.image.load(img_path)
        img = pg.transform.smoothscale(img, (80, 80))

        img_rect = img.get_rect()
        img_rect.center = (mx, my)
        
        self.surf.blit(img, img_rect)

#-----Utility Functions-----#  
# Converts absolute coordinates to relative coordinates of square eg. (132, 273) -> (1, 2)         
def convert_coords_abs_to_relative(abs_coords: tuple[int, int]) -> tuple[int, int]:
    ax, ay = abs_coords
    relative_coords = (math.floor(ax/100), math.floor(ay/100))
    return relative_coords

# Converts relative coordinates of square to absolute coordinates of its center eg. (1, 2) -> (150, 250)
def convert_coords_relative_to_abs(rel_coords: tuple[int, int]) -> tuple[int, int]:
    global square_side
    row, col = rel_coords
    abs_coords = (col*square_side + square_side//2, row*square_side + square_side//2)
    return abs_coords

def opp_colour(colour) -> None:
    return 'w' if colour == 'b' else 'b'

def get_piece(board_list, pos: tuple[int, int]) -> str:
    row, col = pos
    try:
        return board_list[row][col]
    except IndexError:
        return None
    
def get_colour(piece: str) -> str:
    return piece[0] if piece else ''

def get_piecetype(piece: str) -> str:
    return piece[1] if piece else ''

def within_limits(pos: tuple[int, int]) -> bool:
    if (0 <= pos[0] <= 7) and (0 <= pos[1] <= 7):
        return True
    else:
        return False

#-----Functions to return all legal moves in a certain direction----#
class Directions():
    def __init__(self, board_list: List[str], start_pos: tuple[int, int], colour: str) -> None:
        self.start_pos = start_pos
        self.start_row, self.start_col = self.start_pos
        self.colour = colour
        self.board_list = board_list

    def n(self, limit: int) -> List[tuple[int, int]]:
        all_valid_moves = []
        row = self.start_row-1
        col = self.start_col
        distance = 0

        while row >= 0:

            piece = self.board_list[row][col]
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

    def s(self, limit: int) -> List[tuple[int, int]]:
        all_valid_moves = []
        row = self.start_row+1
        col = self.start_col
        distance = 0

        while row <= 7:
            piece = self.board_list[row][col]
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

    def e(self, limit: int) -> List[tuple[int, int]]:
        all_valid_moves = []
        row = self.start_row
        col = self.start_col+1
        distance = 0

        while col <= 7:
            
            piece = self.board_list[row][col]
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

    def w(self, limit: int) -> List[tuple[int, int]]:
        all_valid_moves = []
        row = self.start_row
        col = self.start_col-1
        distance = 0

        while col >= 0:
            
            piece = self.board_list[row][col]
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

    def ne(self, limit: int) -> List[tuple[int, int]]:
        all_valid_moves = []
        row = self.start_row-1
        col = self.start_col+1
        distance = 0

        while row >= 0 and col <= 7:
            piece = self.board_list[row][col]
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

    def nw(self, limit: int) -> List[tuple[int, int]]:
        all_valid_moves = []
        row = self.start_row-1
        col = self.start_col-1
        distance = 0

        while row >= 0 and col >= 0:
            
            piece = self.board_list[row][col]
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

    def sw(self, limit: int) -> List[tuple[int, int]]:
        all_valid_moves = []
        row = self.start_row+1
        col = self.start_col-1
        distance = 0

        while row <= 7 and col >= 0:
            
            piece = self.board_list[row][col]
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

    def se(self, limit: int) -> List[tuple[int, int]]:
        all_valid_moves = []
        row = self.start_row+1
        col = self.start_col+1
        distance = 0

        while row <= 7 and col <= 7:
            
            piece = self.board_list[row][col]
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
    def __init__(self, pos: tuple[int, int], colour: str) -> List[tuple[int, int]]:
        self.pos = pos
        self.row, self.col = self.pos
        self.colour = colour

    def valid_pawn_moves(self, board_list: List[str]) -> List[tuple[int, int]]:
        #TODO: en passant
        all_valid_moves = []

        if self.colour == 'w':
            n1 = (self.row-1, self.col)
            n2 = (self.row-2, self.col)
            ne = (self.row-1, self.col+1)
            nw = (self.row-1, self.col-1)

            #not blocked 1 square ahead
            if not get_piece(board_list, n1):
                all_valid_moves.append(n1)

                #not blocked 2 squares ahead, and on starting row
                if not get_piece(board_list, n2) and self.row == 6:
                    all_valid_moves.append(n2)

            #can capture diagonally to the right
            if get_colour(get_piece(board_list, ne)) == opp_colour(self.colour):
                all_valid_moves.append(ne)

            #can capture diagonally to the left
            if get_colour(get_piece(board_list, nw)) == opp_colour(self.colour):
                all_valid_moves.append(nw)
            
        if self.colour == 'b':
            s1 = (self.row+1, self.col)
            s2 = (self.row+2, self.col)
            se = (self.row+1, self.col+1)
            sw = (self.row+1, self.col-1)

            #not blocked 1 square ahead
            if not get_piece(board_list, s1):
                all_valid_moves.append(s1)

                #not blocked 2 squares ahead, and on starting row
                if not get_piece(board_list, s2) and self.row == 1:
                    all_valid_moves.append(s2)

            #can capture diagonally to the right
            if get_colour(get_piece(board_list, se)) == opp_colour(self.colour):
                all_valid_moves.append(se)

            #can capture diagonally to the left
            if get_colour(get_piece(board_list, sw)) == opp_colour(self.colour):
                all_valid_moves.append(sw)

        return all_valid_moves

    def valid_knight_moves(self, board_list: List[str]) -> List[tuple[int, int]]:
        all_valid_moves = []
        
        #for a row change of 1, col change is 2 and vice versa, in both positive and negative directions
        for row_change in [1, -1, 2, -2]:
            col_change = 3-abs(row_change) 
            for sign in [1, -1]:
                new_pos = (self.row + row_change, self.col + sign*col_change)
                #Check within limits and not blocked by own piece
                if within_limits(new_pos) and get_colour(get_piece(board_list, new_pos)) != self.colour:
                    all_valid_moves.append(new_pos)

        return all_valid_moves

    def valid_bishop_moves(self, board_list: List[str]) -> List[tuple[int, int]]:

        all_valid_moves = []
        directions = Directions(board_list, self.pos, self.colour)

        all_valid_moves+=directions.ne(8)+directions.sw(8)+directions.nw(8)+directions.se(8)

        return all_valid_moves

    def valid_rook_moves(self, board_list: List[str]) -> List[tuple[int, int]]:
        all_valid_moves = []
        directions = Directions(board_list, self.pos, self.colour)

        all_valid_moves+=directions.n(8)+directions.s(8)+directions.w(8)+directions.e(8)

        return all_valid_moves
        
    def valid_queen_moves(self, board_list: List[str]) -> List[tuple[int, int]]:

        all_valid_moves = []
        directions = Directions(board_list, self.pos, self.colour)

        all_valid_moves+=directions.n(8)+directions.s(8)+directions.w(8)+directions.e(8)
        all_valid_moves+=directions.ne(8)+directions.sw(8)+directions.nw(8)+directions.se(8)

        return all_valid_moves

    def valid_king_moves(self, board_list: List[str]) -> List[tuple[int, int]]:

        global white_kingside_castle, white_queenside_castle, black_kingside_castle, black_queenside_castle
        all_valid_moves = []

        directions = Directions(board_list, self.pos, self.colour)

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

#Returns all possible moves for a piece at start_pos regardless of checks
def possible_moves(board_list: List[str], start_pos: tuple[int, int]) -> List[tuple[int, int]]:
    piece = get_piece(board_list, start_pos)
    colour = get_colour(piece)
    piecetype = get_piecetype(piece)

    piece_manager = PieceManager(start_pos, colour)
    match piecetype:
        case '': return[]
        case 'P': return piece_manager.valid_pawn_moves(board_list)
        case 'N': return piece_manager.valid_knight_moves(board_list)
        case 'B': return piece_manager.valid_bishop_moves(board_list)
        case 'R': return piece_manager.valid_rook_moves(board_list)
        case 'Q': return piece_manager.valid_queen_moves(board_list)
        case 'K': return piece_manager.valid_king_moves(board_list)

#Returns all valid moves for a piece at start_pos, considering checks
def valid_moves(board_list: List[str], start_pos: tuple[int, int]) -> List[tuple[int, int]]:
    global turn
    
    piece = get_piece(board_list, start_pos)
    colour = get_colour(piece)

    if colour != turn:
        return []
    
    moves = possible_moves(board_list, start_pos)
    all_valid_moves = legal_check_moves(board_list, start_pos, colour, moves)
    return all_valid_moves

#Promotes pawns that reach the opposite end to queens
def promotion_check() -> None:
    global board_list
    #Check for white pawns on row 0
    for col, piece in enumerate(board_list[0]):
        if piece == 'wP':
            board_list[0][col] = 'wQ'

    #Check for black pawns on row 7
    for col, piece in enumerate(board_list[7]):
        if piece == 'bP':
            board_list[7][col] = 'bQ'

#Updates castling availability after a king or rook has moved
def castling_move_check(piece: str, pos: tuple[int, int]) -> None:
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

#Checks if either king is in check, returns 'w' if white is in check, 'b' if black is in check, '' if no check
def check_for_checks(board_list: List[str]) -> str:
    for row in range(8):
        for col in range(8):
            pos = (row, col)
            moves = possible_moves(board_list, pos)
            for move in moves:
                if get_piece(board_list, move) == 'wK': return 'w'
                if get_piece(board_list, move) == 'bK': return 'b'
    return ''

#Filters possible moves to only legal moves that do not put (or keep) own king in check
def legal_check_moves(board_list: List[str], pos: tuple[int, int], colour: str, possible_moves: List[tuple[int, int]]):
    all_valid_moves = []
    for possible_move in possible_moves:
            simulated_board = [row[:] for row in board_list] #Deep copy of board_list
            simulated_board = move(simulated_board, pos, possible_move) #Make the move
            if check_for_checks(simulated_board) != colour: #Move is legal if you are not in check after it
                all_valid_moves.append(possible_move)
    return all_valid_moves

#Moves a piece from one position to another in board_list
def move(board_list: List[str], start_pos: tuple[int, int], end_pos: tuple[int, int]) -> List[str]:
    start_row, start_col = start_pos
    end_row, end_col = end_pos

    piece_to_move = get_piece(board_list, start_pos)

    #Castling
    castling_move_check(piece_to_move, start_pos)
    if get_piecetype(piece_to_move) == 'K':
        match (end_col - start_col):
            case 2: board_list = move(board_list, (start_row, 7), (start_row, end_col-1)) #Kingside
            case -2: board_list = move(board_list, (start_row, 0), (start_row, end_col+1)) #Queenside

    board_list[end_row][end_col] = piece_to_move #Make ending position the piece that's moving
    board_list[start_row][start_col] = '' #Remove the piece from starting position

    return board_list

def handle_event(event, board_list: List[str]) -> None:
    global selected, dragging, turn

    #left mouse button down
    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
        #Get coordinates of the clicked square
        mouse_pos = pg.mouse.get_pos()
        col, row = convert_coords_abs_to_relative(mouse_pos)

        selected = (row, col)
        if get_piece(board_list, selected):
            dragging = (row, col)

    #left mouse button up
    if event.type == pg.MOUSEBUTTONUP and event.button == 1:
        dragging = ()
        mouse_pos = pg.mouse.get_pos()
        col, row = convert_coords_abs_to_relative(mouse_pos)
        end_pos = (row, col)

        colour = get_colour(get_piece(board_list, selected))
        all_valid_moves = valid_moves(board_list, selected)

        if end_pos in all_valid_moves and turn == colour:
            board_list = move(board_list, selected, end_pos)
            turn = opp_colour(turn)

def main():
    global board_list, check, dragging, screen, selected, turn
    running = True
    board = Board(screen, board_list)

    while running:
        promotion_check()
        check = check_for_checks(board_list)                     
        board.draw_squares()
        board.draw_pieces(dragging)
        board.draw_legal_moves(selected, turn)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            handle_event(event, board_list)
        
        if dragging:
            if get_piece(board_list, dragging):
                mouse_pos = pg.mouse.get_pos()
                board.draw_dragging_piece(dragging, mouse_pos)

        pg.display.flip()
    pg.quit()


if __name__ == '__main__':
    main()