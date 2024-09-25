# simulation.py

def simulate_movement(autobot_paths, autobots):
    total_time = 0
    total_commands = 0
    
    for car, path in autobot_paths.items():
        print(f"\nSimulating movement for {car}:")
        initial_position = autobots[car]['start']
        print(f"Initial position: {initial_position}")
        
        for t, step in enumerate(path):
            print(f"Step {t+1}: {car} moves to {step}")
            total_time += 1
            total_commands += 1
        
        print(f"Final position of {car}: {path[-1]}")
    
    print(f"\nTotal Time: {total_time}")
    print(f"Total Commands: {total_commands}")
