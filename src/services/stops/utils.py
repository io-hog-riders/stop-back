from concurrent.futures import ThreadPoolExecutor

from db.models.common import Location, Rating, OpeningTimes, OpeningHours
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


def estimate_distance_to_route(start_perc: int, points: list[Location], coords: tuple[float, float]) -> int:
    start_index =  int((len(points)-1) * start_perc/100)
    distance_from_start = haversine_m(coords[0], coords[1], points[start_index].lat, points[start_index].lng)

    with ThreadPoolExecutor() as executor:
        future1 = executor.submit(find_minimum_distance_from_one_direction, 1, points, start_index, coords)
        future2 = executor.submit(find_minimum_distance_from_one_direction, -1, points, start_index, coords)

        result = min(future1.result(), future2.result(), distance_from_start)
    return result

def find_minimum_distance_from_one_direction(direction: int, points: list[Location], start_index: int, coords: tuple[float, float] ) -> int:
    prev = current = float("inf")
    if direction == 1:
        indices = range(start_index, len(points))
    else:
        indices = range(start_index, -1, -1)
    for i in indices:
        current = haversine_m(coords[0], coords[1], points[i].lat, points[i].lng)
        if current < prev:
            prev = current
        else:
            return int(prev)
    return int(current)


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

#Parsery OpeningHours i Rating

DAY_MAP = {
    "Mo": "monday",
    "Tu": "tuesday",
    "We": "wednesday",
    "Th": "thursday",
    "Fr": "friday",
    "Sa": "saturday",
    "Su": "sunday",
}

def parse_rating(tags: dict) -> Rating | None:
    value = tags.get("rating") or tags.get("stars")
    if value is None:
        return None
    try:
        rate = int(round(float(value)))
    except ValueError:
        return None

    rate = max(0, min(rate, 5))
    return Rating(rate=rate)

#Te formaty potrafia byc dziwne, wiec jak nie umiemy sparsowac to jest None
def parse_opening_hours(tags: dict) -> OpeningTimes | None:
    value = tags.get("opening_hours")

    if not value:
        return None

    if value == "24/7":
        full_day = OpeningHours(opens="00:00", closes="23:59")
        return OpeningTimes(
            monday=full_day,
            tuesday=full_day,
            wednesday=full_day,
            thursday=full_day,
            friday=full_day,
            saturday=full_day,
            sunday=full_day,
        )

    result = {}

    for rule in value.split(";"):
        rule = rule.strip()
        parts = rule.split()

        if len(parts) < 2:
            continue

        days_part = parts[0]
        hours_part = parts[1]

        if "," in hours_part:
            hours_part = hours_part.split(",")[0]

        if "-" not in hours_part:
            continue

        opens, closes = hours_part.split("-", 1)

        for day in expand_days(days_part):
            if day not in DAY_MAP:
                continue
            result[DAY_MAP[day]] = OpeningHours(opens=opens, closes=closes)
    return OpeningTimes(**result) if result else None


def expand_days(days_part: str) -> list[str]:
    days = list(DAY_MAP.keys())

    if days_part == "PH":
        return []

    if "-" in days_part:
        start, end = days_part.split("-", 1)

        if start not in days or end not in days:
            return []

        start_idx = days.index(start)
        end_idx = days.index(end)

        if start_idx <= end_idx:
            return days[start_idx:end_idx + 1]

        return days[start_idx:] + days[:end_idx + 1]

    if "," in days_part:
        return [day for day in days_part.split(",") if day in DAY_MAP]

    if days_part not in DAY_MAP:
        return []

    return [days_part]