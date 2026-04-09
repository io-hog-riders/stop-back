from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from db.models.common import Location
from db.models.stops import Stop


class Route(BaseModel):
    distance: int
    duration: int
    points: list[Location]


class RoutePlanResponse(BaseModel):
    route: Route
    suggestedStops: list[Stop]
