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
from db.models.common import Person
from services.stops.utils import sort_stops, deduplicate_elements, \
    find_route_point_at_percent, estimate_distance_to_route, parse_rating, parse_opening_hours

#Podejscie oparte na szukaniu tylko w obrębie jednego punktu na trasie

#przy każdej próbie próbujemy innego serwera
OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
#póki co nasz detour time to sztywno detour_distance/900
DETOUR_TIME_MULTIPLIER = 1/8 # <- 1/900 to ok. 3240 kmh XDDDDD

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

RESTAURANT_PERSONALIZATION = {
    Person.family: ("kids_area", "yes"),
    Person.students: ("bar", "yes"),
    Person.disabled: ("wheelchair", "yes"),
    Person.driver: ("bar", "no") #zeby ich nie kusilo xd
}

async def find_stops_along_route(route: Route, stops_config: StopsConfig, person: Person) -> list[Stop]:
    all_stops: list[Stop] = []

    #szukamy po kolei dla każdego wybranego rodzaju stopu
    #dzieki temu mniejsze zapytanie + wywalenie jednego nie psuje całości
    for stop_option in stops_config.stops:
        try:
            stops_for_type = await find_stops_for_option(route, stop_option, person)
        except httpx.HTTPError as exc:
            print("Not found for:", stop_option)
            print("HTTP ERROR TYPE:", type(exc).__name__)
            print("HTTP ERROR:", exc)

            if isinstance(exc, httpx.HTTPStatusError):
                print("STATUS CODE:", exc.response.status_code)
            stops_for_type = []
        all_stops.extend(stops_for_type)

    return all_stops

#Odpytujemy Overpassa o dane miejsce
async def find_stops_for_option(route: Route, stop_option: StopOptions, person: Person) -> list[Stop]:
    osm_key, osm_value = STOP_TYPE_TO_OSM[stop_option.type]
    osm_keys = [osm_key]
    osm_values = [osm_value]

    print("PERSON:", person)
    if person is not None and stop_option.type == StopType.restaurant:
        person_key, person_value = RESTAURANT_PERSONALIZATION[person]
        osm_keys.append(person_key)
        osm_values.append(person_value)
    #punkt w okół którego bedziemy szukać
    target_point = find_route_point_at_percent(route.points, stop_option.targetPercent)

    query = build_overpass_query(
        point=target_point,
        osm_keys=osm_keys,
        osm_values=osm_values,
        radius_m=stop_option.maxDetour,
    )

    print("OVERPASS QUERY:")
    print(query)
    async with httpx.AsyncClient(timeout=50.0) as client:
        data = await fetch_with_retry(client, query)
    if not data:
        return []
    elements = deduplicate_elements(data.get("elements", []))
    print("ELEMENTS COUNT:", len(elements))


    stops: list[Stop] = []
    for element in elements:
        coords = extract_coords(element)
        if coords is None:
            continue
        detour_distance = estimate_distance_to_route(stop_option.targetPercent, route.points, coords)
        stop = map_element_to_stop(element, stop_option.type, detour_distance)
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
    osm_keys: list[str],
    osm_values: list[str],
    radius_m: int,
) -> str:
    pairs = "".join(
        f'["{key}"="{value}"]'
        for key, value in zip(osm_keys, osm_values)
    )


    return f"""
[out:json][timeout:50];
(
  node{pairs}(around:{radius_m},{point.lat},{point.lng});
  way{pairs}(around:{radius_m},{point.lat},{point.lng});
);
out center tags;
""".strip()


# Wynik overpassa -> nasz Stop
# openingHours i rating na razie None
def map_element_to_stop(
    element: dict,
    stop_type: StopType,
    detour_distance: int,

) -> Stop | None:
    coords = extract_coords(element)
    if coords is None:
        return None

    lat, lng = coords
    tags = element.get("tags", {}) or {}

    location = Location(lat=lat, lng=lng)

    return Stop(
        ident=StopIdent(
            id=f"{element.get('type', 'unknown')}-{element.get('id', 'unknown')}",
            type=stop_type,
            name=tags.get("name", "Unnamed place"),
            location=location,
            address=build_address(tags),
        ),
        detourDistance=detour_distance,
        detourTime=max(int(detour_distance * DETOUR_TIME_MULTIPLIER),1),
        website=tags.get("website"),
        openingHours=parse_opening_hours(tags),
        rating=parse_rating(tags),
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
