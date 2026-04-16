from .parsing import parsing, Hub, Connection, Input_Datas


def main():
    try:
        input_data: Input_Datas = parsing()
        print("input:", input_data)
    except Exception as e:
        print(e)
        return
