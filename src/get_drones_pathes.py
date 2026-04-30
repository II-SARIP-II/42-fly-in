from .parsing import Input_Data, Hub, Drone, Connection, ZoneType
from typing import List
import math


class Paths:
    def __init__(self, input_data: Input_Data) -> None:
        self.reservation_hub: dict = {hub.name: {} for hub in input_data.hubs} # {hub1: {1:[drone_id, drone_id], 2: [drone_id]}, hub2: {1:[drone_id, drone_id], 2: [drone_id]}}
        self.reservation_connection: dict = {connection.connection_id: {} for connection in input_data.connections} # {c1: {1:[drone_id, drone_id], 2: [drone_id]}, c2: {1:[drone_id, drone_id], 2: [drone_id]}}
        self.scores = {} # hub|connection: score
        self.input_data: Input_Data = input_data
        self.src: Hub
        self.goal: Hub
        self.queue: List[Hub] = []

    def init_data(self) -> None:
        for hub in self.input_data.hubs:
            if hub.is_start:
                self.src = hub
            if hub.is_end:
                self.goal = hub

    def is_free_hub(self, hub: Hub, time: int) -> bool:
        if self.reservation_hub[hub.name].get(time):
            return self.reservation_hub[hub.name].get(time) < hub.max_drones
        return True

    def is_free_connection(self, connection: Connection, time: int) -> bool:
        if self.reservation_connection[connection.connection_id].get(time):
            return self.reservation_connection[connection.connection_id].get(time) < connection.max_link_capacity
        return True

    def reserve_hub(self, hub: Hub, time: int, delta_t: int) -> None:
        while delta_t > 0:
            if not self.reservation_hub[hub.name].get(time + delta_t):
                self.reservation_hub[hub.name][time + delta_t] = 1
            else:
                self.reservation_hub[hub.name][time + delta_t] += 1
            delta_t -= 1
 
    def reserve_connection(self, connection: Connection, time: int, delta_t: int) -> None:
        if not self.reservation_connection[connection.connection_id].get(time):
            self.reservation_connection[connection.connection_id][time] = 1
        else:
            self.reservation_connection[connection.connection_id][time] += 1

    def get_available_neighbor(self, curr_hub: Hub, curr_time: int):
        neighbors_data = []
        for conn in self.input_data.connections:
            if curr_hub.name == conn.hub1.name:
                if not self.is_free_connection(conn, curr_time):
                    continue                
                delta_t = 2 if conn.hub2.zone == ZoneType.RESTRICTED else 1
                if not self.is_free_hub(conn.hub2, curr_time + delta_t):
                    continue
                
                neighbors_data.append((conn.hub2, conn, delta_t))
        return neighbors_data

    def get_path(self):
        curr_place = self.src
        path: List = [self.src]
        curr_time = 0
        while curr_place.name != self.goal.name and curr_time < 100:
            potential_moves = self.get_available_neighbor(curr_place, curr_time)

            if len(potential_moves) > 0:
                best_move = potential_moves[0] 

                for move in potential_moves:
                    neighbor_hub, conn, dt = move
                    if self.scores[neighbor_hub.name] < self.scores[best_move[0].name]:
                        best_move = move

                next_hub, used_conn, delta_t = best_move

                self.reserve_connection(used_conn, curr_time, 1)                 
                self.reserve_hub(next_hub, curr_time, delta_t)

                curr_place = next_hub
                curr_time += delta_t
                path.append(curr_place)
                if curr_place.zone == ZoneType.RESTRICTED:
                    path.append(curr_place)
            else:
                curr_time += 1
                path.append(curr_place)
        return path

    def init_dijkstra(self):
        for conn in self.input_data.connections:
            if conn.hub1.is_start:
                self.src = conn.hub1
            if conn.hub2.is_end:
                self.goal = conn.hub2
        if not self.src or not self.goal:
            raise ValueError("Input Error: it must be a start "
                             "and an end to the graph")

    def get_hub_scores(self):
        scores = {hub.name: math.inf for hub in self.input_data.hubs}
        scores[self.goal.name] = 0
        queue = [self.goal]
    
        while queue:
            curr_hub = queue.pop(0)
        
            for conn in self.input_data.connections:
                if conn.hub2 == curr_hub:
                    add_val = 1
                    if conn.hub1.zone == ZoneType.RESTRICTED:
                        add_val = 2
                    elif curr_hub.zone == ZoneType.PRIORITY:
                        add_val = 0.4
                    elif curr_hub.zone == ZoneType.BLOCKED:
                        continue
                
                    if scores[curr_hub.name] + add_val < scores[conn.hub1.name]:
                        scores[conn.hub1.name] = scores[curr_hub.name] + add_val
                        queue.append(conn.hub1)
    
        self.scores = scores
        return self.input_data


def dijkstra(input_data: Input_Data):
    #try:
    path = Paths(input_data)
    queue = path.init_dijkstra()
    input_data = path.get_hub_scores()
    #except Exception as e:
    #    raise ValueError(e)
    
    for drone in input_data.lst_drones:
        drone_path = path.get_path()
        if path:
            drone.path = drone_path
        else:
            raise ValueError("An error occured in the algorythm")
    return input_data
