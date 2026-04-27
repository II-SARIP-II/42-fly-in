from .parsing import parsing, Input_Data
from .display_graph import display
from .dijkstra import get_path_drones
from .get_drones_pathes import dijkstra


def main() -> None:
    input_data: Input_Data = parsing()
    input_data = dijkstra(input_data)
    display(input_data)
