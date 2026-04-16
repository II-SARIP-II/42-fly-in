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


class ColorList(Enum):
    NONE = "none"
    GRAY = "gray"
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    PINK = "pink"
    ORANGE = "orange"
    YELLOW = "yellow"
    BROWN = "brown"
    PURPLE = "purple"
    MAROON = "maroon"
    GOLD = "gold"
    DARKRED = "darkred"
    BLACK = "black"
    WHITE = "white"
    VIOLET = "violet"
    CRIMSON = "crimson"
    RAINBOW = "rainbow"
    CYAN = "cyan"
    LIME = "lime"
    MAGENTA = "magenta"


class Hub(BaseModel):
    name: str
    x: int
    y: int
    is_start: bool = Field(default=False)
    is_end: bool = Field(default=False)
    zone: ZoneType = Field(default=ZoneType.NORMAL)
    color: ColorList = Field(default=ColorList.NONE)
    max_drones: int = Field(default=1)


class Connection(BaseModel):
    hub1: str
    hub2: str
    max_link_capacity: int = Field(default=1)
# The connection syntax forbids dashes in zone names.


class Input_Datas(BaseModel):
    nb_drones: int = Field(ge=0)
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


def create_hub_metadata(datas: str,
                        hub_data: Dict[str, Any]
                        ) -> tuple[str, Dict[str, Any]]:
    datas, meta = datas.split(" [")
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
                    hub_data["color"] = ColorList(metavalue.lower())
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
    return datas, hub_data


def create_hub(line: str) -> Hub:
    title, datas = line.split(": ")
    hub_data: Dict[str, Any] = {
        "is_start": False,
        "is_end": False,
    }
    if title not in ["start_hub", "hub", "end_hub"]:
        raise ValueError("Input Error: lines can only start with"
                         " start_hub, hub, end_hub for hubs creations")
    if title == "start_hub":
        hub_data["is_start"] = True
    if title == "end_hub":
        hub_data["is_end"] = True
    if " [" in datas:
        try:
            datas, hub_data = create_hub_metadata(datas, hub_data)
        except Exception as e:
            raise ValidationError(e)
    lst_major = datas.split(" ")
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
        title, datas = line.split(": ")
    except Exception:
        raise ValueError("Input Error: connection lines "
                         "must be 'connection: hub1-hub2'")
    if title != "connection":
        raise ValueError("Input Error: connection lines "
                         "must be 'connection: hub1-hub2'")
    max_link = 1
    if " [max_link_capacity=" in datas:
        datas, metadata = datas.split(" [")
        metadata = metadata.replace("]", "")
        try:
            max_link = int(metadata.split("=")[1])
        except Exception:
            raise ValueError("Input Error: max_link_capacity must be an "
                             "int and define like this: [max_link_capacity=1]")
    try:
        hub1, hub2 = datas.split("-")
    except Exception:
        raise ValueError("Input Error: connection lines "
                         "must be 'connection: hub1-hub2'")
    name_lst = [item.name for item in lst_hubs]
    if hub1 not in name_lst or hub2 not in name_lst:
        raise ValueError(f"Input Error: {datas}, one or more hubs are invalid")
    lst_connection = [[item.hub1, item.hub2] for item in connections]
    if [hub1, hub2] in lst_connection or [hub2, hub1] in lst_connection:
        raise ValueError(f"Input Error: {datas}, connection already exist")
    return Connection(hub1=hub1, hub2=hub2, max_link_capacity=max_link)


def drone_line(line: str, idx: int, nb_drone: int, set_drone: bool) -> int:
    if set_drone:
        raise ValueError(f"Error in line {idx}: Input Error: "
                         "nb_drones already set")
    try:
        nb_drone = int(line.split(":")[1])
    except Exception:
        raise ValueError(f"Error in line {idx}: Input Error: "
                         "nb_drones must be an integer")
    if nb_drone < 0:
        raise ValueError(f"Error in line {idx}: Input Error: "
                         "nb_drones must be positive")
    return nb_drone


def read_file(filename: str) -> Input_Datas:
    with open(filename, 'r') as f:
        lst = f.read().splitlines()
    set_drone = False
    nb_drone = -1
    hubs: List[Hub] = []
    connections: List[Connection] = []
    for idx, line in enumerate(lst):
        if line.startswith("nb_drones: "):
            try:
                nb_drone = drone_line(line, idx+1, nb_drone, set_drone)
                set_drone = True
            except Exception as e:
                raise ValueError(e)

        elif line.startswith(("hub:", "start_hub:", "end_hub:")):
            if not set_drone:
                raise ValueError(f"Error in line {idx+1}: Input Error: "
                                 "The file must start with nb_drones: X")
            try:
                hubs.append(create_hub(line))
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

    return Input_Datas(nb_drones=nb_drone, hubs=hubs, connections=connections)


def parsing() -> Input_Datas:
    if len(sys.argv) != 2:
        raise ValueError("Program should be run with "
                         "'python3 -m src path/to/input_file.txt'")
    try:
        input_datas: Input_Datas = read_file(sys.argv[1])
        return(input_datas)
    except ValidationError as e:
        raise ValidationError(e.errors()[0]['msg'])
    except Exception as e:
        raise Exception(e)
