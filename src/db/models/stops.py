from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from db.models.common import Location, OpeningTimes, Rating


class StopType(str, Enum):
    restaurant = "restaurant"
    gas_station = "gas_station"
    hotel = "hotel"
    rest_area = "rest_area"
    charging_station = "charging_station"
    attraction = "attraction"
    parking = "parking"
    hospital = "hospital"


class StopIdent(BaseModel):
    id: str
    type: StopType
    name: str
    location: Location
    address: str

class Stop(BaseModel):
    ident: StopIdent
    detourDistance: int
    detourTime: int
    website: Optional[str] = None
    openingHours: Optional[OpeningTimes] = None
    rating: Optional[Rating] = None


class SortBy(str, Enum):
    rating = "rating"
    distance = "distance"
    price = "price"

class StopOptions(BaseModel):
    type: StopType
    maxDetour: int
    limit: int
    atJourneyMinute: int
    targetPercent: int
    sortBy: SortBy = Field(
        default=SortBy.distance
    )

class StopsConfig(BaseModel):
    stops: list[StopOptions]