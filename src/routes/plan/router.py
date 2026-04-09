from fastapi import APIRouter

import services.plan.service as service
from db.models.plan import RoutePlanResponse

router = APIRouter(tags=["Plan"])

@router.post("/plan", response_model=RoutePlanResponse)
async def create_route_plan(request: dict) -> RoutePlanResponse:
    # TODO
    raise NotImplementedError()


@router.put("/plan", response_model=RoutePlanResponse)
async def update_route_plan(request: dict) -> RoutePlanResponse:
    #TODO
    raise NotImplementedError()
