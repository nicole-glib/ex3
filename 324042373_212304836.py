import sys
sys.setrecursionlimit(10000)

def Ex_1():
    while True:
        section = int(input('Please enter the section you would like to execute.(for exit enter 4): '))
        #returns the distance between two coordinates
        def distance(row_tower_1, col_tower_1, row_tower_2, col_tower_2):
            horizontal_steps = abs(col_tower_1 - col_tower_2)
            vertical_steps = abs(row_tower_1 - row_tower_2)
            total_steps = vertical_steps + horizontal_steps
            return total_steps
        # returns true if placing a tower is possible otherwise returns false
        # a tower can be placed if its distance from all other towers is bigger then th stated distance
        def add_tower(board, d, row, col, idx=0):
            if idx == row:
                board[row] = col
                return True
            if board[idx] != -1:
                if distance(row, col, idx, board[idx]) <= d:
                    return False
            return add_tower(board, d, row, col, idx + 1)
        # used to transform board from a list of strings to a list of numbers
        def turn_string_list_to_int_list(str_list):
            if not str_list:
                return []
            return [int(str_list[0])] + turn_string_list_to_int_list(str_list[1:])
        #returns a list of tower places of n towers in an n*n matrix with a distance bigger then a given distance
        #if not possible returns empty list
        def n_towers(n, d):
            def try_row(board, row):
                if row == n:
                    return board[:]
                return try_col(board, row, 0)

            def try_col(board, row, col):
                if col == n:
                    return []
                if add_tower(board, d, row, col):
                    result = try_row(board, row + 1)
                    if result:
                        return result
                    board[row] = -1
                return try_col(board, row, col + 1)

            board = [-1] * n
            return try_row(board, 0)

        if section == 1:
            # inputs for distance function:
            row_1 = int(input('enter row1: '))
            col_1 = int(input('enter col1: '))
            row_2 = int(input('enter row2: '))
            col_2 = int(input('enter col2: '))
            print(distance(row_1, col_1, row_2, col_2))
        elif section == 2:
            # inputs for add_tower function:
            board = input("enter the board mumbers separated by space: ") #supposed to be "mumbers".
            dist = int(input("enter d: "))
            row = int(input("enter row: "))
            col = int(input("enter col: "))
            # turn the string into a list of strings, into a list of ints
            board = turn_string_list_to_int_list(board.split())

            print(add_tower(board, dist, row, col))
            print(board)

        elif section == 3:
            n = int(input('enter n: '))
            d = int(input('enter d: '))
            print(n_towers(n, d))
        elif section == 4:
            break

def Ex_2():
    while True:
        section = int(input('Please enter the section you would like to execute.(for exit enter 4): '))
        # opens a file with a matrix inside and returns a matrix
        def read_map(filename):
            with open(filename, 'r') as f:
                return [list(map(int, line.strip().split())) for line in f if line.strip()]

        #checks if a coordinate is in the matrix has zero and wasn't visited
        def is_valid(x, y, grid, visited):
            n = len(grid)
            return 0 <= x < n and 0 <= y < n and (grid[x][y] == 0) and (x,y) not in visited

        #creates an n size matrix with false for every cell
        def create_false_matrix(n, row=0):
            if row == n:
                return []
            return [[False] * n] + create_false_matrix(n, row + 1)

        #finds shortest path using dfs
        #returns best path (a tuple list of coordinates)
        def find_shortest_path(grid, start, end):
            best_path = []

            def dfs(r, c, path, visited):
                nonlocal best_path

                if (r, c) == end:
                    if not best_path or len(path) < len(best_path):
                        best_path = path[:]
                    return

                #you didn't allow for
                nr, nc = r - 1, c # up
                if is_valid(nr, nc, grid, visited):
                    visited.add((nr, nc))
                    path.append((nr, nc))
                    dfs(nr, nc, path, visited)
                    path.pop()
                    visited.remove((nr, nc))

                nr, nc = r, c + 1  # right
                if is_valid(nr, nc, grid, visited):
                    visited.add((nr, nc))
                    path.append((nr, nc))
                    dfs(nr, nc, path, visited)
                    path.pop()
                    visited.remove((nr, nc))

                nr, nc = r + 1, c  # down
                if is_valid(nr, nc, grid, visited):
                    visited.add((nr, nc))
                    path.append((nr, nc))
                    dfs(nr, nc, path, visited)
                    path.pop()
                    visited.remove((nr, nc))

                nr, nc = r, c - 1 # left
                if is_valid(nr, nc, grid, visited):
                    visited.add((nr, nc))
                    path.append((nr, nc))
                    dfs(nr, nc, path, visited)
                    path.pop()
                    visited.remove((nr, nc))

            if grid[start[0]][start[1]] == 0 and grid[end[0]][end[1]] == 0:
                dfs(start[0], start[1], [start], {start})

            return best_path


        if section == 1:
            map_name = input('enter map name: ')
            print(read_map(map_name + '.txt'))
        elif section == 2:
            map_name = input('enter map name: ')
            visited = create_false_matrix(len(read_map(map_name + '.txt')))
            x = int(input('enter x: '))
            y = int(input('enter y: '))
            print(is_valid(x, y, read_map(map_name + '.txt'), visited))
        elif section == 3:

            map_name = input('enter map name: ')
            start_point = input('enter the start point with space \'x y\': ')
            start_point = tuple(map(int, start_point.split()))
            end_point = input('enter the end point with space \'x y\': ')
            end_point = tuple(map(int, end_point.split()))
            path = find_shortest_path(read_map(map_name + '.txt'), start_point, end_point)
            if path:
                print('Shortest path found:')
                for p in path:
                    print(p)
            else:
                print('No path found.')
        elif section == 4:
            break;

if __name__ == '__main__':
    Ex = 0
    while Ex!= 4:
        Ex = int(input('Choose a question (enter 4 for exit): '))
        if Ex == 1:
            Ex_1()
        else:
            if Ex == 2:
                Ex_2()