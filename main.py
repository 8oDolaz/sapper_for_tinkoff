from grid import Grid

import os


def remove_save(*args):
    for file in args:
        os.remove(file)


def game(save):
    if save:
        grid = Grid(0, 0, 0)
        grid.__load__()
        remove_save('grid1.txt', 'grid2.txt')
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
            remove_save('grid1.txt', 'grid2.txt')
            print('Хорошо, тогда начнем новую игру!')

    print(game(save_param))


if __name__ == '__main__':
    main()
