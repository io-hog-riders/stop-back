import httpx
from fastapi import APIRouter, HTTPException, Query, status

import services.plan.service as service
from db.models.plan import NameSearchResult, RoutePlanRequest, RoutePlanResponse

router = APIRouter(tags=["Plan"])


@router.post("/plan", response_model=RoutePlanResponse)
async def create_route_plan(request: RoutePlanRequest, steps: int = 1000) -> RoutePlanResponse:

    route = await service.calculate_route(request.waypoints, steps)

    return RoutePlanResponse(route=route, suggestedStops=[])


@router.get("/search", response_model=list[NameSearchResult])
async def name_search(
    name_search: str = Query(min_length=2, max_length=200),
    limit: int = Query(default=5, ge=1, le=10),
    center_lat: float | None = Query(default=None, ge=-90, le=90),
    center_lng: float | None = Query(default=None, ge=-180, le=180),
    radius_km: float = Query(default=25.0, gt=0, le=300),
) -> list[NameSearchResult]:
    try:
        return await service.search_name_coordinates(
            name_search=name_search,
            limit=limit,
            center_lat=center_lat,
            center_lng=center_lng,
            radius_km=radius_km,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except (httpx.RequestError, httpx.HTTPStatusError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Name search service is unavailable",
        ) from exc
