# main.py

from grid_setup import create_grid
from pathfinding import a_star_search, avoid_collision
from simulation import simulate_movement

def main():
    # Get user input for the grid, autobots, and obstacles
    rows = int(input("Enter the number of rows: "))
    cols = int(input("Enter the number of columns: "))
    num_autobots = int(input("Enter the number of autobots: "))

    autobots = {}
    for i in range(num_autobots):
        start = tuple(map(int, input(f"Enter the starting position for autobot {i+1} (row, col): ").split()))
        goal = tuple(map(int, input(f"Enter the goal position for autobot {i+1} (row, col): ").split()))
        autobots[f'car{i+1}'] = {'start': start, 'goal': goal}

    num_obstacles = int(input("Enter the number of obstacles: "))
    obstacles = [tuple(map(int, input(f"Enter the position for obstacle {i+1} (row, col): ").split())) for i in range(num_obstacles)]

    # Create the grid
    grid = create_grid(rows, cols, autobots, obstacles)
    print("\nGenerated Grid:\n", grid)

    # Pathfinding for each autobot
    paths = {car: a_star_search(grid, positions['start'], positions['goal']) for car, positions in autobots.items()}
    
    # Collision Avoidance
    paths = avoid_collision(paths)

    # Simulate movement and calculate metrics
    simulate_movement(paths, autobots)

if __name__ == '__main__':
    main()
