from .parsing import Input_Data, Hub, Drone, Connection


class Paths:
    def __init__(self, input_data: Input_Data) -> None:
        self.reservation_hub: dict = {hub.name: {} for hub in input_data.hubs} # {hub1: {1:[drone_id, drone_id], 2: [drone_id]}, hub2: {1:[drone_id, drone_id], 2: [drone_id]}}
        self.reservation_connection: dict = {connection: {} for connection in input_data.connections} # {c1: {1:[drone_id, drone_id], 2: [drone_id]}, c2: {1:[drone_id, drone_id], 2: [drone_id]}}

        self.input_data: Input_Data = input_data
        self.src: Hub
        self.goal: Hub

    def init_data(self) -> None:
        for hub in self.input_data.hubs:
            if hub.is_start:
                self.src = hub
            if hub.is_end:
                self.goal = hub

    def is_free_hub(self, hub: Hub, time: int) -> bool:
        return len(self.reservation_hub[hub.name][time]) < hub.max_drones

    def is_free_connection(self, connection: Connection, time: int) -> bool:
        return len(self.reservation_connection[connection.connection_id][time]) < connection.max_link_capacity

    def reserve_hub(self, hub: Hub, time: int, drone: Drone) -> None:
        if not self.reservation_hub[hub.name].get(time):
            self.reservation_hub[hub.name][time] = [drone.drone_id]
        else:
            self.reservation_hub[hub.name][time].append(drone.drone_id)

    def reserve_connection(self, hub: Hub, time: int, drone: Drone) -> None:
        if not self.reservation_connection[hub.name].get(time):
            self.reservation_connection[hub.name][time] = [drone.drone_id]
        else:
            self.reservation_connection[hub.name][time].append(drone.drone_id)

    def get_parent():
        pass

    def get_path():
        pass

    def solve(self) -> None:
        for drone in self.input_data.lst_drones:
            path = self.get_path()
            if path:
                drone.path = path
            else:
                raise ValueError("An error occured in the algorythm")


