from ..parsing.fly_in_class import Input_Data, Hub, Connection, ZoneType

from typing import List, Dict
import math


class PathsFinding:
    '''
    Class to find the best solution of a graph for each drones using
    a reverse djikstra and reservation table
    '''
    def __init__(self, input_data: Input_Data) -> None:
        '''
        Initialisation of the class that find the best solution of a graph
        for each drones using a reverse djikstra and reservation table
        Param:
            input_data: Input_Data = a class that store a list of drones,
                list of hubs and list of connections
        '''
        self.reservation_hub: Dict[str, Dict[int, int]] = {
            hub.name: {} for hub in input_data.hubs}
        self.res_conn: Dict[int, Dict[int, int]] = {
            connection.connection_id: {}
            for connection in input_data.connections}
        self.scores: Dict[str, float] = {}
        self.input_data: Input_Data = input_data
        self.src: Hub
        self.goal: Hub
        self.queue: List[Hub] = []
        self.init_algo()
        self.get_hub_scores()

    def is_free_hub(self, hub: Hub, time: int) -> bool:
        '''
        Return True if the drone can go to the target hub in the right time
        Params:
            hub: Hub = The target hub to potentially reach the next turn
            time: int = which turn the drone tries to go in this hub
        Return value:
            bool = True if it can go in the hub else it returns False
        '''
        if (count := self.reservation_hub[hub.name].get(time)) is not None:
            return count < hub.max_drones
        return True

    def is_free_connection(self, connection: Connection, time: int) -> bool:
        '''
        Return True if the drone can pass by the target connection in the right time
        Params:
            connection: Connection = The target connection to potentially cross the next turn
            time: int = which turn the drone tries to cross the connection
        Return value:
            bool = True if it can cross the connection else it returns False
        '''
        if ((count := self.res_conn[connection.connection_id].get(time))
                is not None):
            return count < connection.max_link_capacity
        return True

    def reserve_hub(self, hub: Hub, time: int, delta_t: int) -> None:
        '''
        Reserve the hub for the next turn to let know to other drones that the place is taken
        Params:
            hub: Hub = The target hub to reserve
            time: int = current time
            delta_t = difference between current time and the time we want to reserve
        '''
        if not self.reservation_hub[hub.name].get(time + delta_t):
            self.reservation_hub[hub.name][time + delta_t] = 1
        else:
            self.reservation_hub[hub.name][time + delta_t] += 1

    def reserve_connection(self,
                           connection: Connection,
                           time: int) -> None:
        '''
        Reserve the connection for the next turn to let know to other drones that the place is taken (mostly for Restricted)
        Params:
            connection: Connection = The target connection to reserve
            time: int = current time
        '''
        if not self.res_conn[connection.connection_id].get(time):
            self.res_conn[connection.connection_id][time] = 1
        else:
            self.res_conn[connection.connection_id][time] += 1

    def get_available_neighbor(self,
                               curr_hub: Hub,
                               curr_time: int
                               ) -> List[tuple[Hub, Connection, int]]:
        '''
        Get all available neighbor from a hub
        Params:
            curr_hub: Hub = the target hub to find their neighbor
            curr_time: int = To look if the neighbor are free in this time
        Return Value:
            List[tuple[Hub, Connection, int]]: List of neighbor with the (next_hub, connection, delta_t)
        '''
        neighbors_data = []
        for conn in self.input_data.connections:
            target_hub = None

            if curr_hub.name == conn.hub1.name:
                target_hub = conn.hub2
            elif curr_hub.name == conn.hub2.name:
                target_hub = conn.hub1

            if target_hub and target_hub.zone != ZoneType.BLOCKED:
                if not self.is_free_connection(conn, curr_time):
                    continue

                delta_t = 2 if target_hub.zone == ZoneType.RESTRICTED else 1

                if not self.is_free_hub(target_hub, curr_time + delta_t):
                    continue

                neighbors_data.append((target_hub, conn, delta_t))
        return neighbors_data

    def get_path(self) -> List[Hub]:
        '''
        Get the path for the drone
        Return value:
            List[Hub]: The path
        '''
        curr_place = self.src
        path: List[Hub] = [self.src]
        curr_time = 0
        while curr_place.name != self.goal.name and curr_time < 100:
            potential_moves = self.get_available_neighbor(curr_place,
                                                          curr_time)
            stay = False
            if len(potential_moves) > 0:
                best_move: tuple[Hub, None | Connection, int] = (
                    potential_moves[0])
                for move in potential_moves:
                    neighbor_hub, _, _ = move
                    if (self.scores[neighbor_hub.name]
                            < self.scores[best_move[0].name]):
                        best_move = move

                if self.is_free_hub(curr_place, curr_time + 1):
                    if (self.scores[curr_place.name]
                            < self.scores[best_move[0].name]):
                        best_move = (curr_place, None, 1)
                        stay = True

                next_hub, used_conn, delta_t = best_move
                if used_conn:
                    self.reserve_connection(used_conn, curr_time)

                self.reserve_hub(next_hub, curr_time, delta_t)

                curr_place = next_hub
                curr_time += delta_t
                path.append(curr_place)
                if curr_place.zone == ZoneType.RESTRICTED and not stay:
                    path.append(curr_place)
            else:
                curr_time += 1
                self.reserve_hub(curr_place, curr_time, 0)
                path.append(curr_place)
        if path[-1] != self.goal:
            raise ValueError("Error: No solutions found")
        return path

    def init_algo(self) -> None:
        '''
        find the start hub and the goal hub from the list of hubs
        '''
        for conn in self.input_data.connections:
            if conn.hub1.is_start:
                self.src = conn.hub1
            if conn.hub2.is_end:
                self.goal = conn.hub2
        if not self.src or not self.goal:
            raise ValueError("Input Error: it must be a start "
                             "and an end to the graph")

    def get_hub_scores(self) -> None:
        '''
        Reverse Djikstra to know how many turn it needs to reach the goal
        Create self.scores that store hub heuristics
        '''
        scores = {hub.name: math.inf for hub in self.input_data.hubs}
        scores[self.goal.name] = 0
        queue = [self.goal]

        while queue:
            curr_hub = queue.pop(0)

            for conn in self.input_data.connections:
                neighbor = None
                if conn.hub2.name == curr_hub.name:
                    neighbor = conn.hub1
                elif conn.hub1.name == curr_hub.name:
                    neighbor = conn.hub2

                if neighbor:
                    add_val: float = 1
                    if neighbor.zone == ZoneType.RESTRICTED:
                        add_val = 2
                    elif neighbor.zone == ZoneType.PRIORITY:
                        add_val = 0.9
                    elif neighbor.zone == ZoneType.BLOCKED:
                        continue

                    if scores[curr_hub.name] + add_val < scores[neighbor.name]:
                        scores[neighbor.name] = scores[curr_hub.name] + add_val
                        queue.append(neighbor)
        self.scores = scores


def algo_path(input_data: Input_Data) -> Input_Data:
    '''
    Get path for each drones
    Params:
        input_data: Input_Data = a class that store a list of drones,
            list of hubs and list of connections
    Return value:
        Input_Data = a class that store a list of drones with pathes,
            list of hubs and list of connections
    '''
    try:
        path = PathsFinding(input_data)
    except Exception as e:
        raise ValueError(e)

    for drone in input_data.lst_drones:
        drone_path = path.get_path()
        if path:
            drone.path = drone_path
        else:
            raise ValueError("An error occured in the algorithm")
    return input_data
