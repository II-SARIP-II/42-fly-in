from ..parsing import Drone

from typing import List, Dict


def build_output(drones: List[Drone]) -> Dict[int, int]:
    max_drone_path = max([len(drone.path) for drone in drones])
    count: Dict[int, int] = {}
    for i in range(max_drone_path):
        count[i] = count[i - 1] if i > 0 else 0
        for drone in drones:
            if (len(drone.path) > i and not drone.path[i].is_start
                    and not drone.path[i - 1].is_end):
                count[i] += 1
                print(f"D{drone.drone_id}-{drone.path[i].name}", end=" ")
        print("\n", end="")
    return count
