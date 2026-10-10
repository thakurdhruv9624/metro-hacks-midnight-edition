from fastapi import APIRouter, HTTPException

from app.models.schemas import RiderRequest, Trip
from app.services.matching import build_trip
from app.services.trip_store import get, save

router = APIRouter()


@router.post("/rider/trip", response_model=Trip)
def create_trip(body: RiderRequest) -> Trip:
    if not body.drop_text.strip():
        raise HTTPException(status_code=422, detail="A drop location is required.")
    try:
        trip = build_trip(body.station_id, body.drop_text, body.party_size, body.tap_in_at)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown station {exc}") from exc
    return save(trip)


@router.get("/rider/trip/{trip_id}", response_model=Trip)
def read_trip(trip_id: str) -> Trip:
    trip = get(trip_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found.")
    return trip
