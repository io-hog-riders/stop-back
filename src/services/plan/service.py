import httpx
from db.models.common import Location
from db.models.plan import Route

OSRM_URL = "https://router.project-osrm.org"

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
