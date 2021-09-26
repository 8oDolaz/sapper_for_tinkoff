import os
import base64

import numpy as np


class Grid:
    def __init__(self, size_x, size_y, bombs_n):
        self.size = (size_x, size_y)
        self.size_int = size_x * size_y
        self.bombs = bombs_n

        self.grid_bombs = np.array([0] * (self.size_int - self.bombs) + [1] * self.bombs)
        np.random.shuffle(self.grid_bombs)
        self.grid_bombs = self.grid_bombs.reshape(self.size[0], self.size[1])

        self._create_help_grids()

        self.grid_play = np.array(['·'] * self.size_int)
        self.grid_play = self.grid_play.reshape(self.size[0], self.size[1])

    def __print__(self):
        print(' ', end='')
        for board in range(len(self.grid_play[0])):
            print('_', end=' ')
        print()

        for line in self.grid_play:
            print('|', end='')
            for cell_i, cell in enumerate(line):
                if cell == '0': print(' ', end='')
                else: print(cell, end='')
                if cell_i != len(line) - 1:
                    print(' ', end='')
            print('|')

        print(' ', end='')
        for board in range(len(self.grid_play[0])):
            print('‾', end=' ')
        print()

    @staticmethod
    def _encrypt(message):
        message = base64.b64encode(bytes(str(message), 'utf8'))
        return message

    @staticmethod
    def _decrypt(message):
        message = base64.b64decode(message).decode('utf8')
        return message

    def _open_zeros(self, x_cord, y_cord, used):
        self.grid_play[x_cord][y_cord] = '0'
        used.append([x_cord, y_cord])
        for d_x in range(-1, 2):
            for d_y in range(-1, 2):
                if self._check_board(x_cord - d_x, y_cord - d_y):
                    self.grid_play[x_cord - d_x][y_cord - d_y] = self.grid_nearest_bombs[x_cord - d_x][y_cord - d_y]

                    if self.grid_play[x_cord - d_x][y_cord - d_y] == '0' and [x_cord - d_x, y_cord - d_y] not in used:
                        self._open_zeros(x_cord - d_x, y_cord - d_y, used)

    def _check_board(self, x_cord, y_cord):
        if x_cord in range(0, self.size[0]) and y_cord in range(0, self.size[1]):
            return True
        return False

    def _count_nearest_bombs(self, x_cord, y_cord):
        counter = 0
        for d_x in range(-1, 2):
            for d_y in range(-1, 2):
                if not (d_x == 0 and d_y == 0) and self._check_board(x_cord - d_x, y_cord - d_y):
                    if self.grid_bombs[x_cord - d_x][y_cord - d_y] == 1:
                        counter += 1

        return counter

    def _create_help_grids(self):
        self.bombs_cords = []

        self.grid_nearest_bombs = np.array([0] * self.size_int)
        self.grid_nearest_bombs = self.grid_nearest_bombs.reshape(self.size[0], self.size[1])

        for row in range(self.size[0]):
            for column in range(self.size[1]):
                if self.grid_bombs[row][column] == 1:
                    self.bombs_cords.append([row, column])

                self.grid_nearest_bombs[row][column] = self._count_nearest_bombs(row, column)

        self.bombs_cords = sorted(self.bombs_cords)

    def __save__(self, *args):
        for i, grid in enumerate(args):
            with open(f'grid{i+1}.txt', 'wb') as grid_file:
                grid_save = ''
                for row in range(self.size[0]):
                    for column in range(self.size[1]):
                        grid_save += str(grid[row][column]) + ' '
                    grid_save += '\n'

                grid_file.write(self._encrypt(grid_save))
                grid_file.close()

    def __load__(self):
        with open('grid1.txt', 'rb') as file:
            grid_bombs = file.read()
            grid_bombs = self._decrypt(grid_bombs)
            grid_bombs = [
                [*map(int, row.split(' ')[:-1])]
                for row in grid_bombs.split('\n')[:-1]
            ]
            grid_bombs = np.asarray(grid_bombs)
            self.grid_bombs = grid_bombs

        with open('grid2.txt', 'rb') as file:
            grid_play = file.read()
            grid_play = self._decrypt(grid_play)
            grid_play = [
                row.split(' ')[:-1]
                for row in grid_play.split('\n')[:-1]
            ]
            grid_play = np.asarray(grid_play)
            self.grid_play = grid_play

        self.size = (len(self.grid_bombs), len(self.grid_bombs[0]))
        self.size_int = self.size[0] * self.size[1]
        self.bombs = np.sum(self.grid_bombs)

        self._create_help_grids()

    def check_lose(self, x_cord, y_cord):
        if self.grid_bombs[x_cord][y_cord]:
            return True
        return False

    def check_win(self):
        close_flag = []
        for row in range(self.size[0]):
            for column in range(self.size[1]):
                if self.grid_play[row][column] == '⚑' or self.grid_play[row][column] == '·':
                    close_flag.append([row, column])

        if sorted(close_flag) == self.bombs_cords:
            return True
        return False

    def open_cell(self, x_cord, y_cord):
        if self.check_lose(x_cord, y_cord):
            return True

        if self.grid_play[x_cord][y_cord] != '⚑' and (not self.grid_play[x_cord][y_cord].isdigit()):
            self.grid_play[x_cord][y_cord] = self.grid_nearest_bombs[x_cord][y_cord]

        if self.grid_play[x_cord][y_cord] == '0':
            self._open_zeros(x_cord, y_cord, [])

    def flag_cell(self, x_cord, y_cord):
        if not self.grid_play[x_cord][y_cord].isdigit() and self.grid_play[x_cord][y_cord] != '⚑':
            self.grid_play[x_cord][y_cord] = '⚑'

    def undo_cell(self, x_cord, y_cord):
        if self.grid_play[x_cord][y_cord] == '⚑':
            self.grid_play[x_cord][y_cord] = '·'


def game(save):
    if save:
        grid = Grid(0, 0, 0)
        grid.__load__()
        os.remove('grid1.txt')
        os.remove('grid2.txt')
    else:
        grid_params = [*map(int, input('Введите длину, ширину поля и количество бомб:').split(' '))]
        grid = Grid(grid_params[0], grid_params[1], grid_params[2])

    print('''
Вот небольшая инструкция:
    x y open -- открыть ячейку с координатами (x, y)
    x y flag -- поставить флаг на ячейку с координатами (x, y)
    x y undo -- убрать флаг с ячейки с координатами (x, y)
    exit -- закончить игру (сессия будет сохранена)
    ''')

    grid.__print__()

    while True:
        move = input('Твой ход: ').split()

        if move[0] == 'exit':
            grid.__save__(grid.grid_bombs, grid.grid_play)
            return 'Ваша игра сохранена, будем ждать тебя!'

        move_cords = int(move[1]) - 1, int(move[0]) - 1
        move_action = move[2].lower()

        if move_action in ['open', 'flag', 'undo'] and sum(move_cords) in range(grid.size_int):
            if move_action == 'open':
                if grid.open_cell(move_cords[0], move_cords[1]):
                    for cords in grid.bombs_cords:
                        grid.grid_play[cords[0]][cords[1]] = 'B'
                    grid.__print__()
                    return 'Ты проиграл!'
            elif move_action == 'flag':
                grid.flag_cell(move_cords[0], move_cords[1])
            elif move_action == 'undo':
                grid.undo_cell(move_cords[0], move_cords[1])
        else:
            print('Пожалуйста, введите корректную команду')

        if grid.check_win():
            grid.__print__()
            return 'Ты выиграл!'

        grid.__print__()


def main():
    save_param = False
    if os.path.isfile('grid1.txt'):
        print('Похоже, мы нашли твое сохранение. Хочешь загрузить его? ("Да", "Нет")')
        answer = input().lower()
        if answer == 'да':
            save_param = True
        elif answer == 'нет':
            os.remove('grid1.txt')
            os.remove('grid2.txt')
            print('Хорошо, тогда начнем новую игру!')

    print(game(save_param))


if __name__ == '__main__':
    main()
