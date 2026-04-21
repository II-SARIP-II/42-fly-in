from .parsing import Input_Data, Hub, Connection
from typing import Dict, List
import math


graph_goal = { 
    'A': {'B': 1, 'C': 4}, 
    'B': {'A': 1, 'C': 2, 'D': 5}, 
    'C': {'A': 4, 'B': 2, 'D': 1}, 
    'D': {'B': 5, 'C': 1} 
} 

def init_dijkstra(input_data: Input_Data):
    queue: List[Hub] = []
    src: Hub
    goal: Hub
    for conn in input_data.connections:
        if conn.hub1.is_start:
            src = conn.hub1
            src.score = 0
            queue.append(src)
        if conn.hub2.is_end:
            goal = conn.hub2
    if not src or not goal:
        raise ValueError("Input Error: it must be a start "
                         "and an end to the graph")
    return queue, goal


def get_hub_scores(input_data: Input_Data, queue: List[Hub]):
    while queue:
        for conn in input_data.connections:
            if conn.hub1 == queue[0]:
                if conn.hub1.score + 1 < conn.hub2.score:
                    conn.hub2.score = conn.hub1.score + 1
                    queue.append(conn.hub2)
        queue.remove(queue[0])
    return input_data


def get_shortest_path(input_data: Input_Data, goal: Hub):
    path: List[Hub] = []
    next_path: Hub
    next_path = goal
    path.append(goal)
    for _ in enumerate(input_data.connections):
        for conn in input_data.connections:
            if conn.hub2 == goal:
                if conn.hub1.score < next_path.score:
                    next_path = conn.hub1
        goal = next_path
        path.append(goal)
        if goal.is_start:
            return path[::-1]
    return path[::-1]


def dijkstra(input_data: Input_Data):
    try:
        queue, goal = init_dijkstra(input_data)
    except Exception as e:
        raise ValueError(e)
    input_data = get_hub_scores(input_data, queue)
    return get_shortest_path(input_data, goal)
