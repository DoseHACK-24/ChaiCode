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
