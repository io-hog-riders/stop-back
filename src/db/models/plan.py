from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from db.models.common import Location
from db.models.stops import Stop, StopsConfig


class Route(BaseModel):
    distance: int
    duration: int
    points: list[Location]
    point_durations: Optional[list[int]] = None


class RoutePlanResponse(BaseModel):
    route: Route
    suggestedStops: list[Stop]


class RoutePlanRequest(BaseModel):
    waypoints: list[Location]
    stops_config: StopsConfig
    routeOptions: Optional[dict] = None


class NameSearchResult(BaseModel):
    name: str
    location: Location
