# 🤖 Autobot Warehouse Simulation

![GitHub forks](https://img.shields.io/github/forks/DoseHACK-24/ChaiCode)
![GitHub contributors](https://img.shields.io/github/contributors/DoseHACK-24/ChaiCode)
![GitHub watchers](https://img.shields.io/github/watchers/DoseHACK-24/ChaiCode)


This project is a simulation of autonomous bots navigating a warehouse environment using the A* algorithm for pathfinding. The simulation is built using Python and Tkinter for the graphical interface. Bots are assigned starting and goal positions, and the environment can be customized with obstacles. The simulation demonstrates the efficient movement of bots while avoiding collisions with obstacles and each-others.

## Project Structure

```bash
ChaiCode/
├
├── .gitignore                     # Ignore file for GitHub
├── main.py                        # Main Python code file
├── requirement.txt                # Dependencies and scripts/library
└── README.md                      # Project documentation
```

## Features

- **Customizable Grid**: Define grid size and place obstacles.
- **Multiple Bots**: Set starting and ending positions for multiple bots.
- **Pathfinding**: A* algorithm for shortest pathfinding.
- **Collision Avoidance**: Bots avoid each other during movement.
- **Real-time Visualization**: Displays bot movement in real-time on the GUI.

## Demonstration Video

[![Watch on YouTube](https://img.youtube.com/vi/7aMxGzzzqv4/0.jpg)](https://youtu.be/7aMxGzzzqv4?si=ujTdLcUShgp6K1Xn)

## Prerequisites

Ensure Python is installed. Download [here](https://www.python.org/downloads/).

### Dependencies

- **Tkinter**: Standard Python GUI package.
- **NumPy**: Grid management and mathematical operations.

Install dependencies using:

```bash
pip install -r requirements.txt
```

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/DoseHACK-24/ChaiCode.git
   ```

2. Navigate to the project directory:

   ```bash
   cd ChaiCode
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Running the Simulation

Run the application using:

```bash
python main.py
```

- **Left Click**: Place obstacles.
- **Enter**: Set bot start and end positions.
- **Space Bar**: Start the simulation.


## License

This project is licensed under the MIT License by ChaiCode Team.
