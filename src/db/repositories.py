from __future__ import annotations

import uuid
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import Place, Route, RouteStop, User


@dataclass
class RouteStopInput:
    place_id: uuid.UUID
    stop_order: int
    planned_duration_minutes: int | None = None


def create_user(
    db: Session,
    *,
    email: str,
    password_hash: str,
    username: str | None = None,
    vehicle_type: str | None = None,
) -> User:
    user = User(
        email=email,
        password_hash=password_hash,
        username=username,
        vehicle_type=vehicle_type,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    return db.scalar(stmt)


def create_place(
    db: Session,
    *,
    name: str,
    category: str,
    latitude: Decimal,
    longitude: Decimal,
    address: str | None = None,
    amenities: dict | None = None,
) -> Place:
    place = Place(
        name=name,
        category=category,
        latitude=latitude,
        longitude=longitude,
        address=address,
        amenities=amenities,
    )
    db.add(place)
    db.commit()
    db.refresh(place)
    return place


def create_route_with_stops(
    db: Session,
    *,
    user_id: uuid.UUID,
    start_point_lat: Decimal,
    start_point_lng: Decimal,
    end_point_lat: Decimal,
    end_point_lng: Decimal,
    name: str | None = None,
    status: str | None = "planowana",
    distance_km: Decimal | None = None,
    stops: list[RouteStopInput] | None = None,
) -> Route:
    route = Route(
        user_id=user_id,
        name=name,
        start_point_lat=start_point_lat,
        start_point_lng=start_point_lng,
        end_point_lat=end_point_lat,
        end_point_lng=end_point_lng,
        status=status,
        distance_km=distance_km,
    )
    db.add(route)
    db.flush()

    for stop in stops or []:
        db.add(
            RouteStop(
                route_id=route.id,
                place_id=stop.place_id,
                stop_order=stop.stop_order,
                planned_duration_minutes=stop.planned_duration_minutes,
            )
        )

    db.commit()
    db.refresh(route)
    return route