from fastapi import FastAPI, Query
import httpx

app = FastAPI()

OSRM_URL = "https://router.project-osrm.org"


def accuracy(steps, points):
    # konfiguracja dokladnosci, parametr steps = ile pnkt chcemy max,
    #  bierzemy co n-ty punkt zeby dalo mniej wiecej tyle ile mu podamy w steps
    total = len(points)
    if total <= steps:
        selected_points = points
    else:
        step_size = total / steps
        selected_points = [points[int(i * step_size)] for i in range(steps)]
        # dodajemy ostatni punkt zeby trasa sie zawsze konczyla tam gdzie powinna
        if selected_points[-1] != points[-1]:
            selected_points.append(points[-1])
    return selected_points


@app.get("/route")
async def get_route(
    start_lat: float = Query(..., description="Latitude punktu startowego"),
    start_lng: float = Query(..., description="Longitude punktu startowego"),
    end_lat: float = Query(..., description="Latitude punktu koncowego"),
    end_lng: float = Query(..., description="Longitude punktu koncowego"),
    steps: int = Query(500, description="Ile punktow max na trasie (więcej = dokladniej)"),
):
    # OSRM chce format /route/v1/driving/lng,lat;lng,lat
    coordinates = f"{start_lng},{start_lat};{end_lng},{end_lat}"
    url = f"{OSRM_URL}/route/v1/driving/{coordinates}"

    # Jakbysmy zmienili z full na simplified to OSRM sam robi uproszczenie trasy za nas, ale nie mamy kontroli ile pnkt dostaniemy
    params = {
        "overview": "full",
        "geometries": "geojson",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()

    # OSRM zwraca table routes z lista punktow [lng, lat] wzdluz trasy
    route = data["routes"][0]
    all_points = route["geometry"]["coordinates"]

    selected_points = accuracy(steps, all_points)

    # GeoJSON LineString
    # takie cos mi czat dal ale chyba dziala xd
    geojson = {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": selected_points,
        },
        "properties": {
            "distance_m": route["distance"],
            "duration_s": route["duration"],
            "total_points_from_osrm": len(all_points),
            "points_returned": len(selected_points),
        },
    }

    return geojson
