from flask import Flask, request, jsonify, render_template
from autobot_navigation import AutobotNavigator

app = Flask(__name__)

# Initialize the Autobot navigator
navigator = AutobotNavigator()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/navigate', methods=['POST'])
def navigate_autobots():
    # Get grid details and positions from the frontend
    data = request.json
    grid = data['grid']
    start_positions = data['start_positions']
    end_positions = data['end_positions']

    # Call the pathfinding algorithm
    results = navigator.find_paths(grid, start_positions, end_positions)
    
    # Return the results (commands for autobot movements)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
