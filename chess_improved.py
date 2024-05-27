import pygame
import os
from PIL import Image
import math
from typing import List


WIDTH: int = 800
HEIGHT: int = 800

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
OFF_WHITE = (240, 233, 220)

# colour(b/w), piece, identifier no.
START_POS: List[str] = [
    ['bR1', 'bN1', 'bB1', 'bQ0', 'bK0', 'bB2', 'bN2', 'bR2'],
    ['bP0', 'bP0', 'bP0', 'bP0', 'bP0', 'bP0', 'bP0', 'bP0'],
    ['']*8,
    ['']*8,
    ['']*8,
    ['']*8,
    ['wP0', 'wP0', 'wP0', 'wP0', 'wP0', 'wP0', 'wP0', 'wP0'],
    ['wR1', 'wN1', 'wB1', 'wQ0', 'wK0', 'wB2', 'wN2', 'wR2']]

square_side: int = WIDTH/8

boardlist: List[str] = START_POS.copy()
turn: str = ''


class Board():
    def __init__(self, surf, boardlist) -> None:
        self.surf = surf
        self.boardlist = boardlist

    # Draws out the chess board
    def draw(self) -> None:
        for i in range(8):
            for j in range(8):
                if (i % 2 == 0) and (j % 2 == 0):
                    square_colour = WHITE
                elif (i % 2 == 1) and (j % 2 == 1):
                    square_colour = WHITE
                else:
                    square_colour = BLACK

                square_rect = (i*square_side, j*square_side,
                               square_side, square_side)

                pygame.draw.rect(self.surf, square_colour, square_rect)


class Piece():
    pass


def isValidMove():
    pass


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    screen.fill(WHITE)
    running = True
    while running:
        board = Board(screen, boardlist)
        board.draw()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mousepos = pygame.mouse.get_pos()

        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()
