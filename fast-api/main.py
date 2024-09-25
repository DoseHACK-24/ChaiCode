import pygame
import heapq
import random

# Grid parameters for a 5x5 warehouse
WIDTH, HEIGHT = 500, 500
ROWS, COLS = 5, 5
SQUARE_SIZE = WIDTH // COLS
FPS = 2

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Initialize Pygame window
pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Warehouse Robot Simulation - Two Robots")

# Define the 5x5 grid (Warehouse simulation)
# 'C' represents the central pickup point, 'D' represents destinations
grid = [
    ['.', '.', 'D', '.', '.'],
    ['.', '.', 'C', '.', '.'],
    ['D', '.', '.', '.', 'D'],
    ['.', '.', '.', '.', '.'],
    ['D', '.', '.', '.', 'D'],
    ['.', '.', 'D', '.', 'C'],
    ['D', 'C', '.', '.', '.']
]

# Central pickup point
CENTRAL_PICKUP = (1, 2)

# List of initial destinations
DESTINATIONS = [(0, 2), (2, 0), (2, 4), (4, 0), (4, 4), (3,4), (0,3), (0,3)]


# List of items associated with each destination
ITEMS = {
    (0, 2): 'Item A',
    (2, 0): 'Item B',
    (2, 4): 'Item C',
    (4, 0): 'Item D',
    (4, 4): 'Item E',
    (3,4): 'Item F',
    (0,3): 'Item G',
    (0,3): 'Item H'
}

# Robot class to hold robot details
class Robot:
    def __init__(self, id, color):
        self.id = id
        self.position = CENTRAL_PICKUP  # Start at central pickup point
        self.color = color
        self.path = []  # Path to follow
        self.path_index = 0  # Index to track position in path
        self.task = None
        self.state = "to_drop"  # Possible states: "to_drop", "returning", "idle"
        self.waiting = False  # Used to manage waiting state
        self.priority = random.random()  # Random priority for deadlock resolution

# Heuristic: Manhattan distance
def manhattan_distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# Define possible movements (up, down, left, right)
moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# Function to find neighbors in the grid
def get_neighbors(position):
    x, y = position
    neighbors = []
    for move in moves:
        new_x, new_y = x + move[0], y + move[1]
        if 0 <= new_x < ROWS and 0 <= new_y < COLS:
            neighbors.append((new_x, new_y))
    return neighbors

# A* algorithm to find the shortest path from start to goal
def a_star(start, goal):
    open_set = []
    heapq.heappush(open_set, (0, start))

    g_score = {start: 0}
    f_score = {start: manhattan_distance(start, goal)}
    came_from = {}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]  # Return reversed path

        for neighbor in get_neighbors(current):
            tentative_g_score = g_score[current] + 1
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + manhattan_distance(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return None  # No path found

# Assign tasks dynamically based on the items, ensuring no duplicate destinations
def assign_new_task(remaining_destinations, assigned_destinations):
    available_destinations = [d for d in remaining_destinations if d not in assigned_destinations]
    if available_destinations:
        return random.choice(available_destinations)
    return None

# Pygame rendering function
def draw_grid(remaining_destinations):
    WIN.fill(WHITE)

    # Draw the grid
    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(WIN, BLACK, rect, 1)
            if grid[row][col] == 'C':
                pygame.draw.circle(WIN, GREEN, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), SQUARE_SIZE // 3)
            elif (row, col) in remaining_destinations:
                pygame.draw.circle(WIN, YELLOW, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), SQUARE_SIZE // 3)

# Draw robots
def draw_robots(robots):
    for robot in robots:
        x, y = robot.position
        pygame.draw.circle(WIN, robot.color, (y * SQUARE_SIZE + SQUARE_SIZE // 2, x * SQUARE_SIZE + SQUARE_SIZE // 2), SQUARE_SIZE // 3)

# Move robots smoothly (simulate human-like behavior)
def move_robot_smoothly(robot, path, path_index):
    if path_index < len(path):
        robot.position = path[path_index]

# Collision detection to check if next move will cause a collision
def will_collide(next_position, other_robots):
    for other_robot in other_robots:
        if next_position == other_robot.position:
            return True
    return False

# Pygame main loop for two robots
def main():
    clock = pygame.time.Clock()
    run = True

    # Initialize two robots
    robots = [Robot(1, BLUE), Robot(2, RED)]
    remaining_destinations = DESTINATIONS.copy()

    robot_paths = {}
    assignments = {}
    path_index = {}

    assigned_destinations = set()

    # Assign the first tasks dynamically to each robot
    for robot in robots:
        random_destination = assign_new_task(remaining_destinations, assigned_destinations)
        if random_destination is not None:
            assignments[robot.id] = random_destination
            assigned_destinations.add(random_destination)
            robot.path = a_star(CENTRAL_PICKUP, random_destination)
            robot_paths[robot.id] = robot.path if robot.path else []
            path_index[robot.id] = 0
            print(f"Robot {robot.id} assigned task: Deliver {ITEMS[random_destination]} to {random_destination}")

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Draw grid and robots
        draw_grid(remaining_destinations)
        draw_robots(robots)

        # Move robots to destinations, then return to pickup point
        for robot in robots:
            other_robots = [r for r in robots if r.id != robot.id]

            if robot.state == "to_drop":
                # Check if robot needs to wait due to collision risk
                if path_index[robot.id] < len(robot_paths[robot.id]):
                    next_position = robot_paths[robot.id][path_index[robot.id]]
                    if not will_collide(next_position, other_robots) or (robot.waiting and robot.priority > other_robots[0].priority):
                        move_robot_smoothly(robot, robot_paths[robot.id], path_index[robot.id])
                        path_index[robot.id] += 1
                        robot.waiting = False
                    else:
                        # If there's a collision risk, robot will wait
                        robot.waiting = True
                else:
                    # Reached the drop destination, remove the destination
                    if assignments[robot.id] in remaining_destinations:
                        print(f"Robot {robot.id} delivered {ITEMS[assignments[robot.id]]} to {assignments[robot.id]}")
                        remaining_destinations.remove(assignments[robot.id])  # Remove destination after delivery
                        assigned_destinations.remove(assignments[robot.id])  # Remove from assigned destinations
                    robot.path = a_star(robot.position, CENTRAL_PICKUP)
                    path_index[robot.id] = 0
                    robot.state = "returning"

            elif robot.state == "returning":
                # Return to the central pickup point
                if path_index[robot.id] < len(robot.path):
                    next_position = robot.path[path_index[robot.id]]
                    if not will_collide(next_position, other_robots) or (robot.waiting and robot.priority > other_robots[0].priority):
                        move_robot_smoothly(robot, robot.path, path_index[robot.id])
                        path_index[robot.id] += 1
                        robot.waiting = False
                    else:
                        # If there's a collision risk, robot will wait
                        robot.waiting = True
                else:
                    # Arrived at the pickup point, assign a new random task
                    if len(remaining_destinations) == 0:
                        robot.state = "idle"  # No more destinations, robot goes idle
                        print(f"Robot {robot.id} has no more destinations to visit!")
                    else:
                        robot.state = "to_drop"
                        random_destination = assign_new_task(remaining_destinations, assigned_destinations)
                        if random_destination is not None:
                            robot.path = a_star(CENTRAL_PICKUP, random_destination)
                            robot_paths[robot.id] = robot.path  # Reset path
                            assignments[robot.id] = random_destination
                            assigned_destinations.add(random_destination)
                            path_index[robot.id] = 0
                            print(f"Robot {robot.id} assigned new task: Deliver {ITEMS[random_destination]} to {random_destination}")

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()