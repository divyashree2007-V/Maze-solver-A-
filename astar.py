
import heapq
import time


def manhattan_distance(current, goal):
    return (
        abs(current[0] - goal[0])
        + abs(current[1] - goal[1])
    )


def get_neighbors(position, grid):
    rows = len(grid)
    cols = len(grid[0])

    row, col = position

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]

    neighbors = []

    for dr, dc in directions:
        nr = row + dr
        nc = col + dc

        if (
            0 <= nr < rows
            and 0 <= nc < cols
            and grid[nr][nc] == 0
        ):
            neighbors.append((nr, nc))

    return neighbors


def reconstruct_path(came_from, current):
    path = [current]

    while current in came_from:
        current = came_from[current]
        path.append(current)

    return path[::-1]


def astar_search(grid, start, goal):
    start_time = time.perf_counter()

    if not grid or not grid[0]:
        raise ValueError("Maze cannot be empty")

    rows = len(grid)
    cols = len(grid[0])

    if any(len(row) != cols for row in grid):
        raise ValueError("Maze must be rectangular")

    for position in (start, goal):
        r, c = position

        if not (0 <= r < rows and 0 <= c < cols):
            raise ValueError("Invalid start or goal position")

        if grid[r][c] != 0:
            raise ValueError("Start and goal must be open cells")

    open_list = []
    counter = 0

    heapq.heappush(
        open_list,
        (
            manhattan_distance(start, goal),
            counter,
            0,
            start
        )
    )

    came_from = {}
    g_score = {start: 0}

    explored = set()
    explored_order = []

    while open_list:
        f_score, _, current_cost, current = heapq.heappop(open_list)

        if current_cost != g_score.get(current):
            continue

        if current in explored:
            continue

        explored.add(current)
        explored_order.append(current)

        if current == goal:
            path = reconstruct_path(came_from, goal)

            return {
                "path": path,
                "explored": explored,
                "explored_order": explored_order,
                "visited_count": len(explored),
                "path_length": len(path) - 1,
                "execution_time": (
                    time.perf_counter() - start_time
                ) * 1000,
                "status": "Path Found"
            }

        for neighbor in get_neighbors(current, grid):
            tentative_g = current_cost + 1

            if tentative_g < g_score.get(
                neighbor,
                float("inf")
            ):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g

                counter += 1

                heuristic = manhattan_distance(
                    neighbor,
                    goal
                )

                heapq.heappush(
                    open_list,
                    (
                        tentative_g + heuristic,
                        counter,
                        tentative_g,
                        neighbor
                    )
                )

    return {
        "path": [],
        "explored": explored,
        "explored_order": explored_order,
        "visited_count": len(explored),
        "path_length": 0,
        "execution_time": (
            time.perf_counter() - start_time
        ) * 1000,
        "status": "No Path Found"
    }
