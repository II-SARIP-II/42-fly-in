from .parsing import parsing, Hub, Connection, Input_Data
from .DisplayGraph import display
from .dijkstra import dijkstra


def main():
    try:
        input_data: Input_Data = parsing()
    except Exception as e:
        print(e)
        return

    dijkstra(input_data)
    display(input_data)
