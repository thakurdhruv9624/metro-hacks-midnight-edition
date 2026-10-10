from datetime import datetime, timedelta

from app.ml.grouping import cluster_riders
from app.models.schemas import GroupRider


def _rider(i: int, lat: float, lng: float, minutes: int = 0) -> GroupRider:
    return GroupRider(
        rider_id=f"r{i}",
        station_id="infocity",
        drop_lat=lat,
        drop_lng=lng,
        ready_at=datetime(2026, 10, 1, 9, 0) + timedelta(minutes=minutes),
        party_size=1,
    )


def test_nearby_drops_form_a_group() -> None:
    riders = [
        _rider(1, 23.1988, 72.6372),
        _rider(2, 23.1989, 72.6373, 2),
        _rider(3, 23.1990, 72.6371, 1),
        _rider(4, 23.2335, 72.6568, 3),
    ]
    clusters, ungrouped = cluster_riders(riders, eps_km=0.7, min_samples=2)
    sizes = [len(c.rider_ids) for c in clusters]
    assert max(sizes) >= 3
    assert "r4" in ungrouped or any("r4" in c.rider_ids and len(c.rider_ids) == 1 for c in clusters)


def test_empty_input() -> None:
    clusters, ungrouped = cluster_riders([])
    assert clusters == []
    assert ungrouped == []
