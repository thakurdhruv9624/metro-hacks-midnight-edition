"""Cluster riders by drop location and readiness time."""

from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
from sklearn.cluster import DBSCAN, KMeans

from app.models.schemas import GroupCluster, GroupRider


DEG_PER_KM = 1 / 111.32
TIME_SCALE = 0.004  # 1 minute ~ this many "degrees" so time is a light feature


def _features(riders: list[GroupRider]) -> np.ndarray:
    rows = []
    base = riders[0].ready_at
    for rider in riders:
        minutes = (rider.ready_at - base).total_seconds() / 60.0
        rows.append([rider.drop_lat, rider.drop_lng, minutes * TIME_SCALE])
    return np.array(rows, dtype=float)


def _vehicle_type(size: int) -> str:
    return "feeder-bus" if size >= 6 else "e-auto"


def _slot(ready_times: list[datetime], index: int) -> tuple[datetime, datetime]:
    latest = max(ready_times)
    start = latest.replace(second=0, microsecond=0) + timedelta(minutes=2 + index)
    return start, start + timedelta(minutes=8)


def cluster_riders(
    riders: list[GroupRider],
    eps_km: float = 0.7,
    min_samples: int = 2,
    bays: int = 3,
) -> tuple[list[GroupCluster], list[str]]:
    """Group nearby drop-offs. Singletons stay ungrouped unless KMeans can fold them."""
    if not riders:
        return [], []

    if len(riders) == 1:
        return [], [riders[0].rider_id]

    features = _features(riders)
    eps = eps_km * DEG_PER_KM
    labels = DBSCAN(eps=eps, min_samples=min_samples).fit_predict(features)

    unique = {label for label in labels if label >= 0}
    if len(unique) == 0 and len(riders) >= 3:
        k = min(3, max(1, len(riders) // 3))
        labels = KMeans(n_clusters=k, n_init=10, random_state=42).fit_predict(features)
        unique = set(labels.tolist())

    clusters: list[GroupCluster] = []
    ungrouped: list[str] = []
    cluster_index = 0

    for label in sorted(set(labels.tolist())):
        members = [riders[i] for i, lab in enumerate(labels) if lab == label]
        if label < 0 or len(members) < min_samples:
            ungrouped.extend(rider.rider_id for rider in members)
            continue
        lats = [m.drop_lat for m in members]
        lngs = [m.drop_lng for m in members]
        times = [m.ready_at for m in members]
        occupancy = sum(m.party_size for m in members)
        slot_start, _slot_end = _slot(times, cluster_index)
        clusters.append(
            GroupCluster(
                group_id=f"G{cluster_index + 1:03d}",
                vehicle_type=_vehicle_type(occupancy),
                centroid_lat=float(np.mean(lats)),
                centroid_lng=float(np.mean(lngs)),
                rider_ids=[m.rider_id for m in members],
                bay=(cluster_index % max(1, bays)) + 1,
                slot_start=slot_start,
                occupancy=occupancy,
            )
        )
        cluster_index += 1

    return clusters, ungrouped
