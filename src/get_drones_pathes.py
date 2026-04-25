from .parsing import Input_Data, Hub, Drone, Connection, ZoneType
from typing import List
import math


class Paths:
    def __init__(self, input_data: Input_Data) -> None:
        self.reservation_hub: dict = {hub.name: {} for hub in input_data.hubs} # {hub1: {1:[drone_id, drone_id], 2: [drone_id]}, hub2: {1:[drone_id, drone_id], 2: [drone_id]}}
        self.reservation_connection: dict = {connection: {} for connection in input_data.connections} # {c1: {1:[drone_id, drone_id], 2: [drone_id]}, c2: {1:[drone_id, drone_id], 2: [drone_id]}}
        self.scores = {} # hub|connection: score
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

    def init_dijkstra(self, input_data: Input_Data):
        queue: List[Hub] = []
        src: Hub
        goal: Hub
        for conn in input_data.connections:
            if conn.hub1.is_start or conn.hub2.is_start:
                src = conn.hub1
                self.scores[src] = 0
                queue.append(src)
            if conn.hub2.is_end or conn.hub1.is_end:
                goal = conn.hub2
        if not src or not goal:
            raise ValueError("Input Error: it must be a start "
                             "and an end to the graph")
        return queue, goal

    def get_hub_scores(self, input_data: Input_Data, queue: List[Hub]):
        while queue:
            lst_next: List[Connection] = []
            for conn in input_data.connections:
                if conn.hub1 == queue[0]:
                    if conn.hub2.zone == ZoneType.PRIORITY:
                        if conn.hub1.zone == ZoneType.PRIORITY:
                            conn.hub2.zone = ZoneType.BLOCKED
                        else:
                            lst_next = [conn]
                    else:
                        lst_next.append(conn)
                if conn.hub2 == queue[0]:
                    if conn.hub1.zone == ZoneType.PRIORITY:
                        if conn.hub2.zone == ZoneType.PRIORITY:
                            conn.hub1.zone = ZoneType.BLOCKED
                        else:
                            lst_next = [conn]
                    else:
                        lst_next.append(conn)

            for conn in lst_next:
                time_to_coss = 2
                if queue[0].zone == ZoneType.RESTRICTED:
                    time_to_coss = 3
                elif queue[0].zone == ZoneType.BLOCKED:
                    time_to_coss == math.inf
                if conn.hub1 == queue[0]:
                    if self.scores[conn.hub1] + time_to_coss < conn.hub2.score:
                        conn.hub2.score = conn.hub1.score + time_to_coss
                        queue.append(conn.hub2)
                if conn.hub2 == queue[0]:
                    if conn.hub2.score + time_to_coss < conn.hub1.score:
                        conn.hub1.score = conn.hub2.score + time_to_coss
                        queue.append(conn.hub1)
            queue.remove(queue[0])
        return input_data

    def get_shortest_path(input_data: Input_Data, goal: Hub):
        path: List[Hub] = []
        next_path: Hub
        next_path = goal
        path.append(goal)
        for _ in enumerate(input_data.connections):
            for conn in input_data.connections:
                if conn.hub2 == goal:
                    if conn.hub1.score < next_path.score:
                        next_path = conn.hub1
            goal = next_path
            path.append(goal)
            if goal.is_start:
                return path[::-1]
        return path[::-1]

    def dijkstra(self, input_data: Input_Data):
        try:
            queue, goal = self.init_dijkstra(input_data)
        except Exception as e:
            raise ValueError(e)
        input_data = self.get_hub_scores(input_data, queue)
        return self.get_shortest_path(input_data, goal)
