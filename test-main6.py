import numpy as np
import tkinter as tk
from tkinter import messagebox


class WarehouseEnv:
    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.starts = []
        self.ends = []
        self.obstacles = []
        self.grid = np.zeros(grid_size)
        self.bots = []

    def set_obstacles(self, obstacles):
        self.obstacles = obstacles
        for obs in obstacles:
            self.grid[obs[0], obs[1]] = -1  # Mark obstacles

    def set_starts_and_ends(self, starts, ends):
        self.starts = starts
        self.ends = ends
        self.bots = list(starts)

    def is_valid_move(self, position):
        x, y = position
        if 0 <= x < self.grid_size[0] and 0 <= y < self.grid_size[1]:
            if self.grid[x, y] != -1 and position not in self.bots:
                return True
        return False

    def get_neighbors(self, position):
        x, y = position
        neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1), position]  # Down, Up, Right, Left, Wait
        return [n for n in neighbors if self.is_valid_move(n)]

    def update_bot_position(self, bot_idx, new_position):
        self.bots[bot_idx] = new_position
        return new_position

    def reached_goal(self, bot_idx):
        return self.bots[bot_idx] == self.ends[bot_idx]

    def get_state(self, bot_idx):
        return self.bots[bot_idx]

    def is_collision_imminent(self, bot_idx, next_position):
        for idx, bot_position in enumerate(self.bots):
            if idx != bot_idx and next_position == bot_position:
                return True
        return False


import heapq


def a_star(env, start, goal):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        current = heapq.heappop(open_set)[1]

        if current == goal:
            return reconstruct_path(came_from, current)

        for neighbor in env.get_neighbors(current):
            tentative_g_score = g_score[current] + 1  # Assume cost between neighbors is 1
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)

                if neighbor not in [i[1] for i in open_set]:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return []  # Return an empty path if no path found


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Manhattan distance


def reconstruct_path(came_from, current):
    total_path = [current]
    while current in came_from:
        current = came_from[current]
        total_path.append(current)
    return total_path[::-1]  # Return reversed path


class WarehouseGUI:
    def __init__(self, env):
        self.env = env
        self.window = tk.Tk()
        self.window.title("Autobot Warehouse")

        self.canvas = tk.Canvas(self.window, width=500, height=500)
        self.canvas.grid(row=0, column=0, columnspan=2)

        self.clear_button = tk.Button(self.window, text="Clear Canvas", command=self.clear_canvas)  # Added Clear Canvas button
        self.clear_button.grid(row=1, column=1)

        self.info_panel = tk.Label(self.window, text="Autobot Status")
        self.info_panel.grid(row=1, column=0)

        self.grid_size = env.grid_size
        self.cell_size = 500 // self.grid_size[0]

        self.start_end_mode = None
        self.current_bot = 0

        self.steps = 0
        self.max_steps = 25  # Set maximum steps for the simulation
        self.states = []  # Initialize bot positions
        self.obstacles = []
        self.starts = []
        self.ends = []

        self.colors = ["blue", "red", "green", "orange", "purple", "yellow"]
        self.bots_color = {i: self.colors[i % len(self.colors)] for i in range(10)}

        self.canvas.bind("<Button-1>", self.on_click)

        self.init_setup()

    def clear_canvas(self):
        # Reset the environment and GUI elements
        self.env.grid = np.zeros(self.grid_size)
        self.starts = []
        self.ends = []
        self.obstacles = []
        self.states = []
        self.steps = 0  # Reset the steps counter
        self.canvas.delete("all")  # Clear everything from the canvas
        self.draw_grid()  # Redraw the grid
        self.update_info_panel("Grid cleared. Start fresh by setting obstacles.")
        
        # Re-enable obstacle selection after clearing
        self.canvas.bind("<Button-1>", self.on_click)
        self.window.bind("<Return>", self.confirm_obstacles)

    def init_setup(self):
        self.draw_grid()
        self.update_info_panel("Click on cells to set obstacles. Right-click to remove.")
        self.window.bind("<Return>", self.confirm_obstacles)

    def draw_grid(self):
        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                x0, y0 = j * self.cell_size, i * self.cell_size
                x1, y1 = x0 + self.cell_size, y0 + self.cell_size
                self.canvas.create_rectangle(x0, y0, x1, y1, outline="black", fill="white")

    def draw_start_and_end(self):
        self.canvas.delete("start_end")
        for idx, (start, end) in enumerate(zip(self.starts, self.ends)):
            sx, sy = start
            ex, ey = end
            color = self.bots_color[idx]

            self.canvas.create_rectangle(sy * self.cell_size, sx * self.cell_size,
                                         (sy + 1) * self.cell_size, (sx + 1) * self.cell_size,
                                         fill=color, stipple="gray50", tags="start_end")
            self.canvas.create_text(sy * self.cell_size + self.cell_size // 2,
                                    sx * self.cell_size + self.cell_size // 2,
                                    text=f"S{idx + 1}", fill="black")

            self.canvas.create_rectangle(ey * self.cell_size, ex * self.cell_size,
                                         (ey + 1) * self.cell_size, (ex + 1) * self.cell_size,
                                         fill="lightgreen", stipple="gray50", tags="start_end")
            self.canvas.create_text(ey * self.cell_size + self.cell_size // 2,
                                    ex * self.cell_size + self.cell_size // 2,
                                    text=f"E{idx + 1}", fill="black")

    def draw_bots(self):
        self.canvas.delete("bot")
        for bot_idx, pos in enumerate(self.states):
            x, y = pos
            x0, y0 = y * self.cell_size + 10, x * self.cell_size + 10
            x1, y1 = x0 + self.cell_size - 20, y0 + self.cell_size - 20
            color = self.bots_color[bot_idx]
            self.canvas.create_oval(x0, y0, x1, y1, fill=color, tags="bot")

    def update_info_panel(self, text):
        self.info_panel.config(text=text)

    def on_click(self, event):
        row, col = event.y // self.cell_size, event.x // self.cell_size

        if (row, col) in self.obstacles:
            self.obstacles.remove((row, col))
            self.env.grid[row, col] = 0
            self.canvas.create_rectangle(col * self.cell_size, row * self.cell_size,
                                         (col + 1) * self.cell_size, (row + 1) * self.cell_size,
                                         outline="black", fill="white")
        else:
            self.obstacles.append((row, col))
            self.env.grid[row, col] = -1
            self.canvas.create_rectangle(col * self.cell_size, row * self.cell_size,
                                         (col + 1) * self.cell_size, (row + 1) * self.cell_size,
                                         outline="black", fill="gray")

    def confirm_obstacles(self, event):
        self.env.set_obstacles(self.obstacles)
        self.update_info_panel("Click on grid to set start position of bot. Right-click to remove.")
        self.canvas.unbind("<Button-1>")
        self.canvas.bind("<Button-1>", self.set_start)
        self.window.bind("<Return>", self.confirm_starts)

    def set_start(self, event):
        row, col = event.y // self.cell_size, event.x // self.cell_size
        if (row, col) not in self.obstacles and (row, col) not in self.starts:
            self.starts.append((row, col))
            self.canvas.create_rectangle(col * self.cell_size, row * self.cell_size,
                                         (col + 1) * self.cell_size, (row + 1) * self.cell_size,
                                         outline="black", fill="blue")
        elif (row, col) in self.starts:
            self.starts.remove((row, col))
            self.canvas.create_rectangle(col * self.cell_size, row * self.cell_size,
                                         (col + 1) * self.cell_size, (row + 1) * self.cell_size,
                                         outline="black", fill="white")

    def confirm_starts(self, event):
        if len(self.starts) > 0:
            self.update_info_panel("Click on grid to set end position of bot. Right-click to remove.")
            self.canvas.bind("<Button-1>", self.set_end)
            self.window.bind("<Return>", self.confirm_ends)
        else:
            self.update_info_panel("Please set at least one start position.")

    def set_end(self, event):
        row, col = event.y // self.cell_size, event.x // self.cell_size
        if (row, col) not in self.obstacles and (row, col) not in self.ends:
            self.ends.append((row, col))
            self.canvas.create_rectangle(col * self.cell_size, row * self.cell_size,
                                         (col + 1) * self.cell_size, (row + 1) * self.cell_size,
                                         outline="black", fill="lightgreen")
        elif (row, col) in self.ends:
            self.ends.remove((row, col))
            self.canvas.create_rectangle(col * self.cell_size, row * self.cell_size,
                                         (col + 1) * self.cell_size, (row + 1) * self.cell_size,
                                         outline="black", fill="white")

    def confirm_ends(self, event):
        if len(self.ends) == len(self.starts):
            self.update_info_panel("Press Enter to start simulation.")
            self.canvas.bind("<Button-1>", lambda e: None)
            self.window.bind("<Return>", self.start_simulation)
            self.env.set_starts_and_ends(self.starts, self.ends)
            self.states = list(self.starts)
            self.draw_start_and_end()
        else:
            self.update_info_panel("Number of end positions must match the number of start positions.")

    def start_simulation(self, event):
        self.update_info_panel("Simulation running...")
        paths = [a_star(self.env, start, end) for start, end in zip(self.starts, self.ends)]
        self.steps = 0
        self.simulation_loop(paths)

    def simulation_loop(self, paths):
        if all(self.env.reached_goal(i) for i in range(len(paths))):
            self.update_info_panel("Simulation complete: All bots have reached their destinations!")
            return

        if self.steps >= self.max_steps:
            messagebox.showwarning("Possible Deadlock", "The bots have not reached their destinations within 25 steps. There may be a deadlock.")
            return

        for i in range(len(paths)):
            if not self.env.reached_goal(i) and len(paths[i]) > 1:
                next_move = paths[i][1]
                if not self.env.is_collision_imminent(i, next_move):
                    paths[i].pop(0)
                    self.states[i] = self.env.update_bot_position(i, next_move)

        self.steps += 1
        self.draw_bots()
        self.window.after(500, self.simulation_loop, paths)


env = WarehouseEnv((5, 5))
gui = WarehouseGUI(env)
gui.window.mainloop()