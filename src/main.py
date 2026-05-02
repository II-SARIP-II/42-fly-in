from .parsing import parsing, Input_Data
from .display.display_graph import display
from .get_drones_pathes import dijkstra


def main() -> None:
    try:
        input_data: Input_Data = parsing()
        input_data = dijkstra(input_data)
        display(input_data)
    except Exception as e:
        print(e)
