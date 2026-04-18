from .parsing import parsing, Hub, Connection, Input_Data
from .DisplayGraph import display

def main():
    try:
        input_data: Input_Data = parsing()
    except Exception as e:
        print(e)
        return

    display(input_data)
