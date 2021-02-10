import numpy as np
import pygame
from typing import Callable


class Color:
    white = (255, 255, 255)
    blue = (0, 0, 139)
    red = (178, 34,34)
    green = (0, 200, 0)
    bright_red = (255, 0, 0)
    bright_green = (0, 255, 0)
    black = (0, 0, 0)
    gray = (80, 80, 80)
    yellow = (240, 230, 140)


class Game:
    """Conventionally, the player who sends the invitation, starts the game!"""
    def __init__(self, row_count: int, column_count: int, square_size: int):
        self.row_count: int = row_count
        self.column_count: int = column_count
        self.square_size: int = square_size
        self.radius: int = int(self.square_size / 2 - 5)
        self.matrix = np.zeros((self.row_count, self.column_count))
        self.font = None
        self.width: int = self.column_count * self.square_size
        self.height: int = (self.row_count + 1) * self.square_size
        self.screen = None

    def available_row(self, col) -> int:
        for row in range(self.row_count):
            if self.matrix[row][col] == 0:
                return row

    def display_matrix(self):
        # TODO renkleri dusun
        for c in range(self.column_count):
            for r in range(self.row_count):
                pygame.draw.rect(self.screen, Color.blue, (c * self.square_size, r * self.square_size
                                                           + self.square_size, self.square_size, self.square_size))
                pygame.draw.circle(self.screen, Color.black, (int(c * self.square_size + self.square_size / 2),
                                                              int(r * self.square_size + self.square_size
                                                                  + self.square_size / 2)), self.radius)

        for c in range(self.column_count):
            for r in range(self.row_count):
                if self.matrix[r][c] == 1:  # 1 represents the pieces that "I", the player who runs the program, dropped
                    pygame.draw.circle(self.screen, Color.red, (int(c * self.square_size + self.square_size / 2),
                                                                self.height - int(
                                                                    r * self.square_size + self.square_size / 2)),
                                       self.radius)
                elif self.matrix[r][c] == 2:  # 2 represents the pieces that my opponent dropped
                    pygame.draw.circle(self.screen, Color.yellow, (int(c * self.square_size + self.square_size / 2),
                                                                   self.height - int(
                                                                       r * self.square_size + self.square_size / 2)),
                                       self.radius)

    def is_game_over(self, piece):  # TODO bu isim aynı mıydı?
        func: Callable
        for func in [self.horizontal_win, self.vertical_win, self.positive_sloped, self.negative_sloped]:
            if func(piece):
                return True
        return False

    def horizontal_win(self, piece):
        for c in range(self.column_count - 3):
            for r in range(self.row_count):
                if self.matrix[r][c] == piece and self.matrix[r][c + 1] == piece \
                        and self.matrix[r][c + 2] == piece and self.matrix[r][c + 3] == piece:
                    return True

    def vertical_win(self, piece):
        for c in range(self.column_count):
            for r in range(self.row_count - 3):
                if self.matrix[r][c] == piece and self.matrix[r + 1][c] == piece \
                        and self.matrix[r + 2][c] == piece and self.matrix[r + 3][c] == piece:
                    return True

    def positive_sloped(self, piece):
        for c in range(self.column_count - 3):
            for r in range(self.row_count - 3):
                if self.matrix[r][c] == piece and self.matrix[r + 1][c + 1] == piece and \
                        self.matrix[r + 2][c + 2] == piece and self.matrix[r + 3][c + 3] == piece:
                    return True

    def negative_sloped(self, piece):
        for c in range(self.column_count - 3):
            for r in range(3, self.row_count):
                if self.matrix[r][c] == piece and self.matrix[r - 1][c + 1] == piece \
                        and self.matrix[r - 2][c + 2] == piece and self.matrix[r - 3][c + 3] == piece:
                    return True
