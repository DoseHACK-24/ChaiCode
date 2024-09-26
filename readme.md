# 🤖 Autobot Warehouse Simulation

This project is a simulation of autonomous bots navigating a warehouse environment using the A* algorithm for pathfinding. The simulation is built using Python and Tkinter for the graphical interface. Bots are assigned starting and goal positions, and the environment can be customized with obstacles. The simulation demonstrates the efficient movement of bots while avoiding collisions with obstacles and each-others.

## Features

- **Customizable Grid**: Define grid size and place obstacles.
- **Multiple Bots**: Set starting and ending positions for multiple bots.
- **Pathfinding**: Uses A* algorithm to find the shortest path between start and goal.
- **Collision Avoidance**: Bots avoid collisions during movement.
- **Real-time Visualization**: The entire bot movement is displayed on the graphical interface.

## Demonstration Video

[![Watch the video](https://i mg.youtube.com/vi/T-ztCxK4H00/maxresdefault.jpg)](https://youtu.be/T-ztCxK4H00?si=CKOS-FWeSMNJ6NH)

## Prerequisites

Ensure you have Python installed on your system. You can download it from [here](https://www.python.org/downloads/).

### Dependencies

- **Tkinter**: Python's standard GUI package.
- **NumPy**: Used for grid management and operations.

You can install the required dependencies using `pip`:

```bash
pip install numpy
```

## How to Install

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/autobot-warehouse-simulation.git
   ```

2. Navigate to the project directory:

   ```bash
   cd autobot-warehouse-simulation
   ```

3. Install the necessary dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   (If a `requirements.txt` file is not provided, you can manually install `numpy` and `tkinter` using the commands above.)

## How to Run the Simulation

1. After installing the dependencies, run the following command in the project directory to start the application:

   ```bash
   python warehouse_simulation.py
   ```

2. The GUI will open where you can interact with the grid.

   - **Left Click**: Place obstacles on the grid.
   - **Press Enter**: Confirm obstacle placement and switch to adding start positions for the bots.
   - **Press Enter Again**: Confirm start positions and proceed to set the end positions.
   - **Space Bar**: Start the bot simulation.

## Usage

1. Set up the warehouse grid by clicking to add obstacles.
2. Define start and end positions for each bot.
3. Watch the simulation as the bots navigate from their start to end positions, avoiding obstacles and other bots.

## Contributing

Feel free to fork this repository, open issues, or create pull requests to improve the simulation. Contributions are always welcome!

## License

This project is licensed under the MIT License by ChaiCode Team.