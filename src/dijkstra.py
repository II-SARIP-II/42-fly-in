from .parsing import Input_Data, Hub, Connection
from typing import Dict, List


graph_goal = { 
    'A': {'B': 1, 'C': 4}, 
    'B': {'A': 1, 'C': 2, 'D': 5}, 
    'C': {'A': 4, 'B': 2, 'D': 1}, 
    'D': {'B': 5, 'C': 1} 
} 


def dijkstra(input_data: Input_Data):
    graph: Dict[Hub, List[Hub]] = {}
    for connection in input_data.connections:
        if connection.hub1 in graph:
            graph[connection.hub1].append(connection.hub2)
        else:
            graph.update({connection.hub1: [connection.hub2]})
    print(graph)
