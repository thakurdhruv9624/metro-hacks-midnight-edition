from __future__ import annotations

from app.models.schemas import Trip

_TRIPS: dict[str, Trip] = {}


def save(trip: Trip) -> Trip:
    _TRIPS[trip.id] = trip
    return trip


def get(trip_id: str) -> Trip | None:
    return _TRIPS.get(trip_id)
