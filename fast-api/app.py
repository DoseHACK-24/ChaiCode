from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Tuple
import heapq
import torch  # YOLOv5 requirement
import cv2    # For handling image/video if necessary
import numpy as np

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow all origins, methods, and headers for development purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Input model for receiving data
class AutobotData(BaseModel):
    grid_size: Tuple[int, int]
    obstacles: List[Tuple[int, int]]
    autobots: List[dict]  # Contains start and goal for each autobot

# A* Pathfinding algorithm
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_search(grid, start, goal):
    ROWS, COLS = len(grid), len(grid[0])
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {}
    cost_so_far = {}

    came_from[start] = None
    cost_so_far[start] = 0

    while frontier:
        _, current = heapq.heappop(frontier)

        if current == goal:
            break

        for direction in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_move = (current[0] + direction[0], current[1] + direction[1])

            if 0 <= next_move[0] < ROWS and 0 <= next_move[1] < COLS and grid[next_move[0]][next_move[1]] != 1:
                new_cost = cost_so_far[current] + 1
                if next_move not in cost_so_far or new_cost < cost_so_far[next_move]:
                    cost_so_far[next_move] = new_cost
                    priority = new_cost + heuristic(goal, next_move)
                    heapq.heappush(frontier, (priority, next_move))
                    came_from[next_move] = current

    # Reconstruct path
    path = []
    current = goal
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)
    path.reverse()
    return path

# YOLOv5 for Object Detection
def detect_nearby_bots(image):
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)  # Load pretrained YOLOv5 model
    results = model(image)
    return results.xyxy[0].numpy()  # Return the bounding boxes (xmin, ymin, xmax, ymax, confidence, class)

@app.post("/calculate_paths/")
async def calculate_paths(data: AutobotData):
    ROWS, COLS = data.grid_size
    grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

    # Place obstacles
    for obs in data.obstacles:
        grid[obs[0]][obs[1]] = 1

    # Calculate paths for all autobots
    paths = {}
    for autobot in data.autobots:
        start = tuple(autobot['start'])
        goal = tuple(autobot['goal'])
        paths[str(start)] = a_star_search(grid, start, goal)

    return {"paths": paths}

@app.post("/detect_bots/")
async def detect_bots(image_file: bytes):
    # Convert image bytes to numpy array
    image = np.frombuffer(image_file, np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    # Detect nearby bots using YOLOv5
    detections = detect_nearby_bots(image)

    return {"detections": detections.tolist()}

