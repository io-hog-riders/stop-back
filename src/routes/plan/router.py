from fastapi import APIRouter

import services.plan.service as service
from db.models.plan import RoutePlanRequest, RoutePlanResponse

router = APIRouter(tags=["Plan"])


@router.post("/plan", response_model=RoutePlanResponse)
async def create_route_plan(request: RoutePlanRequest, steps: int = 1000) -> RoutePlanResponse:

    waypoints = [request.origin, request.destination]
    route = await service.calculate_route(waypoints, steps)

    return RoutePlanResponse(route=route, suggestedStops=[])


@router.put("/plan", response_model=RoutePlanResponse)
async def update_route_plan(request: dict) -> RoutePlanResponse:
    #TODO
    raise NotImplementedError()
