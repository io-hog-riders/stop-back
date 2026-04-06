from fastapi import APIRouter

from db.models.stops import Stop, StopType
from services.stops.service import get_stop_types

router = APIRouter(prefix="/api/mock/stops", tags=["stops"])

@router.get("/types", response_model=list[StopType])
async def get_stop_types_endpoint():
    return get_stop_types()