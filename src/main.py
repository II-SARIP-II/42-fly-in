from .parsing import parsing, Hub, Connection, Input_Data
from .DisplayGraph import display
from .dijkstra import dijkstra


def main():
    input_data: Input_Data = parsing()
    path = dijkstra(input_data)
    display(input_data, path)
