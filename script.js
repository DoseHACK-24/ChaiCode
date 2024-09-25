let gridSize = 10;
let grid = [];
let numObstacles = 5;
let sourcePosition = null;
let destinationPosition = null;
let obstacleCount = 0;
const botEmoji = "🤖";

// Create a dynamic grid
function createGrid() {
    gridSize = document.getElementById("grid-size").value;
    numObstacles = document.getElementById("num-obstacles").value;
    const gridElement = document.getElementById("grid");
    gridElement.style.gridTemplateColumns = `repeat(${gridSize}, 40px)`;
    gridElement.innerHTML = "";

    grid = [];
    sourcePosition = null;
    destinationPosition = null;
    obstacleCount = 0;

    for (let i = 0; i < gridSize; i++) {
        const row = [];
        for (let j = 0; j < gridSize; j++) {
            const cell = document.createElement("div");
            cell.classList.add("grid-cell");
            cell.setAttribute("data-row", i);
            cell.setAttribute("data-col", j);
            cell.onclick = function () {
                handleCellClick(i, j);
            };
            gridElement.appendChild(cell);
            row.push({ bot: null, obstacle: false });
        }
        grid.push(row);
    }
}

// Handle cell click events to set source, destination, or obstacles
function handleCellClick(row, col) {
    const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
    const sourceColor = document.getElementById("source-color").value;
    const destinationColor = document.getElementById("destination-color").value;
    const obstacleColor = document.getElementById("obstacle-color").value;

    if (!cell.style.backgroundColor || cell.style.backgroundColor === "white") {
        if (!sourcePosition) {
            cell.style.backgroundColor = sourceColor;
            sourcePosition = { row, col };
            cell.innerHTML = botEmoji; // Place bot at source
        } else if (!destinationPosition) {
            cell.style.backgroundColor = destinationColor;
            destinationPosition = { row, col };
        } else if (obstacleCount < numObstacles) {
            cell.style.backgroundColor = obstacleColor;
            grid[row][col].obstacle = true;
            obstacleCount++;
        }
    }
}

// Clear the grid colors and reset
function clearGrid() {
    const cells = document.querySelectorAll(".grid-cell");
    cells.forEach((cell) => {
        cell.style.backgroundColor = "white";
        cell.innerHTML = "";
    });
    sourcePosition = null;
    destinationPosition = null;
    obstacleCount = 0;
    grid.forEach((row) => row.forEach((cell) => (cell.obstacle = false)));
}

// Simulate the bot movement when clicking "Run Simulation"
function runSimulation() {
    if (!sourcePosition || !destinationPosition) {
        alert("Please set both source and destination positions!");
        return;
    }
    
    const path = findPath(sourcePosition, destinationPosition);
    if (path.length === 0) {
        alert("No valid path found!"); // Alert if no path is available
        return;
    }

    moveBot(path);
}

// A* Pathfinding Algorithm to find the best path avoiding obstacles
function findPath(start, goal) {
    const openSet = [];
    const cameFrom = {};
    const gScore = {};
    const fScore = {};

    openSet.push(start);
    gScore[`${start.row},${start.col}`] = 0;
    fScore[`${start.row},${start.col}`] = heuristic(start, goal);

    while (openSet.length > 0) {
        const current = openSet.reduce((lowest, node) => {
            return fScore[`${node.row},${node.col}`] < fScore[`${lowest.row},${lowest.col}`] ? node : lowest;
        });

        if (current.row === goal.row && current.col === goal.col) {
            return reconstructPath(cameFrom, current);
        }

        openSet.splice(openSet.indexOf(current), 1);
        const neighbors = getNeighbors(current);

        neighbors.forEach((neighbor) => {
            const tentativeGScore = (gScore[`${current.row},${current.col}`] || Infinity) + 1;
            if (tentativeGScore < (gScore[`${neighbor.row},${neighbor.col}`] || Infinity)) {
                cameFrom[`${neighbor.row},${neighbor.col}`] = current;
                gScore[`${neighbor.row},${neighbor.col}`] = tentativeGScore;
                fScore[`${neighbor.row},${neighbor.col}`] = tentativeGScore + heuristic(neighbor, goal);
                if (!openSet.some(n => n.row === neighbor.row && n.col === neighbor.col)) {
                    openSet.push(neighbor);
                }
            }
        });
    }
    return []; // Return an empty path if no path is found
}

// Heuristic function for A* (Manhattan Distance)
function heuristic(a, b) {
    return Math.abs(a.row - b.row) + Math.abs(a.col - b.col);
}

// Reconstruct the path from the cameFrom map
function reconstructPath(cameFrom, current) {
    const totalPath = [current];
    while (current in cameFrom) {
        current = cameFrom[`${current.row},${current.col}`];
        totalPath.push(current);
    }
    return totalPath.reverse();
}

// Get neighboring cells that are within bounds and not obstacles
function getNeighbors(position) {
    const neighbors = [];
    const directions = [
        { row: -1, col: 0 }, // Up
        { row: 1, col: 0 },  // Down
        { row: 0, col: -1 }, // Left
        { row: 0, col: 1 },  // Right
    ];
    
    directions.forEach(direction => {
        const newRow = position.row + direction.row;
        const newCol = position.col + direction.col;
        if (isValidCell(newRow, newCol)) {
            neighbors.push({ row: newRow, col: newCol });
        }
    });
    
    return neighbors;
}

// Check if the specified position is valid (within bounds and not an obstacle)
function isValidCell(row, col) {
    return (
        row >= 0 &&
        row < gridSize &&
        col >= 0 &&
        col < gridSize &&
        !grid[row][col].obstacle
    );
}

// Move the bot along the found path
function moveBot(path) {
    let currentIndex = 0;

    function moveStep() {
        if (currentIndex < path.length) {
            const currentCell = document.querySelector(
                `[data-row="${path[currentIndex].row}"][data-col="${path[currentIndex].col}"]`
            );
            currentCell.innerHTML = botEmoji; // Place bot at current position

            if (currentIndex > 0) {
                const previousCell = document.querySelector(
                    `[data-row="${path[currentIndex - 1].row}"][data-col="${path[currentIndex - 1].col}"]`
                );
                previousCell.innerHTML = ""; // Clear previous bot position
            }

            currentIndex++;
            setTimeout(moveStep, 1000); // Delay of 1 second between moves
        }
    }

    moveStep(); // Start moving
}

// Initialize the grid on page load
createGrid();