from db.models.common import Location
from db.models.stops import Stop


def deduplicate_elements(elements: list[dict]) -> list[dict]:
    seen: set[str] = set()
    unique: list[dict] = []

    for element in elements:
        osm_id = f"{element.get('type', 'unknown')}-{element.get('id', 'unknown')}"
        if osm_id in seen:
            continue
        seen.add(osm_id)
        unique.append(element)

    return unique

def sort_stops(stops: list[Stop], sort_by) -> list[Stop]:
    if str(sort_by) == "rating":
        return sorted(
            stops,
            key=lambda stop: (
                -(stop.rating.rate if stop.rating is not None else -1),
                stop.detourDistance,
            ),
        )

    return sorted(stops, key=lambda stop: stop.detourDistance)

#naiwnie zakładamy, ze punkty na trasie są równo rozdzielone
#i szacujemy % trasy poprzez liczbe punktow
def find_route_point_at_percent(points: list[Location], percent: int) -> Location:
    if not points:
        return Location(lat=0.0, lng=0.0)

    if len(points) == 1:
        return points[0]

    normalized_percent = max(0, min(100, percent))
    index = round((normalized_percent / 100) * (len(points) - 1))
    return points[index]


# odległość od stopu do wybranego punktu (nie ogólnie trasy)
def estimate_distance_to_point(stop_location: Location, target_point: Location) -> int:
    return int(
        round(
            haversine_m(
                stop_location.lat,
                stop_location.lng,
                target_point.lat,
                target_point.lng,
            )
        )
    )

# odległość dwóch punktów na sferze
def haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    from math import atan2, cos, radians, sin, sqrt

    earth_radius_m = 6_371_000

    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return earth_radius_m * c