from .parsing import Input_Data, Hub, Connection
from typing import Dict, List
import heapq
from .parsing import Drone


class dijkstra:
    def __init__(self, input_data: Input_Data):
        self.reservation = {hub.name: {} for hub in input_data.hubs}
        self.start: Hub
        self.goal: Hub
        self.input_data = input_data

    def is_place_available(self, hub, time):
        drones_prevus = self.reservation[hub.name].get(time, 0)
        return drones_prevus < hub.max_drones

    def init_dijkstra(self, input_data: Input_Data):
        for conn in input_data.connections:
            if conn.hub1.is_start:
                self.start = conn.hub1
            if conn.hub2.is_end:
                self.goal = conn.hub2
        if not self.start or not self.goal:
            raise ValueError("Input Error: it must be a start "
                             "and an end to the graph")

    def reserve_path(self, path: List[Hub]):
        for hub, t in enumerate(path):
            if t not in self.reservation[hub.name]:
                self.reservation[hub.name][t] = 0
            self.reservation[hub.name][t] += 1

    def get_neighbors(self, hub: Hub):
        neighbors = []
        for conn in self.input_data.connections:
            if conn.hub1 == hub:
                neighbors.append(conn.hub2)
            elif conn.hub2 == hub:
                neighbors.append(conn.hub1)

        neighbors.append(hub)
        return neighbors

    def reconstruct_path(self, parents, current_hub, current_time):
        path = []
        curr = (current_hub, current_time)
        while curr in parents:
            path.append(curr[0])
            curr = parents[curr]
        path.append(curr[0])
        return path[::-1]

    def find_path_for_one_drone(self, start_hub, goal_hub):
        # queue contient des tuples (hub, temps)
        queue = [(0, 0, start_hub)]
        scores = {(start_hub.name, 0): 0}
        parents = {} # Pour reconstruire le chemin plus tard

        while queue:
            _, curr_time, curr_hub = heapq.heappop(queue)

            if curr_hub == goal_hub:
                return self.reconstruct_path(parents, curr_hub, curr_time)

            if curr_time > 100:
                continue

            for neighbor in self.get_neighbors(curr_hub):
                new_time = curr_time + 1

                if self.is_place_available(neighbor, new_time):
                    old_score = scores.get((neighbor.name, new_time), float('inf'))
                    if new_time < old_score:
                        scores[(neighbor.name, new_time)] = new_time
                        parents[(neighbor, new_time)] = (curr_hub, curr_time)
                        heapq.heappush(queue, (new_time, new_time, neighbor))
        return None

    def solve(self):
        self.init_dijkstra(self.input_data)

        for drone in self.input_data.lst_drones:
            path = self.find_path_for_one_drone(self.start, self.goal)

            if path:
                self.reserve_path(path)
                drone.path == path
            else:
                raise ValueError("Impossible de faire passer tous les drones")

        return self.input_data



def get_path_drones(input_data: Input_Data):
    try:
        dij = dijkstra(input_data)
        input_data = dij.solve()
    except Exception as e:
        raise ValueError(e)
    return input_data
