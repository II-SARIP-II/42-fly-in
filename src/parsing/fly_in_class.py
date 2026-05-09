from pydantic import BaseModel, model_validator, Field
from enum import Enum
from typing_extensions import Self
from typing import List, Any


class ZoneType(Enum):
    '''
    All possible zone types
    '''
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Hub(BaseModel):
    '''
    Hub class to store each specification of hub
    '''
    name: str
    x: int
    y: int
    is_start: bool = Field(default=False)
    is_end: bool = Field(default=False)
    zone: ZoneType = Field(default=ZoneType.NORMAL)
    color: str = Field(default="gray")
    max_drones: int = Field(default=1)

    @model_validator(mode='after')
    def valid_name(self) -> Self:
        if "\\" in self.name or "/" in self.name or ":" in self.name:
            raise ValueError("The connection syntax forbids "
                             "dashes in zone names")
        else:
            return self


class Connection(BaseModel):
    '''
    Connection class to store each specification of connections
    '''
    connection_id: int
    hub1: Hub
    hub2: Hub
    max_link_capacity: int = Field(default=1)
    nb_drones_in: List[Any] = Field(default=[])


class Drone(BaseModel):
    '''
    Drones class to get their id and their path
    '''
    drone_id: int
    path: List[Hub] = Field(default=[])


class Input_Data(BaseModel):
    '''
    Input_Data class to store all drones, all hubs, and all connections
        from the simulation
    '''
    lst_drones: List[Drone] = Field(default=[])
    hubs: List[Hub] = Field(default=[])
    connections: List[Connection] = Field(default=[])
