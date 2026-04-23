from typing import Any

import httpx
import random
import asyncio

from db.models.common import Location
from db.models.plan import Route
from db.models.stops import (
    Stop,
    StopIdent,
    StopOptions,
    StopsConfig,
    StopType,
)
from services.stops.utils import estimate_distance_to_point, sort_stops, deduplicate_elements, \
    find_route_point_at_percent

#Podejscie oparte na szukaniu tylko w obrębie jednego punktu na trasie

#przy każdej próbie próbujemy innego serwera
OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
#póki co nasz detour time to sztywno detour_distance/300
DETOUR_TIME_MULTIPLIER = 1/300

#zamiana na te śmieszne typy OSM
STOP_TYPE_TO_OSM = {
    StopType.restaurant: ("amenity", "restaurant"),
    StopType.gas_station: ("amenity", "fuel"),
    StopType.hotel: ("tourism", "hotel"),
    StopType.rest_area: ("highway", "rest_area"),
    StopType.charging_station: ("amenity", "charging_station"),
    StopType.attraction: ("tourism", "attraction"),
    StopType.parking: ("amenity", "parking"),
    StopType.hospital: ("amenity", "hospital"),
}


async def find_stops_along_route(route: Route, stops_config: StopsConfig) -> list[Stop]:
    all_stops: list[Stop] = []

    #szukamy po kolei dla każdego wybranego rodzaju stopu
    #dzieki temu mniejsze zapytanie + wywalenie jednego nie psuje całości
    for stop_option in stops_config.stops:
        try:
            stops_for_type = await find_stops_for_option(route, stop_option)
        except httpx.HTTPError as exc:
            print("Not found for:", stop_option)
            print("HTTP ERROR TYPE:", type(exc).__name__)
            print("HTTP ERROR:", exc)

            if isinstance(exc, httpx.HTTPStatusError):
                print("STATUS CODE:", exc.response.status_code)
                print("RESPONSE TEXT:", exc.response.text)
            stops_for_type = []
        all_stops.extend(stops_for_type)

    return all_stops

#Odpytujemy Overpassa o dane miejsce
async def find_stops_for_option(route: Route, stop_option: StopOptions) -> list[Stop]:
    osm_key, osm_value = STOP_TYPE_TO_OSM[stop_option.type]

    #punkt w okół którego bedziemy szukać
    target_point = find_route_point_at_percent(route.points, stop_option.targetPercent)

    query = build_overpass_query(
        point=target_point,
        osm_key=osm_key,
        osm_value=osm_value,
        radius_m=stop_option.maxDetour,
    )

    print("TARGET POINT:", target_point)
    print("RADIUS:", stop_option.maxDetour)
    print("OVERPASS QUERY:")
    print(query)
    async with httpx.AsyncClient(timeout=50.0) as client:
        data = await fetch_with_retry(client, query)
        print("OVERPASS DATA:", data)
    if not data:
        return []
    elements = deduplicate_elements(data.get("elements", []))
    print("ELEMENTS COUNT:", len(elements))

    stops: list[Stop] = []
    for element in elements:
        stop = map_element_to_stop(element, stop_option.type, target_point)
        if stop is None:
            continue
        stops.append(stop)

    stops = sort_stops(stops, stop_option.sortBy)
    return stops[: stop_option.limit]


async def fetch_with_retry(
    client: httpx.AsyncClient,
    query: str,
    lives: int = 3,
) -> dict | None:
    for attempt in range(lives):
        url = OVERPASS_URLS[attempt % len(OVERPASS_URLS)]
        try:
            response = await client.get(
                url=url,
                params={"data": query},
                headers={
                    "Accept": "application/json",
                    "User-Agent": "stop-back/1.0",
                },
            )

            print("FINAL URL:", response.request.url)
            print("STATUS:", response.status_code)
            print("TEXT:", response.text[:500])

            #Too many request, wyskakuje czasem jak mamy w query wiecej niz jedno miejsce
            #ale podaje tez po jakim czasie sprobowac ponownie
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                wait_time = int(retry_after) if retry_after and retry_after.isdigit() else 2 + attempt
                await asyncio.sleep(wait_time + random.random())
                continue

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as exc:
            if exc.response.status_code >= 500 and attempt < lives - 1:
                await asyncio.sleep(2 + attempt + random.random())
                continue
            raise

        except httpx.RequestError:
            if attempt < lives - 1:
                await asyncio.sleep(2 + attempt + random.random())
                continue
            raise

    return None


#Funkcje pomocnicze, typowe dla overpassa
def build_overpass_query(
    point: Location,
    osm_key: str,
    osm_value: str,
    radius_m: int,
) -> str:
    return f"""
[out:json][timeout:50];
(
  node["{osm_key}"="{osm_value}"](around:{radius_m},{point.lat},{point.lng});
  way["{osm_key}"="{osm_value}"](around:{radius_m},{point.lat},{point.lng});
);
out center tags;
""".strip()


# Wynik overpassa -> nasz Stop
# openingHours i rating na razie None
def map_element_to_stop(
    element: dict,
    stop_type: StopType,
    target_point: Location,
) -> Stop | None:
    coords = extract_coords(element)
    if coords is None:
        return None

    lat, lng = coords
    tags = element.get("tags", {}) or {}

    location = Location(lat=lat, lng=lng)
    detour_distance = estimate_distance_to_point(location, target_point)

    return Stop(
        ident=StopIdent(
            id=f"{element.get('type', 'unknown')}-{element.get('id', 'unknown')}",
            type=stop_type,
            name=tags.get("name", "Unnamed place"),
            location=location,
            address=build_address(tags),
        ),
        detourDistance=detour_distance,
        detourTime=int(detour_distance * DETOUR_TIME_MULTIPLIER),
        website=tags.get("website"),
        openingHours=None,
        rating=None,
    )


# Overpass thing - przy pytaniu o way może zwrócić liste punktow, wyciągamy wtedy środek z center
def extract_coords(element: dict) -> tuple[float, float] | None:
    if "lat" in element and "lon" in element:
        return float(element["lat"]), float(element["lon"])

    center = element.get("center")
    if isinstance(center, dict) and "lat" in center and "lon" in center:
        return float(center["lat"]), float(center["lon"])

    return None


# adres Overpassa -> nasz adres
def build_address(tags: dict) -> str:
    street = tags.get("addr:street")
    house_number = tags.get("addr:housenumber")
    city = tags.get("addr:city")
    postcode = tags.get("addr:postcode")

    first_line = " ".join(part for part in [street, house_number] if part)
    second_line = " ".join(part for part in [postcode, city] if part)

    address = ", ".join(part for part in [first_line, second_line] if part)
    return address or "Address unavailable"
