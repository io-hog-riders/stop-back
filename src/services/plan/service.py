import httpx
import math
from db.models.common import Location
from db.models.plan import NameSearchResult, Route

OSRM_URL = "https://router.project-osrm.org"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

async def calculate_route(waypoints: list[Location],steps: int = 1000,) -> Route:
    # OSRM chce format /route/v1/driving/lng,lat;lng,lat ,
    # mozna wiele pkt w jednym requescie, po prostu trzeba je odseparowac ";'
    coords_str = ";".join(f"{p.lng},{p.lat}" for p in waypoints)
    url = f"{OSRM_URL}/route/v1/driving/{coords_str}"

    # Jakbysmy zmienili z full na simplified to OSRM sam robi uproszczenie trasy za nas, ale nie mamy kontroli ile pnkt dostaniemy
    params = {
        "overview": "full",
        "geometries": "geojson",
        "annotations": "duration"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()

    # OSRM zwraca table routes z lista punktow [lng, lat] wzdluz trasy
    route = data["routes"][0]
    all_coords = route["geometry"]["coordinates"]

    # Sklejamy annotation.duration ze wszystkich legs w jedna tablice
    # jesli mamy N waypointow to mamy N-1 legs, kazdy z wlasna annotation
    # annotation.duration to tablica czasow segmentow miedzy kolejnymi punktami
    segment_durations: list[float] = []
    for leg in route["legs"]:
        segment_durations.extend(leg["annotation"]["duration"])

    # dla kazdego punktu liczymy czas od startu
    point_durations: list[int] = [0]
    running = 0.0
    for d in segment_durations:
        running += d
        point_durations.append(int(running))

    all_coords, point_durations = simplify(all_coords, point_durations, steps)

    points = [Location(lat=lat, lng=lng) for lng, lat in all_coords]

    return Route(
        distance=int(route["distance"]),
        duration=int(route["duration"]),
        points=points,
        point_durations=point_durations,
    )


def simplify(coords: list[list[float]], durations: list[int], steps: int,) -> tuple[list[list[float]], list[int]]:
    # konfiguracja dokladnosci, parametr steps = ile pnkt chcemy max,
    # bierzemy co n-ty punkt zeby dalo mniej wiecej tyle ile mu podamy w steps
    total = len(coords)
    if total <= steps:
        return coords, durations

    step_size = total / steps
    selected_coords = [coords[int(i * step_size)] for i in range(steps)]
    selected_durs = [durations[int(i * step_size)] for i in range(steps)]

    # dodajemy ostatni punkt zeby trasa sie zawsze konczyla tam gdzie powinna
    if selected_coords[-1] != coords[-1]:
        selected_coords.append(coords[-1])
        selected_durs.append(durations[-1])

    return selected_coords, selected_durs


async def search_name_coordinates(
    name_search: str,
    limit: int = 5,
    center_lat: float | None = None,
    center_lng: float | None = None,
    radius_km: float = 25.0
) -> list[NameSearchResult]:
    if (center_lat is None) != (center_lng is None):
        raise ValueError("center_lat and center_lng must be provided together")

    if radius_km is not None and center_lat is None:
        raise ValueError("radius_km requires center_lat and center_lng")

    if radius_km is not None and radius_km <= 0:
        raise ValueError("radius_km must be greater than 0")

    params = {
        "q": name_search,
        "format": "jsonv2",
        "limit": limit,
    }

    if center_lat is not None and center_lng is not None:
        params["viewbox"] = _build_viewbox(center_lat, center_lng, radius_km)
        params["bounded"] = 1


    async with httpx.AsyncClient() as client:
        response = await client.get(NOMINATIM_URL, params=params)
        response.raise_for_status()
        data = response.json()

    results: list[NameSearchResult] = []
    for item in data:
        try:
            lat = float(item["lat"])
            lon = float(item["lon"])
            display_name = item.get("display_name") or item.get("name") or name_search
        except (KeyError, TypeError, ValueError):
            continue

        results.append(
            NameSearchResult(
                name=display_name,
                location=Location(lat=lat, lng=lon),
            )
        )

    return results


def _build_viewbox(center_lat: float, center_lng: float, radius_km: float) -> str:
    lat_delta = radius_km / 111.0
    cos_lat = max(math.cos(math.radians(center_lat)), 0.01)
    lng_delta = radius_km / (111.320 * cos_lat)

    south = max(-90.0, center_lat - lat_delta)
    north = min(90.0, center_lat + lat_delta)
    west = max(-180.0, center_lng - lng_delta)
    east = min(180.0, center_lng + lng_delta)

    # Nominatim viewbox format: left,top,right,bottom => west,north,east,south
    return f"{west},{north},{east},{south}"