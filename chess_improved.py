import pygame as pg
import os
from PIL import Image
import math
from typing import List

#dimensions and sizes
WIDTH: int = 800
HEIGHT: int = 800
square_side: int = WIDTH/8

#colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
OFF_WHITE = (240, 233, 220)
DARK_GRAY = (45, 45, 45)
RED = (255, 0, 0)

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

#customization
piece_set = 'cardinal'
DARK_COLOUR = DARK_GRAY
LIGHT_COLOUR = OFF_WHITE

#flags
turn: str = 'w'
moves = 0
selected = ()
check = False
win = ''

#creating screen
pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Chess")
screen.fill(WHITE)

class Board():
    def __init__(self) -> None:
        global screen
        self.surf = screen

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
                    pg.draw.rect(self.surf, RED, square_rect, 5)

    
    def draw_pieces(self, piece_set) -> None:
        global boardlist
        for row in range(8):
            for col in range(8):
                piece_name = boardlist[row][col]
                if piece_name:
                    square_rect = pg.Rect(col*square_side, row*square_side, square_side, square_side)
                    img_path = f"piece/{piece_set}/{piece_name}.svg"

                    piece_img = pg.image.load(img_path)
                    piece_img = pg.transform.smoothscale(piece_img, (80, 80))

                    piece_rect = piece_img.get_rect(center = square_rect.center)
                    self.surf.blit(piece_img, piece_rect)

#-----Utility Functions-----#  
# Converts absolute coordinates to relative coordinates of square eg. (132, 273) -> (1, 2)         
def convert_coords(abs_coords: tuple) -> tuple:
    ax, ay = abs_coords
    relative_coords = (math.floor(ax/100), math.floor(ay/100))
    return relative_coords

def switch_turn() -> None:
    global turn
    turn = 'w' if turn == 'b' else 'b'

def get_colour(piece: str) -> str:
    return piece[0]

def get_piecetype(piece: str) -> str:
    return piece[1]

#-----Functions to return all legal moves in a certain direction----#
def north_south(start_pos: tuple) -> List[tuple]:
    global boardlist
    start_row, start_col = start_pos
    colour = get_colour(boardlist[start_row][start_col])

def east_west(start_pos: tuple) -> List[tuple]:
    global boardlist
    start_row, start_col = start_pos
    colour = get_colour(boardlist[start_row][start_col])

def north_south(start_pos: tuple) -> List[tuple]:
    global boardlist
    start_row, start_col = start_pos
    colour = get_colour(boardlist[start_row][start_col])

def north_south(start_pos: tuple) -> List[tuple]:
    global boardlist
    start_row, start_col = start_pos
    colour = get_colour(boardlist[start_row][start_col])

#-----Functions to return all legal moves for each piece type-----#

def valid_pawn_move(start_pos: tuple) -> List[tuple]:
    #if row=1 for white or row=6 for black, double forward if no piece 2 ahead
    #single if no piece ahead
    #diagonally left or right 1 step if there is a piece
    #if row=7 for white or row=0 for black, promotion to Q

    global boardlist
    start_row, start_col = start_pos
    colour = get_colour(boardlist[start_row][start_col])
    pass

def valid_knight_moves(start_pos: tuple) -> List[tuple]:
    #L-shape in 8 directions
    global boardlist
    start_row, start_col = start_pos
    colour = get_colour(boardlist[start_row][start_col])

def valid_bishop_moves(start_pos: tuple) -> List[tuple]:
    #Diagonally in 4 directions
    #Any steps until end of board or own piece blocks
    global boardlist
    start_row, start_col = start_pos
    colour = get_colour(boardlist[start_row][start_col])

def valid_rook_moves(start_pos: tuple) -> List[tuple]:
    #Straight in 4 directions
    #Any steps until end of board or own piece blocks
    global boardlist
    start_row, start_col = start_pos
    colour = get_colour(boardlist[start_row][start_col])

def valid_queen_moves(start_pos: tuple) -> List[tuple]:
    #Diagonally or straight in 4 directions
    #Any steps until end of board or own piece blocks
    global boardlist
    start_row, start_col = start_pos
    colour = get_colour(boardlist[start_row][start_col])

def valid_king_moves(start_pos: tuple) -> bool:
    #1 step in any direction if not blocked
    #2 steps to either side if no pieces between king and that rook
    #and king not moved, that rook not moved
    global boardlist
    start_row, start_col = start_pos  
    colour = get_colour(boardlist[start_row][start_col])

#Checks if a move is valid given starting and ending position of move
def valid_moves(start_pos: tuple) -> List[tuple]:
    global boardlist, turn, check
    start_row, start_col = start_pos
    end_row, end_col = end_pos
    piece = boardlist[row][col]
    end_piece = boardlist[end_row][end_col]
    colour = get_colour(piece)
    piecetype = get_piecetype(piece)

    end_colour = get_colour(end_piece) if end_piece else ''

    if colour != turn: #Not your turn/moving opponent's piece
        return []
    if end_colour == colour: #Capturing own piece
        return []

    match piecetype:
        case 'n': return valid_knight_moves(start_pos, end_pos)
        case 'b': return valid_bishop_moves(start_pos, end_pos)
        case 'p': return valid_pawn_moves(start_pos, end_pos)
        case 'r': return valid_rook_moves(start_pos, end_pos)
        case 'q': return valid_queen_moves(start_pos, end_pos)
        case 'k': return valid_king_moves(start_pos, end_pos)

#Moves a piece from one position to another in boardlist
def move(start_pos: tuple, end_pos: tuple) -> None:
    global boardlist, moves
    start_row, start_col = start_pos
    end_row, end_col = end_pos

    boardlist[end_row][end_col] = boardlist[start_row][start_col] #Make ending position the piece
    boardlist[start_row][start_col] = '' #Remove the piece from starting position

    moves += 1
    switch_turn()

def highlight_legal_moves(piece_pos: tuple) -> None:
    pass

def handle_event(event) -> None:
    global selected

    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
        #Get coordinates of the clicked square
        mousepos = pg.mouse.get_pos()
        col, row = convert_coords(mousepos)
        new_selected = (row, col)
        
        #Check that a square is selected
        if selected:
            selected_row, selected_col = selected

            #If non-empty square is selected, highlight all legal moves
            if boardlist[selected_row][selected_col]:
                highlight_legal_moves(selected)
                #Move if move is valid
                if new_selected in valid_moves(selected): move(selected, new_selected)

        selected = new_selected #Select the square that was moved to

def main():
    global selected, boardlist
    running = True
    board = Board()

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            handle_event(event)
                            
        board.draw_squares()
        board.draw_pieces(piece_set)

        pg.display.flip()
    pg.quit()


if __name__ == '__main__':
    main()