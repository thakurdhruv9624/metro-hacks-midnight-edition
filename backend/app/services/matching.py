from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

import pandas as pd

from app.config import Settings, get_settings
from app.ml.grouping import cluster_riders
from app.ml.ollama_client import parse_drop, write_summary
from app.models.schemas import GroupRider, PickupAssignment, Trip
from app.services.catalog import drop_zones, station_by_id


def _fare(vehicle_type: str, occupancy: int) -> int:
    base = 28 if vehicle_type == "e-auto" else 18
    share = max(1, occupancy)
    return max(12, int(round(base * (1.4 / share) + 8)))


def _peer_riders(station_id: str, drop_lat: float, drop_lng: float, ready_at: datetime, settings: Settings) -> list[GroupRider]:
    path = settings.trips_path
    peers: list[GroupRider] = [
        GroupRider(
            rider_id="self",
            station_id=station_id,
            drop_lat=drop_lat,
            drop_lng=drop_lng,
            ready_at=ready_at,
            party_size=1,
        )
    ]
    if not path.exists():
        return peers
    trips = pd.read_csv(path, parse_dates=["ready_at"])
    window_start = ready_at - timedelta(minutes=12)
    window_end = ready_at + timedelta(minutes=12)
    sample = trips[
        (trips["station_id"] == station_id)
        & (trips["ready_at"] >= window_start)
        & (trips["ready_at"] <= window_end)
    ].head(18)
    for _, row in sample.iterrows():
        peers.append(
            GroupRider(
                rider_id=str(row["rider_id"]),
                station_id=station_id,
                drop_lat=float(row["drop_lat"]),
                drop_lng=float(row["drop_lng"]),
                ready_at=row["ready_at"].to_pydatetime(),
                party_size=int(row["party_size"]),
            )
        )
    return peers


def build_trip(station_id: str, drop_text: str, party_size: int, tap_in_at: datetime | None) -> Trip:
    settings = get_settings()
    station = station_by_id(station_id, settings)
    ready_at = tap_in_at or datetime.utcnow()
    parsed = parse_drop(drop_text, drop_zones(settings), settings)
    peers = _peer_riders(station_id, parsed.lat, parsed.lng, ready_at, settings)
    clusters, ungrouped = cluster_riders(peers, bays=station.bays)
    chosen = next((c for c in clusters if "self" in c.rider_ids), None)
    if chosen is None:
        slot_start = ready_at.replace(second=0, microsecond=0) + timedelta(minutes=4)
        assignment = PickupAssignment(
            bay=1,
            slot_start=slot_start,
            slot_end=slot_start + timedelta(minutes=8),
            vehicle_id="EA-SOLO",
            vehicle_type="e-auto",
            group_id="G-SOLO",
            group_size=party_size,
            fare_inr=_fare("e-auto", party_size),
            walk_minutes=2,
            eta_minutes=4,
        )
        occupancy = party_size
    else:
        occupancy = max(chosen.occupancy, party_size)
        assignment = PickupAssignment(
            bay=chosen.bay,
            slot_start=chosen.slot_start,
            slot_end=chosen.slot_start + timedelta(minutes=8),
            vehicle_id=f"{'FB' if chosen.vehicle_type == 'feeder-bus' else 'EA'}-{chosen.group_id[1:]}",
            vehicle_type=chosen.vehicle_type,
            group_id=chosen.group_id,
            group_size=occupancy,
            fare_inr=_fare(chosen.vehicle_type, occupancy),
            walk_minutes=2,
            eta_minutes=max(2, int((chosen.slot_start - ready_at).total_seconds() / 60)),
        )

    slot_label = assignment.slot_start.strftime("%H:%M")
    summary = write_summary(
        station.name,
        parsed.zone_name,
        assignment.bay,
        slot_label,
        assignment.vehicle_type,
        assignment.fare_inr,
        settings,
    )
    wait = assignment.eta_minutes
    door = 18 + wait + 9
    return Trip(
        id=str(uuid4())[:8],
        station_id=station.id,
        station_name=station.name,
        drop=parsed,
        assignment=assignment,
        summary=summary,
        status="assigned",
        created_at=ready_at,
        door_to_door_minutes=door,
        wait_minutes=wait,
    )
