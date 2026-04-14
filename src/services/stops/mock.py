from db.models.stops import StopType

def get_stop_types() -> list[StopType]:
    return [
        StopType.restaurant,
        StopType.gas_station,
        StopType.hotel,
        StopType.hospital,
        StopType.parking,
        StopType.attraction,
        StopType.rest_area,
        StopType.charging_station,
    ]
