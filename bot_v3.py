import tkinter as tk
from tkinter import messagebox
import numpy as np
import heapq

# Constants
EMPTY_COLOR = "white"
OBSTACLE_COLOR = "black"
SOURCE_COLOR = "yellow"
DESTINATION_COLOR = "green"
BOT_COLOR = "blue"

class WarehouseBotApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Warehouse Autobots Simulation")

        self.grid_size = 10
        self.grid = np.full((self.grid_size, self.grid_size), None)
        self.source = None
        self.destination = None
        self.bots = []

        self.canvas = tk.Canvas(master, width=400, height=400, bg='white')
        self.canvas.pack()

        self.setup_controls()
        self.create_grid()

    def setup_controls(self):
        control_frame = tk.Frame(self.master)
        control_frame.pack()

        # Grid size input
        tk.Label(control_frame, text="Grid Size (NxN):").grid(row=0, column=0)
        self.grid_size_entry = tk.Entry(control_frame)
        self.grid_size_entry.insert(0, "10")
        self.grid_size_entry.grid(row=0, column=1)

        # Number of bots input
        tk.Label(control_frame, text="Number of Bots:").grid(row=1, column=0)
        self.num_bots_entry = tk.Entry(control_frame)
        self.num_bots_entry.insert(0, "1")
        self.num_bots_entry.grid(row=1, column=1)

        # Set Grid button
        tk.Button(control_frame, text="Set Grid", command=self.set_grid).grid(row=0, column=2)
        tk.Button(control_frame, text="Run Simulation", command=self.run_simulation).grid(row=2, column=0)
        tk.Button(control_frame, text="Clear Grid", command=self.clear_grid).grid(row=2, column=1)
        tk.Button(control_frame, text="Reset All", command=self.reset_all).grid(row=2, column=2)

    def create_grid(self):
        self.cell_rectangles = []  # Store rectangle references
        for i in range(self.grid_size):
            row_rectangles = []
            for j in range(self.grid_size):
                cell = self.canvas.create_rectangle(
                    j * 40, i * 40, (j + 1) * 40, (i + 1) * 40,
                    fill=EMPTY_COLOR, outline='black', tags="cell")
                self.canvas.tag_bind(cell, "<Button-1>", lambda e, row=i, col=j: self.handle_cell_click(row, col))
                row_rectangles.append(cell)
            self.cell_rectangles.append(row_rectangles)

    def handle_cell_click(self, row, col):
        if self.grid[row, col] is None:
            if self.source is None:
                self.source = (row, col)
                self.grid[row, col] = "source"
                self.canvas.itemconfig(self.cell_rectangles[row][col], fill=SOURCE_COLOR)
            elif self.destination is None:
                self.destination = (row, col)
                self.grid[row, col] = "destination"
                self.canvas.itemconfig(self.cell_rectangles[row][col], fill=DESTINATION_COLOR)
            else:
                # Place obstacles
                self.grid[row, col] = "obstacle"
                self.canvas.itemconfig(self.cell_rectangles[row][col], fill=OBSTACLE_COLOR)

    def clear_grid(self):
        self.grid = np.full((self.grid_size, self.grid_size), None)
        self.source = None
        self.destination = None
        for row in self.cell_rectangles:
            for rect in row:
                self.canvas.itemconfig(rect, fill=EMPTY_COLOR)  # Reset rectangles to empty
        self.create_grid()

    def reset_all(self):
        self.clear_grid()
        self.grid_size_entry.delete(0, tk.END)
        self.grid_size_entry.insert(0, "10")  # Reset to default grid size
        self.num_bots_entry.delete(0, tk.END)
        self.num_bots_entry.insert(0, "1")  # Reset to default number of bots

    def set_grid(self):
        try:
            new_size = int(self.grid_size_entry.get())
            if new_size < 1:
                raise ValueError("Grid size must be at least 1.")
            self.grid_size = new_size
            self.clear_grid()  # Clear previous grid
            self.canvas.delete("all")  # Clear canvas
            self.create_grid()  # Create a new grid
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid grid size!")

    def run_simulation(self):
        if not self.source or not self.destination:
            messagebox.showerror("Error", "Please set both source and destination positions!")
            return
        
        # Get the number of bots from the input
        try:
            num_bots = int(self.num_bots_entry.get())
            self.bots = [(self.source[0], self.source[1], f"Bot {i + 1}") for i in range(num_bots)]
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of bots!")
            return

        # Start moving the first bot
        self.move_bots(0)

    def move_bots(self, bot_index):
        if bot_index >= len(self.bots):
            return  # All bots have moved

        current_bot = self.bots[bot_index]
        path = self.a_star_pathfinding(current_bot[0], current_bot[1], self.destination[0], self.destination[1])
        
        if path:
            self.move_bot_along_path(path, bot_index)
        else:
            messagebox.showinfo("Info", f"{current_bot[2]} cannot find a path!")

    def move_bot_along_path(self, path, bot_index):
        for step in path:
            row, col = step
            self.grid[self.bots[bot_index][0], self.bots[bot_index][1]] = None  # Clear previous position
            self.update_grid(row, col, bot_index)  # Update to the new position
            self.bots[bot_index] = (row, col, f"Bot {bot_index + 1}")

            self.master.after(500)  # Delay for visualization
            self.master.update()  # Update the UI
        
        # Wait for 1 second after the bot reaches the destination before moving the next bot
        self.master.after(1000, lambda: self.move_bots(bot_index + 1))

    def a_star_pathfinding(self, start_row, start_col, goal_row, goal_col):
        open_set = []
        heapq.heappush(open_set, (0, (start_row, start_col)))  # (priority, (row, col))
        came_from = {}
        g_score = { (start_row, start_col): 0 }
        f_score = { (start_row, start_col): self.heuristic(start_row, start_col, goal_row, goal_col) }

        while open_set:
            current = heapq.heappop(open_set)[1]

            if current == (goal_row, goal_col):
                return self.reconstruct_path(came_from, current)

            for neighbor in self.get_neighbors(current[0], current[1]):
                tentative_g_score = g_score[current] + 1  # Distance from start to neighbor

                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor[0], neighbor[1], goal_row, goal_col)

                    if neighbor not in [i[1] for i in open_set]:  # Check if the neighbor is not already in open set
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None  # No path found

    def heuristic(self, row, col, goal_row, goal_col):
        # Use Manhattan distance as heuristic
        return abs(goal_row - row) + abs(goal_col - col)

    def get_neighbors(self, row, col):
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Up, Down, Left, Right
            new_row, new_col = row + dr, col + dc
            if self.is_within_bounds((new_row, new_col)) and not self.is_obstacle((new_row, new_col)):
                neighbors.append((new_row, new_col))
        return neighbors

    def reconstruct_path(self, came_from, current):
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)
        total_path.reverse()
        return total_path

    def is_within_bounds(self, position):
        row, col = position
        return 0 <= row < self.grid_size and 0 <= col < self.grid_size

    def is_obstacle(self, position):
        row, col = position
        return self.grid[row, col] == "obstacle"

    def update_grid(self, new_row, new_col, bot_index):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if (row, col) == (new_row, new_col):
                    self.canvas.itemconfig(self.cell_rectangles[row][col], fill=BOT_COLOR)
                elif self.grid[row, col] == "source":
                    self.canvas.itemconfig(self.cell_rectangles[row][col], fill=SOURCE_COLOR)
                elif self.grid[row, col] == "destination":
                    self.canvas.itemconfig(self.cell_rectangles[row][col], fill=DESTINATION_COLOR)
                elif self.grid[row, col] == "obstacle":
                    self.canvas.itemconfig(self.cell_rectangles[row][col], fill=OBSTACLE_COLOR)
                else:
                    self.canvas.itemconfig(self.cell_rectangles[row][col], fill=EMPTY_COLOR)

if __name__ == "__main__":
    root = tk.Tk()
    app = WarehouseBotApp(root)
    root.mainloop()