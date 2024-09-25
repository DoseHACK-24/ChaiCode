import heapq

# Grid size (rows x cols)
ROWS, COLS = 10, 10
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

# Example obstacles
obstacles = [(2, 2), (3, 2), (4, 2)]
for obstacle in obstacles:
    grid[obstacle[0]][obstacle[1]] = 1  # Mark as obstacle (1)

# Starting points and destinations of autobots
autobots = [
    {'start': (0, 0), 'goal': (5, 5)},
    {'start': (9, 9), 'goal': (0, 9)},
]

def heuristic(a, b):
    # Manhattan Distance Heuristic
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_search(start, goal):
    # Priority queue to store the paths to explore
    frontier = []
    heapq.heappush(frontier, (0, start))
    
    # Dictionary to store the best path found
    came_from = {}
    cost_so_far = {}
    
    came_from[start] = None
    cost_so_far[start] = 0

    while not len(frontier) == 0:
        _, current = heapq.heappop(frontier)

        if current == goal:
            break
        
        # Explore neighbors
        for direction in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_move = (current[0] + direction[0], current[1] + direction[1])
            
            # Check if within grid and not an obstacle
            if 0 <= next_move[0] < ROWS and 0 <= next_move[1] < COLS and grid[next_move[0]][next_move[1]] != 1:
                new_cost = cost_so_far[current] + 1  # Each step costs 1
                if next_move not in cost_so_far or new_cost < cost_so_far[next_move]:
                    cost_so_far[next_move] = new_cost
                    priority = new_cost + heuristic(goal, next_move)
                    heapq.heappush(frontier, (priority, next_move))
                    came_from[next_move] = current
    
    # Reconstruct path
    path = []
    current = goal
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)
    path.reverse()
    return path

def move_autobots(autobots):
    # Dictionary to store planned paths for each autobot
    autobot_paths = {}
    
    for autobot in autobots:
        start, goal = autobot['start'], autobot['goal']
        path = a_star_search(start, goal)
        autobot_paths[autobot['start']] = path
    
    return autobot_paths

# Get the planned paths for all autobots
paths = move_autobots(autobots)
for autobot, path in paths.items():
    print(f"Autobot starting at {autobot} will follow the path: {path}")

def simulate_movements(autobot_paths):
    # Store the current positions of autobots
    current_positions = {autobot: autobot for autobot in autobot_paths.keys()}
    
    time_step = 0
    while any(len(path) > 0 for path in autobot_paths.values()):
        print(f"Time step: {time_step}")
        next_positions = {}
        
        # Move each autobot
        for autobot, path in autobot_paths.items():
            if len(path) > 0:
                next_pos = path.pop(0)
                
                # Check for collisions
                if next_pos in current_positions.values():
                    print(f"Collision detected! Autobot at {autobot} waits.")
                    autobot_paths[autobot].insert(0, next_pos)  # Wait (stay in place)
                else:
                    next_positions[autobot] = next_pos
                    print(f"Autobot at {autobot} moves to {next_pos}")
        
        current_positions.update(next_positions)
        time_step += 1

simulate_movements(paths)


import time
import os

# Helper function to display the grid with autobots' positions
def display_grid(current_positions):
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear screen
    for row in range(ROWS):
        for col in range(COLS):
            if (row, col) in current_positions.values():
                print('A', end=' ')  # Autobot
            elif grid[row][col] == 1:
                print('#', end=' ')  # Obstacle
            else:
                print('.', end=' ')  # Empty space
        print()
    time.sleep(0.5)  # Delay to create a smooth animation effect

# Simulation function with grid display
def simulate_movements_with_display(autobot_paths):
    # Store the current positions of autobots
    current_positions = {autobot: autobot for autobot in autobot_paths.keys()}
    
    time_step = 0
    while any(len(path) > 0 for path in autobot_paths.values()):
        print(f"Time step: {time_step}")
        next_positions = {}
        
        # Move each autobot
        for autobot, path in autobot_paths.items():
            if len(path) > 0:
                next_pos = path.pop(0)
                
                # Check for collisions
                if next_pos in current_positions.values():
                    autobot_paths[autobot].insert(0, next_pos)  # Wait (stay in place)
                else:
                    next_positions[autobot] = next_pos
        
        # Update positions
        current_positions.update(next_positions)
        display_grid(current_positions)  # Display grid with autobots' positions
        time_step += 1

# Run the simulation with grid animation
simulate_movements_with_display(paths)
