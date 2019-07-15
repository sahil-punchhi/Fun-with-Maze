import sys
import os
from copy import deepcopy
from collections import defaultdict, deque


# change current working directory
# path = "/Users/sahilpunchhi/Desktop/COMP 9021 POP/Assignments/Assignment 2"
# path2 = "/Users/sahilpunchhi/Desktop/COMP 9021 POP/Assignments/Assignment 2/Testing"
# os.chdir(path2)
# cwd = os.getcwd()

# import time
# start_time = time.time()


class Queue:
    min_capacity = 10

    def __init__(self, capacity=min_capacity):
        self.min_capacity = capacity
        self._data = [None] * capacity
        self._length = 0
        self._front = 0

    def __len__(self):
        return self._length

    def is_empty(self):
        return self._length == 0

    def enqueue(self, datum):
        if self._length == len(self._data):
            self._resize(2 * len(self._data))
        self._data[(self._front + self._length) % len(self._data)] = datum
        self._length += 1

    def dequeue(self):
        if self.is_empty():
            raise EmptyQueueError('Cannot dequeue from empty queue')
        datum_at_front = self._data[self._front]
        # Not necessary, only done to possibly hasten garbage collection
        # of element being removed from the deque.
        self._data[self._front] = None
        self._front = (self._front + 1) % len(self._data)
        self._length -= 1
        self._shrink_if_needed()
        return datum_at_front

    def _resize(self, new_size):
        # In any case, the element at position self._front will be at position 0 in new list.
        end = self._front + new_size
        # We are shrinking to a smaller list, and not wrapping in original list.
        if end <= len(self._data):
            self._data = self._data[self._front: end]
        # We are shrinking to a smaller list, but wrapping in original list.
        elif new_size <= len(self._data):
            # There are len(self._data) - self._front data in self._data[self._front: ],
            # and new_size - (len(self._data) - self._front) == end - len(self._data).
            self._data = self._data[self._front:] + self._data[: end - len(self._data)]
        # We are expanding to a larger list.
        else:
            # The first two lists have a total length of len(self._data).
            self._data = (self._data[self._front:] + self._data[: self._front] +
                          [None] * (new_size - len(self._data)))
        self._front = 0

    def _shrink_if_needed(self):
        # When the queue is one quarter full, we reduce its size to make it half full,
        # provided that it would not reduce its capacity to less than the minimum required.
        if self.min_capacity // 2 <= self._length <= len(self._data) // 4:
            self._resize(len(self._data) // 2)


class MazeError(Exception):
    def __init__(self, message):
        self.message = message


class Maze:
    def __init__(self, some_filename):
        self.some_filename = some_filename

        try:
            with open(some_filename) as input_file:
                lines = input_file.readlines()
                temp_grid = []
                for row in lines:
                    if not row.isspace():
                        temp_grid.append(row.split())
            str1 = str()
            grid = []
            for i in range(len(temp_grid)):
                for j in range(len(temp_grid[i])):
                    str1 += temp_grid[i][j]
                grid.append(str1)
                str1 = ''
            grid = [list(s) for s in grid]
            grid = [[int(element) for element in row] for row in grid]
            self.grid = grid
            y_dim = len(grid)
            x_dim = len(grid[0])

            if y_dim < 2 or y_dim > 41 or x_dim < 2 or x_dim > 31:
                raise MazeError('Incorrect input.')

            for i in range(len(grid)):
                if len(grid[i]) != x_dim:
                    raise MazeError('Incorrect input.')

            for i in range(len(grid)):
                for j in range(len(grid[i])):
                    if grid[i][j] not in (0, 1, 2, 3):
                        raise MazeError('Incorrect input.')
                    if grid[len(grid) - 1][j] in (2, 3):
                        raise MazeError('Input does not represent a maze.')
                    if grid[i][len(grid[0]) - 1] in (1, 3):
                        raise MazeError('Input does not represent a maze.')

            # to find total number of cells
            points = (y_dim - 1) * (x_dim - 1)
            self.points = points

            # creating dictionary of all connected coordinates
            # this dictionary does not contain those coordinates in keys which are not connected to any other coordinates
            connects = defaultdict(list)
            for i in range(len(self.grid)):
                for j in range(len(self.grid[0])):

                    if self.grid[i][j] in (1, 3):
                        if not (i < 0 or j + 1 < 0):
                            connects[(i, j)].append((i, j + 1))
                    if self.grid[i][j - 1] in (1, 3):
                        if not (i < 0 or j - 1 < 0):
                            connects[(i, j)].append((i, j - 1))
                    if self.grid[i - 1][j] in (2, 3):
                        if not (i - 1 < 0 or j < 0):
                            connects[(i, j)].append((i - 1, j))
                    if self.grid[i][j] in (2, 3):
                        if not (i + 1 < 0 or j < 0):
                            connects[(i, j)].append((i + 1, j))

            self.connects = connects

            connects1 = connects.copy()
            self.connects1 = connects1

            # to find all pillar coordinates
            not_pillars = []
            all_points = []
            for key in self.connects:
                not_pillars.append(key)
            for i in range(len(grid)):
                for j in range(len(grid[0])):
                    all_points.append((i, j))
            pillars = [x for x in all_points if x not in not_pillars]
            self.pillars = pillars

            # to find all pillar cells
            pillar_cells = []
            for (x, y) in pillars:
                if x - 1 >= 0 and y - 1 >= 0 and x - 1 < len(grid) - 1 and y < len(grid[0]):
                    pillar_cells.append(((x - 1, y - 1), (x - 1, y)))
                if x - 1 >= 0 and y >= 0 and x - 1 < len(grid) - 1 and y + 1 < len(grid[0]):
                    pillar_cells.append(((x - 1, y), (x - 1, y + 1)))
                if x >= 0 and y - 1 >= 0 and x < len(grid) - 1 and y < len(grid[0]):
                    pillar_cells.append(((x, y - 1), (x, y)))
                if x >= 0 and y >= 0 and x < len(grid) - 1 and y + 1 < len(grid[0]):
                    pillar_cells.append(((x, y), (x, y + 1)))
            self.pillar_cells = pillar_cells

            # creating dictionary of all connected cells
            cells = defaultdict(list)
            for i in range(len(self.grid) - 1):
                for j in range(len(self.grid[0]) - 1):
                    cells[((i, j), (i, j + 1))] = []
                    if (i + 1, j + 1) not in connects1[i, j + 1]:
                        if i >= 0 and j + 1 >= 0 and i < len(self.grid) - 1 and j + 2 < len(self.grid[0]):
                            cells[((i, j), (i, j + 1))].append(((i, j + 1), (i, j + 2)))

                    if (i + 1, j + 1) not in connects1[i + 1, j]:
                        if i + 1 >= 0 and j >= 0 and i + 1 < len(self.grid) - 1 and j + 1 < len(self.grid[0]):
                            cells[((i, j), (i, j + 1))].append(((i + 1, j), (i + 1, j + 1)))

                    if (i + 1, j) not in connects1[i, j]:
                        if i >= 0 and j - 1 >= 0 and i < len(self.grid) - 1 and j < len(self.grid[0]):
                            cells[((i, j), (i, j + 1))].append(((i, j - 1), (i, j)))

                    if (i, j + 1) not in connects1[i, j]:
                        if i - 1 >= 0 and j >= 0 and i - 1 < len(self.grid) - 1 and j + 1 < len(self.grid[0]):
                            cells[((i, j), (i, j + 1))].append(((i - 1, j), (i - 1, j + 1)))

            self.cells = cells

            # creating dictionary of all connected cells to find number of exits from each cell
            # we make this dictionary only to find number of exits from each cell (used for cul-de-sacs)
            # in all other cases for cell references -dictionary 'cells' will be used
            exits_cells = defaultdict(list)
            for i in range(len(self.grid) - 1):
                for j in range(len(self.grid[0]) - 1):
                    exits_cells[((i, j), (i, j + 1))] = []
                    if (i + 1, j + 1) not in connects1[i, j + 1]:
                        if i >= -1 and j + 1 >= -1 and i < len(self.grid) and j + 2 < len(self.grid[0]) + 1:
                            exits_cells[((i, j), (i, j + 1))].append(((i, j + 1), (i, j + 2)))

                    if (i + 1, j + 1) not in connects1[i + 1, j]:
                        if i + 1 >= -1 and j >= -1 and i + 1 < len(self.grid) and j + 1 < len(self.grid[0]) + 1:
                            exits_cells[((i, j), (i, j + 1))].append(((i + 1, j), (i + 1, j + 1)))

                    if (i + 1, j) not in connects1[i, j]:
                        if i >= -1 and j - 1 >= -1 and i < len(self.grid) and j < len(self.grid[0]) + 1:
                            exits_cells[((i, j), (i, j + 1))].append(((i, j - 1), (i, j)))

                    if (i, j + 1) not in connects1[i, j]:
                        if i - 1 >= -1 and j >= -1 and i - 1 < len(self.grid) and j + 1 < len(self.grid[0]) + 1:
                            exits_cells[((i, j), (i, j + 1))].append(((i - 1, j), (i - 1, j + 1)))

            exits = {}
            for key, value in exits_cells.items():
                exits[key] = len(value)

            self.exits = exits

            # to find gate cells
            gates = []
            for j in range(len(grid[0]) - 1):
                if grid[0][j] in (0, 2):
                    gates.append(((0, j), (0, j + 1)))
            for j in range(len(grid[0]) - 1):
                if grid[len(grid) - 1][j] in (0, 2):
                    gates.append(((len(grid) - 2, j), (len(grid) - 2, j + 1)))
            for i in range(len(grid) - 1):
                if grid[i][0] in (0, 1):
                    gates.append(((i, 0), (i, 1)))
            for i in range(len(grid) - 1):
                if grid[i][len(grid[0]) - 1] in (0, 1):
                    gates.append(((i, len(grid[0]) - 2), (i, len(grid[0]) - 1)))
            self.gates = gates

            # to find corner cells
            corners = [((0, 0), (0, 1)), \
                       ((0, len(grid[0]) - 2), (0, len(grid[0]) - 1)), \
                       ((len(grid) - 2, 0), (len(grid) - 2, 1)), \
                       ((len(grid) - 2, len(grid[0]) - 2), (len(grid) - 2, len(grid[0]) - 1))]
            self.corners = corners

        except FileNotFoundError:
            sys.exit()

    def analyse(self):

        # to find number of gates
        number_of_gates = len(self.gates)
        if number_of_gates == 0:
            print('The maze has no gate.')
        elif number_of_gates == 1:
            print('The maze has a single gate.')
        else:
            print(f'The maze has {number_of_gates} gates.')

        # to find number of connected walls
        queue = Queue()
        number_of_walls = 0
        visited_points = []
        walls = []
        for key in self.connects:
            if key not in visited_points:
                queue.enqueue(key)
                wall = []
                while not queue.is_empty():  # breadth first search algorithm
                    node = queue.dequeue()
                    visited_points.append(node)
                    wall.append(node)
                    if node in self.connects:
                        for child in (self.connects[node]):
                            if child not in visited_points:
                                queue.enqueue(child)
                            else:
                                continue
                number_of_walls += 1
                walls.append(wall)
        # print(walls)

        if number_of_walls == 0:
            print('The maze has no wall.')
        elif number_of_walls == 1:
            print('The maze has walls that are all connected.')
        else:
            print(f'The maze has {number_of_walls} sets of walls that are all connected.')

        # to find no of inaccessible points and no of accessible areas
        queue1 = Queue()
        number_of_accessible_areas = 0
        visited_cells = []
        accessible_spaces = []
        for key1 in self.cells:
            if key1 not in visited_cells:
                queue1.enqueue(key1)
                spaces = []

                while not queue1.is_empty():  # breadth first search algorithm
                    node1 = queue1.dequeue()
                    visited_cells.append(node1)
                    spaces.append(node1)
                    if node1 in self.cells:
                        for child1 in (self.cells[node1]):
                            if child1 not in visited_cells:
                                queue1.enqueue(child1)
                for i in range(len(self.gates)):  # if gate occurs in spaces, means it is accessible
                    if self.gates[i] in spaces:
                        number_of_accessible_areas += 1
                        accessible_spaces.append(spaces)
                        break
        accessible_cells2 = [item for sublist in accessible_spaces for item in
                             sublist]  # creating a flat list of all accessible cells
        accessible_cells = set(accessible_cells2)  # creating a unique list of all accessible cells
        number_of_inaccessible_cells = self.points - len(accessible_cells)

        if number_of_inaccessible_cells == 0:
            print('The maze has no inaccessible inner point.')
        elif number_of_inaccessible_cells == 1:
            print('The maze has a unique inaccessible inner point.')
        else:
            print(f'The maze has {number_of_inaccessible_cells} inaccessible inner points.')

        if number_of_accessible_areas == 0:
            print('The maze has no accessible area.')
        elif number_of_accessible_areas == 1:
            print('The maze has a unique accessible area.')
        else:
            print(f'The maze has {number_of_accessible_areas} accessible areas.')

        # to find cul-de-sacs cells
        cul_de_sacs_dict = self.exits.copy()

        cells_visited = []
        for key2 in cul_de_sacs_dict:
            if (cul_de_sacs_dict[key2] == 1) and (key2 in accessible_cells) and (key2 not in cells_visited):
                cul_de_sacs_dict[key2] = 5
                queue2 = Queue()
                queue2.enqueue(key2)
                while len(queue2) == 1:
                    node2 = queue2.dequeue()
                    cells_visited.append(node2)
                    if node2 in self.cells:
                        for child2 in self.cells[node2]:
                            if child2 not in cells_visited:
                                queue2.enqueue(child2)
                                if cul_de_sacs_dict[child2] == 2:
                                    cul_de_sacs_dict[child2] = 5
                                    cells_visited.append(child2)
                                else:
                                    cul_de_sacs_dict[child2] = cul_de_sacs_dict[child2] - 1
                                    queue2.enqueue(
                                        child2)  # enqueuing dummy child2 so that length of queue becomes more than 1

        # to find number of sets of cul-de-sacs points all connected
        queue3 = Queue()
        number_of_cul_de_sacs_sets = 0
        visited_cul_de_sacs_points = []
        for key3 in cul_de_sacs_dict:
            if (key3 not in visited_cul_de_sacs_points) and (cul_de_sacs_dict[key3] == 5):
                queue3.enqueue(key3)
                while not queue3.is_empty():  # breadth first search algorithm
                    node3 = queue3.dequeue()
                    visited_cul_de_sacs_points.append(node3)
                    if node3 in self.cells:
                        for child3 in (self.cells[node3]):
                            if (child3 not in visited_cul_de_sacs_points) and (cul_de_sacs_dict[child3] == 5):
                                queue3.enqueue(child3)
                            else:
                                continue
                number_of_cul_de_sacs_sets += 1

        if number_of_cul_de_sacs_sets == 0:
            print('The maze has no accessible cul-de-sac.')
        elif number_of_cul_de_sacs_sets == 1:
            print('The maze has accessible cul-de-sacs that are all connected.')
        else:
            print(f'The maze has {number_of_cul_de_sacs_sets} sets of accessible cul-de-sacs that are all connected.')

        # to find number of unique paths # if value in dictionary is '5' meaning it is cul-de-sac or inaccessible
        unique_paths_dict = {}
        for key in cul_de_sacs_dict:
            if key not in accessible_cells:
                unique_paths_dict[key] = 5
            elif (key in cul_de_sacs_dict) and cul_de_sacs_dict[key] == 5:
                unique_paths_dict[key] = 5
            else:
                unique_paths_dict[key] = cul_de_sacs_dict[key]

        # to find number of unique paths
        queue4 = Queue()
        number_of_unique_paths = 0
        visited_unique_path_points = []
        unique_paths = []
        for key4 in unique_paths_dict:
            if (key4 not in visited_unique_path_points) and (unique_paths_dict[key4] == 2) and (key4 in self.gates):
                queue4.enqueue(key4)
                unique_path = []
                while not queue4.is_empty():  # breadth first search algorithm
                    node4 = queue4.dequeue()
                    visited_unique_path_points.append(node4)
                    unique_path.append(node4)
                    if node4 in self.cells:
                        for child4 in (self.cells[node4]):
                            if (child4 not in visited_unique_path_points) and (unique_paths_dict[child4] == 2):
                                queue4.enqueue(child4)
                            else:
                                continue
                if node4 in self.gates:
                    if (len(unique_path) == 1) and (key4 in self.pillar_cells) and (key4 in self.corners):
                        g = key4
                        if g[0][0] == 0 and g[0][1] == 0:  # means top left corner
                            if g[0] in self.pillars:
                                number_of_unique_paths += 1
                                unique_paths.append(unique_path)

                        elif g[0][0] == 0 and (g[0][1] != 0):  # means top right corner
                            if g[1] in self.pillars:
                                number_of_unique_paths += 1
                                unique_paths.append(unique_path)

                        elif g[0][1] == 0 and (g[0][0] != 0):  # means bottom left corner
                            if (g[0][0] + 1, g[0][1]) in self.pillars:
                                number_of_unique_paths += 1
                                unique_paths.append(unique_path)

                        elif g[0][0] != 0 and g[0][1] != 0 and g[1][0] != 0 and g[1][
                            1] != 0:  # means bottom right corner
                            if (g[1][0] + 1, g[1][1]) in self.pillars:
                                number_of_unique_paths += 1
                                unique_paths.append(unique_path)
                    elif len(unique_path) > 1:
                        number_of_unique_paths += 1
                        unique_paths.append(unique_path)

        # print(unique_paths)

        if number_of_unique_paths == 0:
            print('The maze has no entry-exit path with no intersection not to cul-de-sacs.')
        elif number_of_unique_paths == 1:
            print('The maze has a unique entry-exit path with no intersection not to cul-de-sacs.')
        else:
            print(f'The maze has {number_of_unique_paths} entry-exit paths with no intersections not to cul-de-sacs.')

    def display(self):

        # longest horizontal pairs (walls)
        single_hor_pair = []
        horizontal_pairs = []
        for m in range(len(self.grid)):
            k = 0
            while k < len(self.grid[0]):
                if (m, k + 1) in self.connects[(m, k)]:
                    single_hor_pair.append((k, m))
                    k += 1
                    if k < len(self.grid[0]):
                        while (m, k + 1) in self.connects[(m, k)]:
                            k += 1
                            if k >= len(self.grid[0]):
                                break
                        single_hor_pair.append((k, m))
                        horizontal_pairs.append(single_hor_pair)
                        single_hor_pair = []
                        k += 1
                    else:
                        single_hor_pair.append((k, m))
                        horizontal_pairs.append(single_hor_pair)
                        single_hor_pair = []
                else:
                    k += 1

        # print(horizontal_pairs)

        # longest vertical pairs (walls)
        single_ver_pair = []
        vertical_pairs = []
        for k in range(len(self.grid[0])):
            m = 0
            while m < len(self.grid):
                if (m + 1, k) in self.connects[(m, k)]:
                    single_ver_pair.append((k, m))
                    m += 1
                    if m < len(self.grid):
                        while (m + 1, k) in self.connects[(m, k)]:
                            m += 1
                            if m >= len(self.grid):
                                break
                        single_ver_pair.append((k, m))
                        vertical_pairs.append(single_ver_pair)
                        single_ver_pair = []
                        m += 1
                    else:
                        single_ver_pair.append((k, m))
                        vertical_pairs.append(single_ver_pair)
                        single_ver_pair = []
                else:
                    m += 1

        # print(vertical_pairs)

        # all pillars
        display_pillars = [(x, y) for (y, x) in self.pillars]
        # print(display_pillars)

        # to find no of inaccessible points and no of accessible areas
        queue1 = Queue()
        number_of_accessible_areas = 0
        visited_cells = []
        accessible_spaces = []
        for key1 in self.cells:
            if key1 not in visited_cells:
                queue1.enqueue(key1)
                spaces = []

                while not queue1.is_empty():  # breadth first search algorithm
                    node1 = queue1.dequeue()
                    visited_cells.append(node1)
                    spaces.append(node1)
                    if node1 in self.cells:
                        for child1 in (self.cells[node1]):
                            if child1 not in visited_cells:
                                queue1.enqueue(child1)
                for i in range(len(self.gates)):  # if gate occurs in spaces, means it is accessible
                    if self.gates[i] in spaces:
                        number_of_accessible_areas += 1
                        accessible_spaces.append(spaces)
                        break
        accessible_cells2 = [item for sublist in accessible_spaces for item in
                             sublist]  # creating a flat list of all accessible cells
        accessible_cells = set(accessible_cells2)  # creating a unique list of all accessible cells

        # to find cul-de-sacs cells
        cul_de_sacs_dict = self.exits.copy()

        cells_visited = []
        for key2 in cul_de_sacs_dict:
            if (cul_de_sacs_dict[key2] == 1) and (key2 in accessible_cells) and (key2 not in cells_visited):
                cul_de_sacs_dict[key2] = 5
                queue2 = Queue()
                queue2.enqueue(key2)
                while len(queue2) == 1:
                    node2 = queue2.dequeue()
                    cells_visited.append(node2)
                    if node2 in self.cells:
                        for child2 in self.cells[node2]:
                            if child2 not in cells_visited:
                                queue2.enqueue(child2)
                                if cul_de_sacs_dict[child2] == 2:
                                    cul_de_sacs_dict[child2] = 5
                                    cells_visited.append(child2)
                                else:
                                    cul_de_sacs_dict[child2] = cul_de_sacs_dict[child2] - 1
                                    queue2.enqueue(
                                        child2)  # enqueuing dummy child2 so that length of queue becomes more than 1

        cul_de_sacs_cells = []
        for key3 in cul_de_sacs_dict:
            if cul_de_sacs_dict[key3] == 5:
                cul_de_sacs_cells.append(key3)

        cul_de_sacs_cells_display = []
        for p in range(len(cul_de_sacs_cells)):
            x = cul_de_sacs_cells[p][0][0] + 0.5
            y = (cul_de_sacs_cells[p][0][1] + cul_de_sacs_cells[p][1][1]) / 2
            cul_de_sacs_cells_display.append((y, x))

        # print(cul_de_sacs_cells_display)

        # to find number of unique paths # if value in dictionary is '5' meaning it is cul-de-sac or inaccessible
        unique_paths_dict = {}
        for key in cul_de_sacs_dict:
            if key not in accessible_cells:
                unique_paths_dict[key] = 5
            elif (key in cul_de_sacs_dict) and cul_de_sacs_dict[key] == 5:
                unique_paths_dict[key] = 5
            else:
                unique_paths_dict[key] = cul_de_sacs_dict[key]

        # print(unique_paths_dict)

        # to find number of unique paths
        queue4 = Queue()
        number_of_unique_paths = 0
        visited_unique_path_points = []
        unique_paths = []
        for key4 in unique_paths_dict:
            if (key4 not in visited_unique_path_points) and (unique_paths_dict[key4] == 2) and (key4 in self.gates):
                queue4.enqueue(key4)
                unique_path = []
                while not queue4.is_empty():  # breadth first search algorithm
                    node4 = queue4.dequeue()
                    visited_unique_path_points.append(node4)
                    unique_path.append(node4)
                    if node4 in self.cells:
                        for child4 in (self.cells[node4]):
                            if (child4 not in visited_unique_path_points) and (unique_paths_dict[child4] == 2):
                                queue4.enqueue(child4)
                            else:
                                continue
                if node4 in self.gates:
                    if (len(unique_path) == 1) and (key4 in self.pillar_cells) and (key4 in self.corners):
                        g = key4
                        if g[0][0] == 0 and g[0][1] == 0:  # means top left corner
                            if g[0] in self.pillars:
                                number_of_unique_paths += 1
                                unique_paths.append(unique_path)

                        elif g[0][0] == 0 and (g[0][1] != 0):  # means top right corner
                            if g[1] in self.pillars:
                                number_of_unique_paths += 1
                                unique_paths.append(unique_path)

                        elif g[0][1] == 0 and (g[0][0] != 0):  # means bottom left corner
                            if (g[0][0] + 1, g[0][1]) in self.pillars:
                                number_of_unique_paths += 1
                                unique_paths.append(unique_path)

                        elif g[0][0] != 0 and g[0][1] != 0 and g[1][0] != 0 and g[1][
                            1] != 0:  # means bottom right corner
                            if (g[1][0] + 1, g[1][1]) in self.pillars:
                                number_of_unique_paths += 1
                                unique_paths.append(unique_path)
                    elif len(unique_path) > 1:
                        number_of_unique_paths += 1
                        unique_paths.append(unique_path)

        # print(unique_paths)

        horizontal = []
        vertical = []
        for a in range(len(unique_paths)):
            for b in range(len(unique_paths[a])):
                # for the first cell
                if b == 0:
                    if unique_paths[a][0] in self.corners:
                        if len(unique_paths[a]) == 1:
                            t = unique_paths[a][0]
                            if t[0][0] == 0 and t[0][1] == 0:  # means top left corner
                                horizontal.append([(0.5, -0.5), (0.5, 0.5)])
                                vertical.append([(-0.5, 0.5), (0.5, 0.5)])
                            elif t[0][0] == 0 and (t[0][1] != 0):  # means top right corner
                                horizontal.append([(0.5, t[0][1] + 0.5), (0.5, t[1][1] + 0.5)])
                                vertical.append([(-0.5, t[0][1] + 0.5), (0.5, t[0][1] + 0.5)])
                            elif t[0][1] == 0 and (t[0][0] != 0):  # means bottom left corner
                                horizontal.append([(t[0][0] + 0.5, -0.5), (t[0][0] + 0.5, 0.5)])
                                vertical.append([(t[0][0] + 0.5, 0.5), (t[0][0] + 1.5, 0.5)])
                            elif t[0][0] != 0 and t[0][1] != 0 and t[1][0] != 0 and t[1][
                                1] != 0:  # means bottom right corner
                                horizontal.append([(t[0][0] + 0.5, t[0][1] + 0.5), (t[0][0] + 0.5, t[1][1] + 0.5)])
                                vertical.append([(t[0][0] + 0.5, t[0][1] + 0.5), (t[0][0] + 1.5, t[0][1] + 0.5)])
                        else:
                            h = unique_paths[a][0]
                            if h[0][0] == 0 and h[0][1] == 0:  # means top left corner
                                if h[1] in self.connects[h[0]]:
                                    horizontal.append([(0.5, -0.5), (0.5, 0.5)])
                                else:
                                    vertical.append([(-0.5, 0.5), (0.5, 0.5)])
                            elif h[0][0] == 0 and (h[0][1] != 0):  # means top right corner
                                if h[1] in self.connects[h[0]]:
                                    horizontal.append([(0.5, h[0][1] + 0.5), (0.5, h[1][1] + 0.5)])
                                else:
                                    vertical.append([(-0.5, h[0][1] + 0.5), (0.5, h[0][1] + 0.5)])
                            elif h[0][1] == 0 and (h[0][0] != 0):  # means bottom left corner
                                if (h[1][0] + 1, h[1][1]) in self.connects[(h[0][0] + 1, h[0][1])]:
                                    horizontal.append([(h[0][0] + 0.5, -0.5), (h[0][0] + 0.5, 0.5)])
                                else:
                                    vertical.append([(h[0][0] + 0.5, 0.5), (h[0][0] + 1.5, 0.5)])
                            elif h[0][0] != 0 and h[0][1] != 0 and h[1][0] != 0 and h[1][
                                1] != 0:  # means bottom right corner
                                if (h[1][0] + 1, h[1][1]) in self.connects[(h[0][0] + 1, h[0][1])]:
                                    horizontal.append([(h[0][0] + 0.5, h[0][1] + 0.5), (h[0][0] + 0.5, h[1][1] + 0.5)])
                                else:
                                    vertical.append([(h[0][0] + 0.5, h[0][1] + 0.5), (h[0][0] + 1.5, h[0][1] + 0.5)])

                    else:
                        m = unique_paths[a][0]
                        if m[0][0] == 0 and m[1][0] == 0:
                            vertical.append([(m[0][0] - 0.5, m[0][1] + 0.5), (m[0][0] + 0.5, m[0][1] + 0.5)])
                        elif m[0][0] == len(self.grid) - 2 and m[1][0] == len(self.grid) - 2:
                            vertical.append([(m[0][0] + 0.5, m[0][1] + 0.5), (m[0][0] + 1.5, m[0][1] + 0.5)])
                        elif m[0][1] == 0 and m[1][1] == 1:
                            horizontal.append([(m[0][0] + 0.5, m[0][1] - 0.5), (m[0][0] + 0.5, m[0][1] + 0.5)])
                        elif m[0][1] == len(self.grid[0]) - 2 and m[1][1] == len(self.grid[0]) - 1:
                            horizontal.append([(m[0][0] + 0.5, m[0][1] + 0.5), (m[0][0] + 0.5, m[0][1] + 1.5)])

                # for the last cell
                if b == len(unique_paths[a]) - 1:
                    if unique_paths[a][len(unique_paths[a]) - 1] in self.corners:
                        if len(unique_paths[a]) == 1:
                            pass
                        else:
                            g = unique_paths[a][len(unique_paths[a]) - 1]
                            if g[0][0] == 0 and g[0][1] == 0:  # means top left corner
                                if g[1] in self.connects[g[0]]:
                                    horizontal.append([(0.5, -0.5), (0.5, 0.5)])
                                else:
                                    vertical.append([(-0.5, 0.5), (0.5, 0.5)])
                            elif g[0][0] == 0 and (g[0][1] != 0):  # means top right corner
                                if g[1] in self.connects[g[0]]:
                                    horizontal.append([(0.5, g[0][1] + 0.5), (0.5, g[1][1] + 0.5)])
                                else:
                                    vertical.append([(-0.5, g[0][1] + 0.5), (0.5, g[0][1] + 0.5)])
                            elif g[0][1] == 0 and (g[0][0] != 0):  # means bottom left corner
                                if (g[1][0] + 1, g[1][1]) in self.connects[(g[0][0] + 1, g[0][1])]:
                                    horizontal.append([(g[0][0] + 0.5, -0.5), (g[0][0] + 0.5, 0.5)])
                                else:
                                    vertical.append([(g[0][0] + 0.5, 0.5), (g[0][0] + 1.5, 0.5)])
                            elif g[0][0] != 0 and g[0][1] != 0 and g[1][0] != 0 and g[1][
                                1] != 0:  # means bottom right corner
                                if (h[1][0] + 1, h[1][1]) in self.connects[(h[0][0] + 1, h[0][1])]:
                                    horizontal.append([(g[0][0] + 0.5, g[0][1] + 0.5), (g[0][0] + 0.5, g[1][1] + 0.5)])
                                else:
                                    vertical.append([(g[0][0] + 0.5, g[0][1] + 0.5), (g[0][0] + 1.5, g[0][1] + 0.5)])

                    else:
                        n = unique_paths[a][len(unique_paths[a]) - 1]
                        if n[0][0] == 0 and n[1][0] == 0:
                            vertical.append([(n[0][0] - 0.5, n[0][1] + 0.5), (n[0][0] + 0.5, n[0][1] + 0.5)])
                        elif n[0][0] == len(self.grid) - 2 and n[1][0] == len(self.grid) - 2:
                            vertical.append([(n[0][0] + 0.5, n[0][1] + 0.5), (n[0][0] + 1.5, n[0][1] + 0.5)])
                        elif n[0][1] == 0 and n[1][1] == 1:
                            horizontal.append([(n[0][0] + 0.5, n[0][1] - 0.5), (n[0][0] + 0.5, n[0][1] + 0.5)])
                        elif n[0][1] == len(self.grid[0]) - 2 and n[1][1] == len(self.grid[0]) - 1:
                            horizontal.append([(n[0][0] + 0.5, n[0][1] + 0.5), (n[0][0] + 0.5, n[0][1] + 1.5)])


                # for all the cells from first to last in pairs
                else:
                    x = unique_paths[a][b]
                    y = unique_paths[a][b + 1]
                    if x[0][0] != y[0][0]:  # means vertical path
                        vertical.append([(x[0][0] + 0.5, x[0][1] + 0.5), (y[0][0] + 0.5, y[0][1] + 0.5)])
                    else:
                        horizontal.append([(x[0][0] + 0.5, x[0][1] + 0.5), (y[0][0] + 0.5, y[0][1] + 0.5)])

        # to collate all longest lengths
        new_horizontal = []

        for element in horizontal:
            element = sorted(element)
            new_horizontal.append(element)

        new_horizontal = sorted(new_horizontal)

        new_vertical = []

        for element in vertical:
            element = sorted(element)
            new_vertical.append(element)

        new_vertical = sorted(new_vertical, key=lambda x: (x[0][1], x[0][0]))

        # print(new_horizontal)
        # print(new_vertical)

        new_vertical2 = []
        new_vertical_deque = deque(new_vertical)
        while len(new_vertical_deque) > 1:
            x = new_vertical_deque.popleft()
            y = new_vertical_deque.popleft()
            if x[1] == y[0]:
                new_vertical_deque.appendleft([x[0], y[1]])
            else:
                new_vertical2.append(x)
                new_vertical_deque.appendleft(y)

        if len(new_vertical_deque) > 0:
            new_vertical2.append(new_vertical_deque.pop())

        ver_entry_exit_paths = []
        for i in new_vertical2:
            for j in i:
                j = [(x, y) for (y, x) in i]
            ver_entry_exit_paths.append(j)

        ver_entry_exit_paths = sorted(ver_entry_exit_paths)
        # print(ver_entry_exit_paths)

        new_horizontal2 = []
        new_horizontal_deque = deque(new_horizontal)
        while len(new_horizontal_deque) > 1:
            x = new_horizontal_deque.popleft()
            y = new_horizontal_deque.popleft()
            if x[1] == y[0]:
                new_horizontal_deque.appendleft([x[0], y[1]])
            else:
                new_horizontal2.append(x)
                new_horizontal_deque.appendleft(y)

        if len(new_horizontal_deque) > 0:
            new_horizontal2.append(new_horizontal_deque.pop())

        hor_entry_exit_paths = []
        for i in new_horizontal2:
            for j in i:
                j = [(x, y) for (y, x) in i]
            hor_entry_exit_paths.append(j)

        hor_entry_exit_paths = sorted(hor_entry_exit_paths, key=lambda x: (x[0][1], x[0][0]))
        # print(hor_entry_exit_paths)

        # to print the text string and write it to the new tex file
        tex_string = str()

        tex_string += '\\documentclass[10pt]{article}\n' \
                      '\\usepackage{tikz}\n' \
                      '\\usetikzlibrary{shapes.misc}\n' \
                      '\\usepackage[margin=0cm]{geometry}\n' \
                      '\\pagestyle{empty}\n' \
                      '\\tikzstyle{every node}=[cross out, draw, red]\n\n' \
                      '\\begin{document}\n\n' \
                      '\\vspace*{\\fill}\n' \
                      '\\begin{center}\n' \
                      '\\begin{tikzpicture}[x=0.5cm, y=-0.5cm, ultra thick, blue]\n' \
                      '% Walls\n'

        for i in range(len(horizontal_pairs)):
            tex_string += f'    \\draw ({horizontal_pairs[i][0][0]},{horizontal_pairs[i][0][1]}) -- ({horizontal_pairs[i][1][0]},{horizontal_pairs[i][1][1]});\n'
        for i in range(len(vertical_pairs)):
            tex_string += f'    \\draw ({vertical_pairs[i][0][0]},{vertical_pairs[i][0][1]}) -- ({vertical_pairs[i][1][0]},{vertical_pairs[i][1][1]});\n'

        tex_string += '% Pillars\n'
        for i in range(len(display_pillars)):
            tex_string += f'    \\fill[green] ({display_pillars[i][0]},{display_pillars[i][1]}) circle(0.2);\n'

        tex_string += '% Inner points in accessible cul-de-sacs\n'
        for i in range(len(cul_de_sacs_cells_display)):
            tex_string += f'    \\node at ({cul_de_sacs_cells_display[i][0]},{cul_de_sacs_cells_display[i][1]})'
            tex_string += ' {};\n'

        tex_string += '% Entry-exit paths without intersections\n'
        for i in range(len(hor_entry_exit_paths)):
            tex_string += f'    \\draw[dashed, yellow] ({hor_entry_exit_paths[i][0][0]},{hor_entry_exit_paths[i][0][1]}) -- ({hor_entry_exit_paths[i][1][0]},{hor_entry_exit_paths[i][1][1]});\n'
        for i in range(len(ver_entry_exit_paths)):
            tex_string += f'    \\draw[dashed, yellow] ({ver_entry_exit_paths[i][0][0]},{ver_entry_exit_paths[i][0][1]}) -- ({ver_entry_exit_paths[i][1][0]},{ver_entry_exit_paths[i][1][1]});\n'

        tex_string += '\\end{tikzpicture}\n' \
                      '\\end{center}\n' \
                      '\\vspace*{\\fill}\n\n' \
                      '\\end{document}\n'

        with open(f'{self.some_filename[:(len(self.some_filename) - 4)]}.tex', 'w') as file:
            file.write(tex_string)

        # print(tex_string)

# maze1 = Maze('maze_1.txt')
# maze1.analyse()
# maze1.display()
# print()

# maze2 = Maze('maze_2.txt')
# maze2.analyse()
# maze2.display()
# print()

# maze3 = Maze('labyrinth.txt')
# maze3.analyse()
# maze3.display()
# print()

# print("--- %s seconds ---" % (time.time() - start_time))



