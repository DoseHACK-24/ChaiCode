import numpy as np
import tkinter as tk
from tkinter import messagebox
import heapq
import logging
import copy

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

class WarehouseEnv:
    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.obstacles = set()
        self.grid = np.zeros(grid_size, dtype=int)

    def set_obstacles(self, obstacles):
        self.obstacles = set(obstacles)
        for obs in self.obstacles:
            self.grid[obs] = -1  # Mark obstacles
        logging.info(f"Obstacles set at: {self.obstacles}")

    def is_valid_move(self, position):
        x, y = position
        return (0 <= x < self.grid_size[0]) and (0 <= y < self.grid_size[1]) and self.grid[position] != -1

    def get_neighbors(self, position):
        x, y = position
        neighbors = [
            (x + 1, y), (x - 1, y),
            (x, y + 1), (x, y - 1),
            position  # Wait action
        ]
        return [n for n in neighbors if self.is_valid_move(n)]

def a_star(env, start, goal, agent, constraints, stats):
    open_set = []
    heapq.heappush(open_set, (heuristic(start, goal), 0, start))
    came_from = {}
    g_score = {(start, 0): 0}
    expanded_nodes = 0

    while open_set:
        _, current_time, current = heapq.heappop(open_set)
        expanded_nodes += 1

        if current == goal and not has_future_constraints(current, current_time, agent, constraints):
            path = reconstruct_path(came_from, current, current_time)
            stats['expanded_nodes'] += expanded_nodes
            return path

        for neighbor in env.get_neighbors(current):
            tentative_g_score = g_score[(current, current_time)] + 1
            time = current_time + 1

            if violates_constraint(current, neighbor, time, agent, constraints):
                continue

            state_time = (neighbor, time)
            if state_time not in g_score or tentative_g_score < g_score[state_time]:
                came_from[state_time] = (current, current_time)
                g_score[state_time] = tentative_g_score
                f_score = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score, time, neighbor))

    stats['expanded_nodes'] += expanded_nodes
    return None

def violates_constraint(curr_pos, next_pos, time, agent, constraints):
    for constraint in constraints:
        if constraint['agent'] == agent:
            if constraint['type'] == 'vertex' and constraint['loc'] == [next_pos] and constraint['time'] == time:
                return True
            if constraint['type'] == 'edge' and constraint['loc'] == [curr_pos, next_pos] and constraint['time'] == time:
                return True
    return False

def has_future_constraints(pos, time, agent, constraints):
    for constraint in constraints:
        if constraint['agent'] == agent and constraint['time'] > time and constraint['loc'] == [pos]:
            return True
    return False

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def reconstruct_path(came_from, current, time):
    total_path = [(current, time)]
    while (current, time) in came_from:
        current, time = came_from[(current, time)]
        total_path.append((current, time))
    path = [pos for pos, t in reversed(total_path)]
    return path

def detect_conflicts(paths):
    max_time = max(len(path) for path in paths)
    conflicts = []
    for t in range(max_time):
        positions = {}
        for agent, path in enumerate(paths):
            if t < len(path):
                pos = path[t]
            else:
                pos = path[-1]  # Wait at the goal
            if pos in positions:
                conflicts.append({'time': t, 'agents': [positions[pos], agent], 'loc': [pos], 'type': 'vertex'})
            positions[pos] = agent

        # Edge conflicts
        for agent, path in enumerate(paths):
            if t + 1 < len(path):
                curr_pos = path[t]
                next_pos = path[t + 1]
                for other_agent, other_path in enumerate(paths):
                    if agent == other_agent:
                        continue
                    if t + 1 < len(other_path):
                        other_curr = other_path[t]
                        other_next = other_path[t + 1]
                        if curr_pos == other_next and next_pos == other_curr:
                            conflicts.append({'time': t + 1, 'agents': [agent, other_agent],
                                              'loc': [curr_pos, next_pos], 'type': 'edge'})
    return conflicts

def CBS(env, starts, goals):
    # Initialize the root of the search tree with no constraints and initial paths
    root = {'paths': [], 'constraints': [], 'cost': 0}
    priorities = {i: 0 for i in range(len(starts))}  # Dynamic priorities
    stats = {'expanded_nodes': 0}  # For tracking the number of expanded nodes

    # Initial path finding for all agents
    for agent in range(len(starts)):
        path = a_star(env, starts[agent], goals[agent], agent, [], stats)
        if path is None:
            return None, stats
        root['paths'].append(path)
        root['cost'] += len(path)

    # Priority queue for managing search nodes
    open_set = [root]

    while open_set:
        current = open_set.pop(0)
        stats['expanded_nodes'] += 1  # Counting the CBS node expansion
        conflicts = detect_conflicts(current['paths'])

        if not conflicts:
            return current['paths'], stats  # No conflicts, solution found

        # Handle conflict
        conflict = conflicts[0]  # Consider handling more than one conflict
        for agent in conflict['agents']:
            new_constraints = list(current['constraints'])  # Copy constraints
            new_constraints.append({
                'agent': agent,
                'time': conflict['time'],
                'loc': conflict['loc'],
                'type': conflict['type']
            })

            # Re-plan path for the agent with new constraints
            new_paths = current['paths'].copy()
            new_path = a_star(env, starts[agent], goals[agent], agent, new_constraints, stats)
            if new_path is None:
                continue  # No valid path found, skip this branch

            # Create new node in the search tree
            new_paths[agent] = new_path
            new_node = {
                'paths': new_paths,
                'constraints': new_constraints,
                'cost': sum(len(p) for p in new_paths) + sum(priorities.values())  # Adjust cost by priorities
            }
            open_set.append(new_node)

            # Adjust priorities to handle deadlocks dynamically
            priorities[agent] += 1  # Increase priority for the current agent

        # Sort open set based on the cost to prioritize nodes with lower path costs
        open_set.sort(key=lambda x: x['cost'])

    return None, stats  # If the loop exits without returning, no solution was found

class WarehouseGUI:
    def __init__(self, env):
        self.env = env
        self.window = tk.Tk()
        self.window.title("Autobot Warehouse")

        self.canvas_size = 500
        self.canvas = tk.Canvas(self.window, width=self.canvas_size, height=self.canvas_size)
        self.canvas.grid(row=0, column=0, columnspan=2)

        self.info_panel = tk.Label(self.window, text="Autobot Status")
        self.info_panel.grid(row=1, column=0)

        self.clear_button = tk.Button(self.window, text="Clear Canvas", command=self.clear_canvas)
        self.clear_button.grid(row=1, column=1)

        self.grid_size = env.grid_size
        self.cell_size = self.canvas_size // self.grid_size[0]

        self.starts = []
        self.ends = []
        self.states = []
        self.obstacles = []

        self.colors = ["blue", "red", "green", "orange", "purple", "yellow", "cyan", "magenta", "brown", "pink"]
        self.robot_colors = {i: self.colors[i % len(self.colors)] for i in range(10)}

        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click)

        self.init_setup()

    def clear_canvas(self):
        self.env.grid = np.zeros(self.grid_size)
        self.starts = []
        self.ends = []
        self.states = []
        self.obstacles = []
        self.canvas.delete("all")
        self.draw_grid()
        self.update_info_panel("Canvas cleared. Start by setting obstacles.")
        self.mode = "obstacles"
        self.window.bind("<Return>", self.confirm_obstacles)

    def init_setup(self):
        self.draw_grid()
        self.update_info_panel("Click to set obstacles ('O'). Right-click to remove.")
        self.mode = "obstacles"
        self.window.bind("<Return>", self.confirm_obstacles)

    def draw_grid(self):
        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                x0, y0 = j * self.cell_size, i * self.cell_size
                x1, y1 = x0 + self.cell_size, y0 + self.cell_size
                self.canvas.create_rectangle(x0, y0, x1, y1, outline="black", fill="white")

    def draw_cell(self, x, y, fill_color, text=None, tag=""):
        x0 = y * self.cell_size
        y0 = x * self.cell_size
        x1 = x0 + self.cell_size
        y1 = y0 + self.cell_size
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill_color, tags=tag, outline="black")
        if text:
            self.canvas.create_text(x0 + self.cell_size // 2, y0 + self.cell_size // 2, text=text, fill="black")

    def update_info_panel(self, text):
        self.info_panel.config(text=text)

    def on_left_click(self, event):
        row, col = event.y // self.cell_size, event.x // self.cell_size
        if self.mode == "obstacles":
            if (row, col) not in self.obstacles:
                self.obstacles.append((row, col))
                self.env.grid[row, col] = -1
                self.draw_cell(row, col, "gray", "O")
                logging.info(f"Obstacle added at: {(row, col)}")
        elif self.mode == "starts":
            if len(self.starts) < 10 and (row, col) not in self.starts and (row, col) not in self.obstacles:
                self.starts.append((row, col))
                idx = len(self.starts) - 1
                color = self.robot_colors[idx]
                self.draw_cell(row, col, color, f"r{idx + 1}")
                logging.info(f"Start position for robot {idx + 1} set at: {(row, col)}")
        elif self.mode == "ends":
            if len(self.ends) < len(self.starts) and (row, col) not in self.ends and (row, col) not in self.obstacles:
                self.ends.append((row, col))
                idx = len(self.ends) - 1
                self.draw_cell(row, col, "lightgreen", f"d{idx + 1}")
                logging.info(f"End position for robot {idx + 1} set at: {(row, col)}")

    def on_right_click(self, event):
        row, col = event.y // self.cell_size, event.x // self.cell_size
        if self.mode == "obstacles" and (row, col) in self.obstacles:
            self.obstacles.remove((row, col))
            self.env.grid[row, col] = 0
            self.draw_cell(row, col, "white")
            logging.info(f"Obstacle removed from: {(row, col)}")
        elif self.mode == "starts" and (row, col) in self.starts:
            idx = self.starts.index((row, col))
            self.starts.pop(idx)
            self.draw_cell(row, col, "white")
            logging.info(f"Start position for robot {idx + 1} removed from: {(row, col)}")
            # Adjust robot indices
            for i in range(idx, len(self.starts)):
                self.draw_cell(self.starts[i][0], self.starts[i][1], self.robot_colors[i], f"r{i + 1}")
        elif self.mode == "ends" and (row, col) in self.ends:
            idx = self.ends.index((row, col))
            self.ends.pop(idx)
            self.draw_cell(row, col, "white")
            logging.info(f"End position for robot {idx + 1} removed from: {(row, col)}")
            # Adjust destination indices
            for i in range(idx, len(self.ends)):
                self.draw_cell(self.ends[i][0], self.ends[i][1], "lightgreen", f"d{i + 1}")

    def confirm_obstacles(self, event):
        self.env.set_obstacles(self.obstacles)
        self.update_info_panel("Click to set start positions ('r1', 'r2', ...). Right-click to remove.")
        self.mode = "starts"
        self.window.bind("<Return>", self.confirm_starts)

    def confirm_starts(self, event):
        if len(self.starts) > 0:
            self.update_info_panel("Click to set end positions ('d1', 'd2', ...). Right-click to remove.")
            self.mode = "ends"
            self.window.bind("<Return>", self.confirm_ends)
        else:
            messagebox.showwarning("Input Required", "Please set at least one start position.")

    def confirm_ends(self, event):
        if len(self.ends) == len(self.starts):
            self.update_info_panel("Press Enter to start simulation.")
            self.mode = "simulate"
            self.window.bind("<Return>", self.start_simulation)
        else:
            messagebox.showwarning("Input Required", "Please set end positions for all robots.")

    def start_simulation(self, event):
        self.states = list(self.starts)
        self.draw_start_and_end()
        paths, stats = CBS(self.env, self.starts, self.ends)
        self.paths = paths
        if self.paths:
            # Calculate total number of commands for each bot
            self.commands_per_bot = [len(path) - 1 for path in self.paths]
            average_commands = sum(self.commands_per_bot) / len(self.commands_per_bot)
            max_commands = max(self.commands_per_bot)
            logging.info("Total Number of Movements/Commands:")
            for idx, commands in enumerate(self.commands_per_bot):
                logging.info(f"Bot {idx + 1}: {commands} commands")
            logging.info(f"Average number of commands: {average_commands}")
            logging.info(f"Maximum number of commands: {max_commands} (determines when the test case finishes)")
            messagebox.showinfo("Simulation Statistics",
                                f"Total Commands per Bot:\n" +
                                "\n".join([f"Bot {idx + 1}: {commands}" for idx, commands in enumerate(self.commands_per_bot)]) +
                                f"\n\nAverage Commands: {average_commands:.2f}\n" +
                                f"Maximum Commands: {max_commands}")
            self.steps = 0
            self.reached = [False] * len(self.paths)  # Track which robots have reached their destinations
            self.update_info_panel("Simulation started.")
            self.run_simulation_step()
        else:
            messagebox.showerror("No Solution", "No valid paths found for all robots.")
            logging.info(f"No solution found after {stats['expanded_nodes']} commands.")
            self.update_info_panel(f"No solution found after {stats['expanded_nodes']} commands.")

    def run_simulation_step(self):
        all_reached = True
        for idx, path in enumerate(self.paths):
            if self.steps < len(path):
                next_pos = path[self.steps]
                self.states[idx] = next_pos
                all_reached = False
            elif not self.reached[idx]:
                # Robot has reached its destination
                self.reached[idx] = True
                # Update the destination cell
                ex, ey = self.ends[idx]
                color = self.robot_colors[idx]
                self.draw_cell(ex, ey, color, f"r{idx + 1}xd{idx + 1}", tag="start_end")
                logging.info(f"Robot {idx + 1} reached destination.")
        self.draw_bots()

        if not all_reached:
            self.steps += 1
            self.window.after(300, self.run_simulation_step)
        else:
            self.update_info_panel(f"Simulation complete in {self.steps} steps.")
            logging.info(f"Simulation complete in {self.steps} steps.")
            messagebox.showinfo("Simulation Complete",
                                f"All robots reached their destinations in {self.steps} steps.\n\n" +
                                "Total Number of Movements/Commands:\n" +
                                "\n".join([f"Bot {idx + 1}: {commands}" for idx, commands in enumerate(self.commands_per_bot)]) +
                                f"\n\nAverage Commands: {sum(self.commands_per_bot)/len(self.commands_per_bot):.2f}\n" +
                                f"Maximum Commands: {max(self.commands_per_bot)}")

    def draw_start_and_end(self):
        self.canvas.delete("start_end")
        for idx, (start, end) in enumerate(zip(self.starts, self.ends)):
            sx, sy = start
            ex, ey = end
            color = self.robot_colors[idx]

            # Start position with 'r1', 'r2', etc.
            self.draw_cell(sx, sy, color, f"r{idx + 1}", tag="start_end")
            # End position with 'd1', 'd2', etc.
            self.draw_cell(ex, ey, "lightgreen", f"d{idx + 1}", tag="start_end")

    def draw_bots(self):
        self.canvas.delete("bot")
        for idx, pos in enumerate(self.states):
            if not self.reached[idx]:
                x, y = pos
                x0 = y * self.cell_size + self.cell_size * 0.2
                y0 = x * self.cell_size + self.cell_size * 0.2
                x1 = x0 + self.cell_size * 0.6
                y1 = y0 + self.cell_size * 0.6
                color = self.robot_colors[idx]
                self.canvas.create_oval(x0, y0, x1, y1, fill=color, tags="bot")
                self.canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=str(idx + 1), fill="white")

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    grid_size = (10, 10)
    env = WarehouseEnv(grid_size)
    gui = WarehouseGUI(env)
    gui.run()
