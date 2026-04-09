from fastapi import APIRouter

import services.stops.mock as mock 
from db.models.stops import StopType

router = APIRouter(tags=["Stops"])

@router.get("/types", response_model=list[StopType])
async def get_stop_types():
    return mock.get_stop_types()