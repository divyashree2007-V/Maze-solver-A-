
import random


def generate_maze(rows=21, cols=21, wall_probability=0.25):
    rows = max(7, rows)
    cols = max(7, cols)

    if rows % 2 == 0:
        rows += 1

    if cols % 2 == 0:
        cols += 1

    grid = [[1 for _ in range(cols)] for _ in range(rows)]

    start = (1, 1)
    goal = (rows - 2, cols - 2)

    stack = [start]
    grid[start[0]][start[1]] = 0

    directions = [
        (-2, 0),
        (2, 0),
        (0, -2),
        (0, 2)
    ]

    while stack:
        current = stack[-1]
        r, c = current

        neighbors = []

        for dr, dc in directions:
            nr = r + dr
            nc = c + dc

            if (
                1 <= nr < rows - 1
                and 1 <= nc < cols - 1
                and grid[nr][nc] == 1
            ):
                neighbors.append((nr, nc))

        if neighbors:
            nr, nc = random.choice(neighbors)

            grid[(r + nr) // 2][(c + nc) // 2] = 0
            grid[nr][nc] = 0

            stack.append((nr, nc))

        else:
            stack.pop()

    grid[start[0]][start[1]] = 0
    grid[goal[0]][goal[1]] = 0

    return grid, start, goal
