from db.models.plan import Route
from db.models.stops import StopsConfig, Stop


async def find_stops_along_route(route: Route, stops_config: StopsConfig) -> list[Stop]:
    #TODO
    return []