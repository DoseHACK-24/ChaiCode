# pathfinding.py

from queue import PriorityQueue

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_search(grid, start, goal):
    rows, cols = grid.shape
    open_set = PriorityQueue()
    open_set.put((0, start))
    
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while not open_set.empty():
        _, current = open_set.get()
        
        if current == goal:
            return reconstruct_path(came_from, current)
        
        for neighbor in get_neighbors(grid, current):
            tentative_g_score = g_score[current] + 1
            
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                open_set.put((f_score[neighbor], neighbor))
    
    return None

def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.insert(0, current)
    return path

def get_neighbors(grid, position):
    neighbors = []
    row, col = position
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    for dr, dc in directions:
        r, c = row + dr, col + dc
        if 0 <= r < grid.shape[0] and 0 <= c < grid.shape[1] and grid[r, c] != 'X':
            neighbors.append((r, c))

    return neighbors

def avoid_collision(autobot_paths):
    max_time_steps = max(len(path) for path in autobot_paths.values())
    
    for t in range(max_time_steps):
        occupied_positions = set()

        for car, path in autobot_paths.items():
            if t < len(path):
                current_position = path[t]
                if current_position in occupied_positions:
                    path.insert(t, path[t-1])
                else:
                    occupied_positions.add(current_position)

    return autobot_paths
