import sys

from .fly_in_class import Drone, Hub, Connection, Input_Data, ZoneType

from typing import List, Dict, Any


def create_hub_metadata(data: str,
                        hub_data: Dict[str, Any]
                        ) -> tuple[str, Dict[str, Any]]:
    '''
    Get the meta data of the hub fron the line
    Params:
        data: str = the line after 'hub_name:'
        hub_data: Dict[str, Any] = The dictionnary to store hubs data to
            create the hub
    Return value:
        tuple[str, Dict[str, Any]] = str is the line without hub_name and the
            meta data and Dict is hub_data with meta data in it
    '''
    data, meta = data.split(" [")
    import re
    if len(re.findall(r"\[", meta)) != 0 or len(re.findall(r"\]", meta)) != 1:
        raise ValueError("Input Error: Metadata: "
                         "[ or ] format not respected")
    meta = meta.replace("]", "")
    lst_meta = meta.split()
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
                if hub_data["max_drones"] < 1:
                    raise ValueError("Input Error: max_drones must be > 0")
            case _:
                raise ValueError("Input Error: Only zone, color and "
                                 "max_drones can be in meta data")
    return data, hub_data


def create_hub(line: str) -> tuple[Hub, bool, bool]:
    '''
    Create hub with the line from the input file
    Params:
        line: str = line from the file
    Return value:
        Hub: Hub = the created hub
        bool = to know if the created hub was the start
        bool = to know if the created hub was the end
    '''
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
    if title == "end_hub":
        hub_data["is_end"] = True
    if "  " in data:
        raise ValueError("Too much spaces detected")
    if " [" in data:
        if "]" != line[-1:]:
            raise ValueError("Input Error: line must end with ] "
                             "if metadata are passed")
        try:
            data, hub_data = create_hub_metadata(data, hub_data)
        except Exception as e:
            raise ValueError(e)
    lst_major = data.split(" ")
    if len(lst_major) != 3:
        raise ValueError("Input Error: the hub creation must be define "
                         "as 'name(string) x(integer) y(integer)'")
    hub_data["name"] = str(lst_major[0])
    hub_data["x"] = int(lst_major[1])
    hub_data["y"] = int(lst_major[2])
    return Hub(**hub_data), hub_data["is_start"], hub_data["is_end"]


def create_connection(line: str,
                      lst_hubs: List[Hub],
                      connections: List[Connection]
                      ) -> Connection:
    '''
    Create the connection between to hubs
    Params:
        line: str = line from the file
        lst_hubs: List[Hub] = to verify if the hubs around the connection
            exists
        connections: List[Connection] = To look at duplicate connections
    Return value:
        Connection: The created connection
    '''
    try:
        title, data = line.split(": ")
    except Exception:
        raise ValueError("Input Error: connection lines "
                         "must be 'connection: hub1-hub2'")
    if title != "connection":
        raise ValueError("Input Error: connection lines "
                         "must be 'connection: hub1-hub2'")
    max_link = 1
    if "  " in data:
        raise ValueError("Too much spaces detected")
    if " [" in data:
        if "]" != line[-1:]:
            raise ValueError("Input Error: line must end with ] "
                             "if metadata are passed")
        data, metadata = data.split(" [")
        metadata = metadata.replace("]", "")
        try:
            meta_title, max_link_str = metadata.split("=")
            if meta_title != "max_link_capacity":
                raise ValueError
            max_link = int(max_link_str)
            if max_link < 1:
                raise ValueError("Input Error: max_link_capacity must be >")
        except Exception:
            raise ValueError("Input Error: max_link_capacity must be an "
                             "int > 0 and define like: [max_link_capacity=1]")
    try:
        name1, name2 = data.split("-")
    except Exception:
        raise ValueError("Input Error: connection lines "
                         "must be 'connection: hub1-hub2'")
    hub_map = {hub.name: hub for hub in lst_hubs}
    if name1 not in hub_map or name2 not in hub_map:
        raise ValueError(f"Input Error: {data}, connection is invalid")
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
    '''
    Get the number of drones and create the list of drones
    Params:
        line: str = the drone's line
        idx: int = the idex of the drone's line
        lst_drones: List[Drone] = The list to create
        set_drone: bool = True if drone list has already been created
    Return Value:
        List[Drone] = List of all drone initialised with their id
    '''
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
    if nb_drone < 1:
        raise ValueError(f"Error in line {idx}: Input Error: "
                         "nb_drones must be greater than 0")
    return lst_drones


def read_file(filename: str) -> Input_Data:
    '''
    Function to read the file and create hubs, connections and drones
    Params:
        filename: str = the file to read and get the informations
    Return value:
        Input_Data: All data stored in this class
    '''
    with open(filename, 'r') as f:
        lst = f.read().splitlines()
    set_drone = False
    lst_drones: List[Drone] = []
    hubs: List[Hub] = []
    connections: List[Connection] = []
    is_end = False
    is_start = False
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
                hub, temp_start, temp_end = create_hub(line)
                for h in hubs:
                    if h.name == hub.name:
                        raise ValueError("duplicate hub name")
                    if h.x == hub.x and h.y == hub.y:
                        raise ValueError("duplicate hub position")
                if temp_end and is_end:
                    raise ValueError("It must be only one end")
                elif temp_end:
                    if len(lst_drones) > hub.max_drones:
                        raise ValueError("Not enough capacity in end hub")
                    is_end = True
                if temp_start and is_start:
                    raise ValueError("It must be only one start")
                elif temp_start:
                    if len(lst_drones) > hub.max_drones:
                        raise ValueError("Not enough capacity in start hub")
                    is_start = True
                if ((hub.is_start or hub.is_end)
                        and hub.zone == ZoneType.BLOCKED):
                    raise ValueError("Start and End cannot be blocked")
                hubs.append(hub)
            except Exception as e:
                raise ValueError(f"Error in line {idx+1}: {e}")

        elif line.startswith("connection:"):
            if not set_drone:
                raise ValueError(f"Error in line {idx+1}: Input Error: "
                                 "The file must start with nb_drones: X")
            if not is_start or not is_end:
                raise ValueError(f"Error in line {idx+1}: Input Error: "
                                 "Define hubs before connections")
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
    '''
    Get the argv and read it and return data from read_file()
    '''
    if len(sys.argv) != 2:
        raise ValueError("Program should be run with "
                         "'python3 -m src path/to/input_file.txt'")
    try:
        input_data: Input_Data = read_file(sys.argv[1])
        return input_data
    except Exception as e:
        raise Exception(e)
