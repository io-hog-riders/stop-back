from fastapi import APIRouter

from db.models.plan import RoutePlanResponse
from services.plan.service import plan_route_mock, modify_route_mock

router = APIRouter(prefix="/api/v1/route", tags=["Plan"])

@router.post("/plan", response_model=RoutePlanResponse)
async def plan_route_endpoint(request: dict) -> RoutePlanResponse:
    # TODO
    return plan_route_mock()


@router.put("/plan", response_model=RoutePlanResponse)
async def modify_route_endpoint(request: dict) -> RoutePlanResponse:
    #TODO
    return modify_route_mock()