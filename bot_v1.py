import tkinter as tk
from tkinter import messagebox
import numpy as np
import heapq

# Constants
GRID_SIZE = 10
OBSTACLE_COUNT = 5
BOT_SYMBOL = "🤖"
EMPTY_SYMBOL = "⬜"
OBSTACLE_SYMBOL = "⬛"
SOURCE_SYMBOL = "🌟"
DESTINATION_SYMBOL = "🏁"

class WarehouseBotApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Warehouse Autobots Simulation")
        
        self.grid_size = GRID_SIZE
        self.grid = np.full((self.grid_size, self.grid_size), EMPTY_SYMBOL)
        self.source = None
        self.destination = None
        self.path = []

        self.canvas = tk.Canvas(master, width=400, height=400, bg='white')
        self.canvas.pack()

        self.setup_controls()
        self.create_grid()

    def setup_controls(self):
        control_frame = tk.Frame(self.master)
        control_frame.pack()

        tk.Button(control_frame, text="Run Simulation", command=self.run_simulation).grid(row=0, column=0)
        tk.Button(control_frame, text="Clear Grid", command=self.clear_grid).grid(row=0, column=1)

    def create_grid(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                cell = self.canvas.create_rectangle(
                    j * 40, i * 40, (j + 1) * 40, (i + 1) * 40,
                    fill='white', outline='black', tags="cell")
                self.canvas.tag_bind(cell, "<Button-1>", lambda event, row=i, col=j: self.handle_cell_click(row, col))

    def handle_cell_click(self, row, col):
        if self.grid[row, col] == EMPTY_SYMBOL:
            if self.source is None:
                self.source = (row, col)
                self.grid[row, col] = SOURCE_SYMBOL
                self.canvas.itemconfig(self.canvas.find_withtag("cell")[row * self.grid_size + col], fill='red')
            elif self.destination is None:
                self.destination = (row, col)
                self.grid[row, col] = DESTINATION_SYMBOL
                self.canvas.itemconfig(self.canvas.find_withtag("cell")[row * self.grid_size + col], fill='green')
            elif np.sum(self.grid == OBSTACLE_SYMBOL) < OBSTACLE_COUNT:
                self.grid[row, col] = OBSTACLE_SYMBOL
                self.canvas.itemconfig(self.canvas.find_withtag("cell")[row * self.grid_size + col], fill='black')

    def clear_grid(self):
        self.grid = np.full((self.grid_size, self.grid_size), EMPTY_SYMBOL)
        self.source = None
        self.destination = None
        self.canvas.delete("all")
        self.create_grid()

    def run_simulation(self):
        if not self.source or not self.destination:
            messagebox.showerror("Error", "Please set both source and destination positions!")
            return
        self.path = self.a_star(self.source, self.destination)
        if self.path:
            self.move_bot()
        else:
            messagebox.showerror("Error", "No path found!")

    def a_star(self, start, goal):
        open_set = []
        heapq.heappush(open_set, (0, start))  # (f_score, position)
        came_from = {}
        
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        
        while open_set:
            current = heapq.heappop(open_set)[1]

            if current == goal:
                return self.reconstruct_path(came_from, current)

            for neighbor in self.get_neighbors(current):
                tentative_g_score = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    
                    if neighbor not in [i[1] for i in open_set]:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return []  # Return an empty path if no path is found

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Manhattan distance

    def get_neighbors(self, position):
        row, col = position
        neighbors = [(row + dr, col + dc) for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
        return [p for p in neighbors if self.is_within_bounds(p) and not self.is_obstacle(p)]

    def is_within_bounds(self, position):
        row, col = position
        return 0 <= row < self.grid_size and 0 <= col < self.grid_size

    def is_obstacle(self, position):
        row, col = position
        return self.grid[row, col] == OBSTACLE_SYMBOL

    def reconstruct_path(self, came_from, current):
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)
        return total_path[::-1]  # Reverse the path

    def move_bot(self):
        if not self.path:
            return

        position = self.path.pop(0)
        self.grid[position] = BOT_SYMBOL
        self.update_grid()
        self.grid[position] = EMPTY_SYMBOL  # Clear previous bot position
        
        if self.path:  # If there are still positions to move
            self.master.after(1000, self.move_bot)  # Delay for 1000ms (1 second)

    def update_grid(self):
        self.canvas.delete("all")
        self.create_grid()
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.grid[row, col] == BOT_SYMBOL:
                    self.canvas.itemconfig(self.canvas.find_withtag("cell")[row * self.grid_size + col], fill='yellow')
                elif self.grid[row, col] == SOURCE_SYMBOL:
                    self.canvas.itemconfig(self.canvas.find_withtag("cell")[row * self.grid_size + col], fill='red')
                elif self.grid[row, col] == DESTINATION_SYMBOL:
                    self.canvas.itemconfig(self.canvas.find_withtag("cell")[row * self.grid_size + col], fill='green')
                elif self.grid[row, col] == OBSTACLE_SYMBOL:
                    self.canvas.itemconfig(self.canvas.find_withtag("cell")[row * self.grid_size + col], fill='black')

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = WarehouseBotApp(root)
    root.mainloop()