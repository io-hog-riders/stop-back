from fastapi import APIRouter

import services.stops.service as service
from db.models.stops import StopType

router = APIRouter(tags=["Stops"])

@router.get("/types", response_model=StopType)
async def get_stop_types():
    # TODO:
    raise NotImplementedError()
