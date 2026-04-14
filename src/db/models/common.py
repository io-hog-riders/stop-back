from typing import Optional

from pydantic import BaseModel, Field


class Location(BaseModel):
    lat: float
    lng: float

class OpeningHours(BaseModel):
    opens: str
    closes: str

class OpeningTimes(BaseModel):
    monday: Optional[OpeningHours] = None
    tuesday: Optional[OpeningHours] = None
    wednesday: Optional[OpeningHours] = None
    thursday: Optional[OpeningHours] = None
    friday: Optional[OpeningHours] = None
    saturday: Optional[OpeningHours] = None
    sunday: Optional[OpeningHours] = None


class Rating(BaseModel):
    rate: Optional[int] = Field(ge=0, le=5)