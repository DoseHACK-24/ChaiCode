# reinforcement_learning.py

import random

# Initialize Q-table for state-action values
Q_table = {}

# Parameters
alpha = 0.1
gamma = 0.9
epsilon = 0.2

actions = ['Forward', 'Reverse', 'Left', 'Right', 'Wait']

def choose_action(state):
    if random.uniform(0, 1) < epsilon:
        return random.choice(actions)
    else:
        return max(Q_table.get(state, {}), key=Q_table.get(state, {}).get, default=random.choice(actions))

def update_q_value(state, action, reward, next_state):
    max_future_q = max(Q_table.get(next_state, {}).values(), default=0)
    current_q = Q_table.get(state, {}).get(action, 0)
    new_q = (1 - alpha) * current_q + alpha * (reward + gamma * max_future_q)
    Q_table.setdefault(state, {})[action] = new_q
