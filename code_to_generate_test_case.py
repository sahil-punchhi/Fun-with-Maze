from random import seed, randrange, choice
import os

path = "/Users/sahilpunchhi/Desktop/COMP 9021 POP/Assignments/Assignment 2/Testing/"
os.chdir(path)
cwd = os.getcwd()

file_name = 'test_13'
y_dim = 38 # max 41 # min 2
x_dim = 31 # max 31 # min 2
arg_seed = 6000

seed(arg_seed)
grid = [[randrange(4) for _ in range(x_dim)] for _ in range(y_dim)]

for i in range(len(grid)):
    if grid[i][len(grid[0]) - 1] in (1, 3):
        grid[i][len(grid[0]) - 1] = choice((0, 2))

for i in range(len(grid[0])):
    if grid[len(grid)-1][i] in (2, 3):
        grid[len(grid) - 1][i] = choice((0, 1))

def display_grid():
    for i in range(y_dim):
        print('     ', end = '')
        for j in range(x_dim):
            print(grid[i][j], end = '')
            print(' ', end = '')
        print()

#display_grid()

string = str()

for i in range(y_dim):
    string += '     '
    for j in range(x_dim):
        string += f'{grid[i][j]}'
        string += ' '
    string += '\n'
print(string)

with open(f'{path}\\{file_name}.txt', 'w') as file:
    file.write(string)


