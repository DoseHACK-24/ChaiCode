# grid_setup.py

import numpy as np

def create_grid(rows, cols, autobots, obstacles):
    grid = np.full((rows, cols), '.')
    
    for bot, positions in autobots.items():
        grid[positions['start'][0], positions['start'][1]] = 'A'
        grid[positions['goal'][0], positions['goal'][1]] = 'B'
    
    for obstacle in obstacles:
        grid[obstacle[0], obstacle[1]] = 'X'
    
    return grid
