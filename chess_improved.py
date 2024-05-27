import pygame as pg
from typing import List

WIDTH: int = 800
HEIGHT: int = 800
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

DARK_GRAY = (65, 65, 65)
OFF_WHITE = (240, 233, 220)

DARK_COLOUR = DARK_GRAY
LIGHT_COLOUR = OFF_WHITE

RED = (255,0,0)

piece_set = 'cardinal'
# colour(b/w), piece type
START_POS: List[str] = [
    ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
    ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
    ['']*8,
    ['']*8,
    ['']*8,
    ['']*8,
    ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
    ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]

square_side: int = WIDTH/8
squares = [[] for i in range(8)]
pieces = []

selected: tuple = ()
boardlist: List[str] = START_POS.copy()
turn: str = ''
running: bool = True

class Board():
    def __init__(self, surf, boardlist) -> None:
        self.surf = surf
        self.boardlist = boardlist

    def create_squares(self) -> None:
        for i in range(8):
            for j in range(8):
                square = Square(self.surf, i, j)
    
    def create_pieces(self) -> None:
        global square_sid
        for i in range(8):
            for j in range(8):
                piece_str = boardlist[i][j]
                colour = self.piece_str[0]
                piece_type = self.piece_str[1]

                img_path = f'piece/{piece_set}/{self.occupying_piece_str}.svg'
                rect = (i*8, j*8, square_side, square_side)

                match piece_type:
                    case 'P': self.piece = Pawn(colour, rect, img_path, self.surf)
                    case 'N': self.piece = Knight(colour, rect, img_path, self.surf)
                    case 'B': self.piece = Bishop(colour, rect, img_path, self.surf)
                    case 'R': self.piece = Rook(colour, rect, img_path, self.surf)
                    case 'Q': self.piece = Queen(colour, rect, img_path, self.surf)
                    case 'K': self.piece = King(colour, rect, img_path, self.surf)

    def update(self) -> None:
        global squares
        for row in squares:
            for square in row:
                square.draw()
        for i in range(8):
            for j in range(8):
                boardlist[i][j]

class Square():
    def __init__(self, surf, row, col):
        self.surf = surf
        self.row, self.col = row, col
        self.rect = pg.Rect(self.col*square_side, self.row*square_side, square_side, square_side) 
        squares[self.row].append(self)
        self.selected: bool = False

    def draw(self) -> None:
        global selected

        #Deciding colour of square
        if (self.row % 2 == 0) and (self.col % 2 == 0):
            self.colour = LIGHT_COLOUR
        elif (self.row % 2 == 1) and (self.col % 2 == 1):
            self.colour = LIGHT_COLOUR
        else:
            self.colour = DARK_COLOUR

        #Drawing out the square
        pg.draw.rect(self.surf, self.colour, self.rect)

        if selected == (self.row, self.col):
            pg.draw.rect(self.surf, RED, self.rect, 5)
            self.selected = True
        else:
            self.selected = False

class Piece():
    def __init__(self, colour, rect, img_path, surf):
        self.colour = colour
        self.rect = rect
        self.img_path = img_path
        self.surf = surf

    def move(startpos, endpos) -> None:
        pass

    def draw(self) -> None:
        self.img = pg.image.load(self.img_path)
        self.img = pg.transform.smoothscale(self.img, (80, 80))
        self.rect = self.img.get_rect(center = self.rect.center)
        self.surf.blit(self.img, self.rect)

class Pawn(Piece):
    def __init__(self, colour, rect, img_path, surf):
        super().__init__(colour, rect, img_path, surf)

class Knight(Piece):
    def __init__(self, colour, rect, img_path, surf):
        super().__init__(colour, rect, img_path, surf)

class Bishop(Piece):
    def __init__(self, colour, rect, img_path, surf):
        super().__init__(colour, rect, img_path, surf)

class Rook(Piece):
    def __init__(self, colour, rect, img_path, surf):
        super().__init__(colour, rect, img_path, surf)

class Queen(Piece):
    def __init__(self, colour, rect, img_path, surf):
        super().__init__(colour, rect, img_path, surf)

class King(Piece):
    def __init__(self, colour, rect, img_path, surf):
        super().__init__(colour, rect, img_path, surf)

def isValidMove():
    pass

def handle_event(event) -> None:
    global running, selected
    if event.type == pg.QUIT:
        running = False
    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
        mousepos = pg.mouse.get_pos()
        for row in squares:
            for square in row:
                if square.rect.collidepoint(mousepos):
                    selected = (square.row, square.col)

def main():
    global running
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Chess")
    clock = pg.time.Clock()
    screen.fill(WHITE)
    board = Board(screen, boardlist)
    board.create_squares()

    #Main loop
    while running:
        board.update()

        for event in pg.event.get():
            handle_event(event)
         
        pg.display.flip()
    pg.quit()


if __name__ == '__main__':
    main()
