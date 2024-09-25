import numpy as np
import tkinter as tk
from tkinter import simpledialog

class WarehouseEnv:
    def __init__(self, grid_size, starts, ends, obstacles):
        self.grid_size = grid_size
        self.starts = starts
        self.ends = ends
        self.obstacles = obstacles
        self.grid = np.zeros(grid_size)
        
        for obs in obstacles:
            self.grid[obs[0], obs[1]] = -1  # Mark obstacles

        self.bots = list(starts)

    def is_valid_move(self, position):
        x, y = position
        if 0 <= x < self.grid_size[0] and 0 <= y < self.grid_size[1]:
            if self.grid[x, y] != -1 and position not in self.bots:
                return True
        return False

    def get_neighbors(self, position):
        x, y = position
        neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1), position]  # Down, Up, Right, Left, Wait
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
        
        self.info_panel = tk.Label(self.window, text="Autobot Status")
        self.info_panel.grid(row=1, column=0)

        self.steps = 0
        self.states = self.env.bots  # Initialize bot positions
        self.colors = ["blue", "red", "green", "orange", "purple", "yellow"]
        self.bots_color = {i: self.colors[i % len(self.colors)] for i in range(len(self.env.starts))}

        self.draw_grid()
        self.draw_start_and_end()
        self.draw_bots()
    
    def draw_grid(self):
        for i in range(self.env.grid_size[0]):
            for j in range(self.env.grid_size[1]):
                x0, y0 = j * 50, i * 50
                x1, y1 = x0 + 50, y0 + 50
                if self.env.grid[i, j] == -1:
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill="gray")
                else:
                    self.canvas.create_rectangle(x0, y0, x1, y1, outline="black", fill="white")
    
    def draw_start_and_end(self):
        for idx, (start, end) in enumerate(zip(self.env.starts, self.env.ends)):
            sx, sy = start
            ex, ey = end
            color = self.bots_color[idx]

            self.canvas.create_rectangle(sy * 50, sx * 50, (sy + 1) * 50, (sx + 1) * 50, fill=color, stipple="gray50")
            self.canvas.create_text(sy * 50 + 25, sx * 50 + 25, text=f"S{idx+1}", fill="black")

            self.canvas.create_rectangle(ey * 50, ex * 50, (ey + 1) * 50, (ex + 1) * 50, fill="lightgreen", stipple="gray50")
            self.canvas.create_text(ey * 50 + 25, ex * 50 + 25, text=f"E{idx+1}", fill="black")
    
    def draw_bots(self):
        self.canvas.delete("bot")
        for bot_idx, pos in enumerate(self.states):
            x, y = pos
            x0, y0 = y * 50 + 10, x * 50 + 10
            x1, y1 = x0 + 30, y0 + 30
            color = self.bots_color[bot_idx]
            self.canvas.create_oval(x0, y0, x1, y1, fill=color, tags="bot")

    def update_info_panel(self):
        info_text = f"Steps: {self.steps}\n"
        for bot_idx, pos in enumerate(self.states):
            info_text += f"Bot {bot_idx+1}: {pos}\n"
        self.info_panel.config(text=info_text)

    def run(self):
        def step():
            self.steps += 1
            for bot_idx in range(len(self.env.starts)):
                if not self.env.reached_goal(bot_idx):
                    start = self.env.bots[bot_idx]
                    goal = self.env.ends[bot_idx]
                    path = a_star(self.env, start, goal)

                    if len(path) > 1:
                        next_position = path[1]  # Get the next position in the path
                        if not self.env.is_collision_imminent(bot_idx, next_position):
                            self.states[bot_idx] = self.env.update_bot_position(bot_idx, next_position)
                        else:
                            # If a collision is imminent, wait
                            self.states[bot_idx] = self.env.update_bot_position(bot_idx, start)

            self.draw_bots()
            self.update_info_panel()

            if not all(self.env.reached_goal(i) for i in range(len(self.env.starts))):
                self.window.after(500, step)  # Reduced time to make it faster
            else:
                self.info_panel.config(text=f"Simulation Finished in {self.steps} steps")

        step()
        self.window.mainloop()

def get_user_input():
    grid_size = simpledialog.askstring("Input", "Enter grid size (e.g. 5,5):")
    grid_size = tuple(map(int, grid_size.split(',')))

    num_bots = int(simpledialog.askstring("Input", "Enter the number of bots:"))

    starts = []
    ends = []
    for i in range(num_bots):
        start = simpledialog.askstring(f"Input", f"Enter start position for bot {i+1} (e.g. 1,1):")
        start = tuple(map(int, start.split(',')))
        starts.append(start)

        end = simpledialog.askstring(f"Input", f"Enter end position for bot {i+1} (e.g. 4,4):")
        end = tuple(map(int, end.split(',')))
        ends.append(end)

    obstacles = []
    num_obstacles = int(simpledialog.askstring("Input", "Enter the number of obstacles:"))
    for i in range(num_obstacles):
        obs = simpledialog.askstring(f"Input", f"Enter obstacle position {i+1} (e.g. 2,2):")
        obs = tuple(map(int, obs.split(',')))
        obstacles.append(obs)

    return grid_size, starts, ends, obstacles

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    grid_size, starts, ends, obstacles = get_user_input()

    env = WarehouseEnv(grid_size, starts, ends, obstacles)
    gui = WarehouseGUI(env)
    gui.run()
