import httpx
from fastapi import APIRouter, HTTPException

import services.plan.service as plan_service
from db.models.plan import RoutePlanRequest, RoutePlanResponse
import services.stops.service as stop_service

router = APIRouter(tags=["Plan"])


@router.post("/plan", response_model=RoutePlanResponse)
async def create_route_plan(request: RoutePlanRequest, steps: int = 1000) -> RoutePlanResponse:

    waypoints = [request.origin, request.destination]
    route = await plan_service.calculate_route(waypoints, steps)
    try:
        suggested_stops =  await stop_service.get_stops_along_route(route=route, stops_config=request.stops_config)
    except (httpx.HTTPStatusError, httpx.RequestError):
        suggested_stops = []
    return RoutePlanResponse(route=route, suggestedStops=suggested_stops)


@router.put("/plan", response_model=RoutePlanResponse)
async def update_route_plan(request: dict) -> RoutePlanResponse:
    #TODO
    raise NotImplementedError()
