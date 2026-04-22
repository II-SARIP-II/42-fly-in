from .parsing import parsing, Hub, Connection, Input_Data
from .display_graph import display
from .dijkstra import get_path_drones


def main():
    input_data: Input_Data = parsing()
    input_data = get_path_drones(input_data)
    display(input_data)
