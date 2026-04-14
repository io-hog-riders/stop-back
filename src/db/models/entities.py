from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str | None] = mapped_column(String, nullable=True)
    vehicle_type: Mapped[str | None] = mapped_column(String, nullable=True)
    total_distance_km: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, server_default="0")
    total_routes_completed: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    routes: Mapped[list[Route]] = relationship(back_populates="user", cascade="all, delete-orphan")
    reviews: Mapped[list[Review]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    start_point_lat: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    start_point_lng: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    end_point_lat: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    end_point_lng: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    distance_km: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    status: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    user: Mapped[User] = relationship(back_populates="routes")
    stops: Mapped[list[RouteStop]] = relationship(back_populates="route", cascade="all, delete-orphan")


class Place(Base):
    __tablename__ = "places"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    latitude: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    address: Mapped[str | None] = mapped_column(String, nullable=True)
    average_rating: Mapped[Decimal | None] = mapped_column(Numeric(3, 2), nullable=True)
    reviews_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    amenities: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    route_stops: Mapped[list[RouteStop]] = relationship(back_populates="place", cascade="all, delete-orphan")
    reviews: Mapped[list[Review]] = relationship(back_populates="place", cascade="all, delete-orphan")


class RouteStop(Base):
    __tablename__ = "route_stops"
    __table_args__ = (UniqueConstraint("route_id", "stop_order", name="uq_route_stops_route_order"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    route_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("routes.id", ondelete="CASCADE"), nullable=False)
    place_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("places.id", ondelete="CASCADE"), nullable=False)
    stop_order: Mapped[int] = mapped_column(Integer, nullable=False)
    planned_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    route: Mapped[Route] = relationship(back_populates="stops")
    place: Mapped[Place] = relationship(back_populates="route_stops")


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (CheckConstraint("rating BETWEEN 1 AND 5", name="ck_reviews_rating_1_5"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    place_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("places.id", ondelete="CASCADE"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    user: Mapped[User] = relationship(back_populates="reviews")
    place: Mapped[Place] = relationship(back_populates="reviews")