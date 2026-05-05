from pydantic import BaseModel, model_validator, Field, ValidationError

from enum import Enum

from typing_extensions import Self
from typing import List, Any


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

    @model_validator(mode='after')
    def valid_name(self) -> Self:
        if "\\" in self.name or "/" in self.name or ":" in self.name:
            raise ValidationError("The connection syntax forbids "
                                  "dashes in zone names")
        else:
            return self


class Connection(BaseModel):
    connection_id: int
    hub1: Hub
    hub2: Hub
    max_link_capacity: int = Field(default=1)
    nb_drones_in: List[Any] = Field(default=[])


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
