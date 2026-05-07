from ..parsing.fly_in_class import Drone, ZoneType

from typing import List, Dict


def build_output(drones: List[Drone]) -> Dict[int, int]:
    max_drone_path = max([len(drone.path) for drone in drones])
    count: Dict[int, int] = {}
    for i in range(max_drone_path):
        print(f"t{i}: ", end="")
        count[i] = count[i - 1] if i > 0 else 0
        for drone in drones:
            if (len(drone.path) > i
                    and not drone.path[i].is_start
                    and not drone.path[i - 1].is_end
                    and (drone.path[i - 1] != drone.path[i] or
                         (drone.path[i].zone == ZoneType.RESTRICTED and
                          drone.path[i - 2] != drone.path[i]))):
                if drone.path[i].zone == ZoneType.RESTRICTED:
                    count[i] += 1
                count[i] += 1
                print(f"D{drone.drone_id}-{drone.path[i].name}", end=" ")
        print(end="\n")
    return count
