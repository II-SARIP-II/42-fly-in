from .parsing import Input_Data, Hub
from typing import List, Dict, Any
import heapq


class dijkstra:
    def __init__(self, input_data: Input_Data) -> None:
        self.reservation: Dict[str, Dict] = {hub.name: {} for
                                             hub in input_data.hubs}
        self.start: Hub
        self.goal: Hub
        self.input_data = input_data

    def is_place_available(self, hub: Hub, time: int) -> Any:
        if hub.is_start or hub.is_end:
            return True
        drones_prevus = self.reservation[hub.name].get(time, 0)
        return drones_prevus < hub.max_drones

    def init_dijkstra(self) -> None:
        for conn in self.input_data.connections:
            if conn.hub1.is_start:
                self.start = conn.hub1
            if conn.hub2.is_end:
                self.goal = conn.hub2
        if not self.start or not self.goal:
            raise ValueError("Input Error: it must be a start "
                             "and an end to the graph")

    def reserve_path(self, path: List[Hub]) -> None:
        for t, hub in enumerate(path):
            if t not in self.reservation[hub.name]:
                self.reservation[hub.name][t] = 0
            self.reservation[hub.name][t] += 1

    def get_neighbors(self, hub: Hub) -> List[Hub]:
        neighbors = []
        for conn in self.input_data.connections:
            if conn.hub1 == hub:
                neighbors.append(conn.hub2)
            elif conn.hub2 == hub:
                neighbors.append(conn.hub1)

        neighbors.append(hub)
        return neighbors

    def reconstruct_path(self,
                         parents: Dict,
                         goal_hub: Hub,
                         goal_time: int
                         ) -> List[Hub]:
        hub_map = {hub.name: hub for hub in self.input_data.hubs}

        path = []
        curr_name = goal_hub.name
        curr_time = goal_time

        while (curr_name, curr_time) in parents:
            path.append(hub_map[curr_name])
            curr_name, curr_time = parents[(curr_name, curr_time)]

        path.append(hub_map[curr_name])
        return path[::-1]

    def find_path_for_one_drone(self,
                                start_hub: Hub,
                                goal_hub: Hub
                                ) -> List[Hub] | None:
        # On ajoute un compteur pour départager les égalités
        counter = 0
        # Tuple: (priorité, temps, index_unique, objet_hub)
        queue = [(0, 0, counter, start_hub)]
        scores = {(start_hub.name, 0): 0}
        parents: Dict[tuple[str, int], tuple[str, int]] = {}

        while queue:
            _, curr_time, _, curr_hub = heapq.heappop(queue)

            if curr_hub.name == goal_hub.name:
                return self.reconstruct_path(parents, curr_hub, curr_time)

            if curr_time > 100:
                continue

            for neighbor in self.get_neighbors(curr_hub):
                new_time = curr_time + 1

                if self.is_place_available(neighbor, new_time):
                    state_key = (neighbor.name, new_time)
                    old_score = scores.get(state_key, float('inf'))

                    if new_time < old_score:
                        scores[state_key] = new_time
                        parents[state_key] = (curr_hub.name, curr_time)

                        # On incrémente le compteur à chaque push
                        counter += 1
                        heapq.heappush(queue, (new_time, new_time,
                                               counter, neighbor))
        return None

    def solve(self) -> Input_Data:
        self.init_dijkstra()

        for drone in self.input_data.lst_drones:
            path = self.find_path_for_one_drone(self.start, self.goal)
            if path:
                self.reserve_path(path)
                drone.path = path
            else:
                raise ValueError("Impossible de faire passer tous les drones")

        return self.input_data


def get_path_drones(input_data: Input_Data) -> Input_Data:
    try:
        dij = dijkstra(input_data)
        input_data = dij.solve()
    except Exception as e:
        raise ValueError(e)
    return input_data
