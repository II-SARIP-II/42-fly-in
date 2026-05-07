from .parsing.parsing import parsing
from .parsing.fly_in_class import Input_Data
from .display.display_graph import display
from .algorithm.get_drones_pathes import algo_path
from .output.output_constructor import build_output


def main() -> None:
    try:
        input_data: Input_Data = parsing()
        input_data = algo_path(input_data)
        total_movement = build_output(input_data.lst_drones)
        display(input_data, total_movement)
    except Exception as e:
        print(e)



if __name__ == "__main__":
    main()
