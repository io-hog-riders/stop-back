from fastapi import APIRouter

import services.plan.mock as mock 
from db.models.plan import RoutePlanResponse

router = APIRouter(tags=["Plan"])

@router.post("/plan", response_model=RoutePlanResponse)
async def create_route_plan(_: dict) -> RoutePlanResponse:
    return mock.create_route_plan()

@router.put("/plan", response_model=RoutePlanResponse)
async def update_route_plan(_: dict) -> RoutePlanResponse:
    return mock.update_route_plan()