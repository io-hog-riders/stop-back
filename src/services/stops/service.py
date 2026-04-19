from dotenv import load_dotenv
import os

from db.models.plan import Route
from db.models.stops import StopsConfig, Stop
from services.stops.overpass_service import find_stops_along_route as overpass_service
from services.stops.google_service import find_stops_along_route as google_service

load_dotenv()

api = os.environ.get("API", "Overpass")

async def get_stops_along_route(route: Route, stops_config: StopsConfig) -> list[Stop]:
    if api == "Overpass":
        return await overpass_service(route, stops_config)
    elif api == "Google":
        return await google_service(route, stops_config)
    return []