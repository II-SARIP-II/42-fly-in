from ..parsing.fly_in_class import Drone, ZoneType

from typing import List, Dict


def build_output(drones: List[Drone]) -> Dict[int, int]:
    if not drones:
        return {}

    max_drone_path = max([len(drone.path) for drone in drones])
    count: Dict[int, int] = {}

    for i in range(max_drone_path):
        count[i] = count[i - 1] if i > 0 else 0
        if i == 0:
            continue

        print(f"t{i}: ", end="")
        for drone in drones:
            if i >= len(drone.path):
                continue
            current_node = drone.path[i]
            prev_node = drone.path[i-1]

            if current_node.zone == ZoneType.RESTRICTED:
                if prev_node != current_node:
                    print(f"D{drone.drone_id}-{prev_node.name}"
                          f"-{current_node.name}", end=" ")
                    count[i] += 1
                elif i >= 2 and i-2 < len(drone.path):
                    if drone.path[i-2] != current_node:
                        print(f"D{drone.drone_id}-{current_node.name}",
                              end=" ")
                        count[i] += 1
            elif current_node != prev_node:
                print(f"D{drone.drone_id}-{current_node.name}", end=" ")
                count[i] += 1
        print()

    return count
