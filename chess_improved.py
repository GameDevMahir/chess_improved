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

# board lists
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

piece_set = 'cardinal'

#flags
turn: str = ''

class Board():
    def __init__(self, surf) -> None:
        self.surf = surf

    # Draws out the chess board
    def draw_squares(self) -> None:
        for row in range(8):
            for col in range(8):
                if (row % 2 == 0) and (col % 2 == 0):
                    square_colour = WHITE
                elif (row % 2 == 1) and (col % 2 == 1):
                    square_colour = WHITE
                else:
                    square_colour = BLACK

                square_rect = pg.Rect(row*square_side, col*square_side,
                               square_side, square_side)

                pg.draw.rect(self.surf, square_colour, square_rect)
    
    def draw_pieces(self, boardlist, piece_set) -> None:
        for row in range(8):
            for col in range(8):
                piece_name = boardlist[row][col]
                square_rect = pg.Rect(row*square_side, col*square_side, square_side, square_side)
                img_path = f"images\\{piece_set}\\{piece_name}.svg"

                piece_img = pg.image.load(img_path)
                piece_img = pg.transform.smoothscale(self.img, (80, 80))

                img_rect = piece_img.get_rect(center = square_rect.center)
                self.surf.blit(piece_img, piece_rect)
                

def is_valid_move():
    pass

def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    screen.fill(WHITE)
    board = Board(screen)
    running = True
    while running:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mousepos = pg.mouse.get_pos()

        board.draw_squares()
        board.draw_pieces(boardlist, piece_set)

        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()
