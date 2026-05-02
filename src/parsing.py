from pydantic import BaseModel, model_validator, Field, ValidationError
from enum import Enum
from typing import List, Dict, Any
from typing_extensions import Self
import sys


class ZoneType(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Hub(BaseModel):
    name: str
    x: int
    y: int
    is_start: bool = Field(default=False)
    is_end: bool = Field(default=False)
    zone: ZoneType = Field(default=ZoneType.NORMAL)
    color: str = Field(default="gray")
    max_drones: int = Field(default=1)
    nb_drones_in: List[Any] = Field(default=[])


class Connection(BaseModel):
    connection_id: int
    hub1: Hub
    hub2: Hub
    max_link_capacity: int = Field(default=1)
    nb_drones_in: List[Any] = Field(default=[])
    # The connection syntax forbids dashes in zone names.


class Drone(BaseModel):
    drone_id: int
    path: List[Hub] = Field(default=[])


class Input_Data(BaseModel):
    lst_drones: List[Drone] = Field(default=[])
    hubs: List[Hub] = Field(default=[])
    connections: List[Connection] = Field(default=[])

    @model_validator(mode='after')
    def valid_start_end(self) -> Self:
        is_end = False
        is_start = False
        for hub in self.hubs:
            if hub.is_start and is_start:
                raise ValidationError("Input Error: It can only have "
                                      "one start hub")
            if hub.is_end and is_end:
                raise ValidationError("Input Error: It can only have "
                                      "one end hub")
            if hub.is_start and not is_start:
                is_start = True
            if hub.is_end and not is_end:
                is_end = True
        return self


def create_hub_metadata(data: str,
                        hub_data: Dict[str, Any]
                        ) -> tuple[str, Dict[str, Any]]:
    data, meta = data.split(" [")
    meta = meta.replace("]", "")
    lst_meta = meta.split(" ")
    for item in lst_meta:
        key, metavalue = item.split("=")
        match key:
            case "zone":
                try:
                    hub_data["zone"] = ZoneType(metavalue.lower())
                except Exception:
                    raise ValueError("Input Error: Metadata: "
                                     "the zone value is unknown")
            case "color":
                try:
                    hub_data["color"] = metavalue.lower()
                except KeyError:
                    raise ValueError("Input Error: Metadata: "
                                     "the color value is unknown")
            case "max_drones":
                try:
                    hub_data["max_drones"] = int(metavalue)
                except Exception:
                    raise ValueError("Input Error: Metadata: "
                                     "the max_drones value must be an integer")
            case _:
                raise ValueError("Input Error: Only zone, color and "
                                 "max_drones can be in meta data")
    return data, hub_data


def create_hub(line: str, lst_drones: List[Drone]) -> Hub:
    title, data = line.split(": ")
    hub_data: Dict[str, Any] = {
        "is_start": False,
        "is_end": False,
    }
    if title not in ["start_hub", "hub", "end_hub"]:
        raise ValueError("Input Error: lines can only start with"
                         " start_hub, hub, end_hub for hubs creations")
    if title == "start_hub":
        hub_data["is_start"] = True
        hub_data["nb_drones_in"] = lst_drones
    if title == "end_hub":
        hub_data["is_end"] = True
    if " [" in data:
        try:
            data, hub_data = create_hub_metadata(data, hub_data)
        except Exception as e:
            raise ValidationError(e)
    lst_major = data.split(" ")
    if len(lst_major) != 3:
        raise ValueError("Input Error: the hub creation must be define "
                         "as 'name(string) x(integer) y(integer)'")
    hub_data["name"] = str(lst_major[0])
    hub_data["x"] = int(lst_major[1])
    hub_data["y"] = int(lst_major[2])
    return Hub(**hub_data)


def create_connection(line: str,
                      lst_hubs: List[Hub],
                      connections: List[Connection]
                      ) -> Connection:
    try:
        title, data = line.split(": ")
    except Exception:
        raise ValueError("Input Error: connection lines "
                         "must be 'connection: hub1-hub2'")
    if title != "connection":
        raise ValueError("Input Error: connection lines "
                         "must be 'connection: hub1-hub2'")
    max_link = 1
    if " [max_link_capacity=" in data:
        data, metadata = data.split(" [")
        metadata = metadata.replace("]", "")
        try:
            max_link = int(metadata.split("=")[1])
        except Exception:
            raise ValueError("Input Error: max_link_capacity must be an "
                             "int and define like this: [max_link_capacity=1]")
    try:
        name1, name2 = data.split("-")
    except Exception:
        raise ValueError("Input Error: connection lines "
                         "must be 'connection: hub1-hub2'")
    hub_map = {hub.name: hub for hub in lst_hubs}
    if name1 not in hub_map or name2 not in hub_map:
        raise ValueError(f"Input Error: {data}, one or more hubs are invalid")
    hub1 = hub_map[name1]
    hub2 = hub_map[name2]
    next_id = 0
    for conn in connections:
        next_id = conn.connection_id + 1
        existing_names = {conn.hub1.name, conn.hub2.name}
        if {name1, name2} == existing_names:
            raise ValueError(f"Input Error: {data}, connection already exists")
    return Connection(hub1=hub1,
                      hub2=hub2,
                      max_link_capacity=max_link,
                      connection_id=next_id)


def drone_line(line: str,
               idx: int,
               lst_drones: List[Drone],
               set_drone: bool
               ) -> List[Drone]:
    if set_drone:
        raise ValueError(f"Error in line {idx}: Input Error: "
                         "nb_drones already set")
    try:
        nb_drone = int(line.split(":")[1].strip())
        for i in range(nb_drone):
            new_drone = Drone(drone_id=i)
            lst_drones.append(new_drone)
    except Exception:
        raise ValueError(f"Error in line {idx}: Input Error: "
                         "nb_drones must be an integer")
    if nb_drone < 0:
        raise ValueError(f"Error in line {idx}: Input Error: "
                         "nb_drones must be positive")
    return lst_drones


def read_file(filename: str) -> Input_Data:
    with open(filename, 'r') as f:
        lst = f.read().splitlines()
    set_drone = False
    lst_drones: List[Drone] = []
    hubs: List[Hub] = []
    connections: List[Connection] = []
    for idx, line in enumerate(lst):
        if line.startswith("nb_drones: "):
            try:
                lst_drones = drone_line(line, idx+1, lst_drones, set_drone)
                set_drone = True
            except Exception as e:
                raise ValueError(e)

        elif line.startswith(("hub:", "start_hub:", "end_hub:")):
            if not set_drone:
                raise ValueError(f"Error in line {idx+1}: Input Error: "
                                 "The file must start with nb_drones: X")
            try:
                hubs.append(create_hub(line, lst_drones))
            except Exception as e:
                raise ValueError(f"Error in line {idx+1}: {e}")

        elif line.startswith("connection:"):
            if not set_drone:
                raise ValueError(f"Error in line {idx+1}: Input Error: "
                                 "The file must start with nb_drones: X")
            try:
                connections.append(create_connection(line, hubs, connections))
            except Exception as e:
                raise ValueError(f"Error in line {idx+1}: {e}")

        elif line.startswith("#") or line == "":
            pass

        else:
            raise ValueError(f"Error in line {idx+1}: unknown line")

    return Input_Data(lst_drones=lst_drones,
                      hubs=hubs,
                      connections=connections)


def parsing() -> Input_Data:
    if len(sys.argv) != 2:
        raise ValueError("Program should be run with "
                         "'python3 -m src path/to/input_file.txt'")
    try:
        input_data: Input_Data = read_file(sys.argv[1])
        return input_data
    except ValidationError as e:
        raise ValidationError(e.errors()[0]['msg'])
    except Exception as e:
        raise Exception(e)
