"""Generate peak-aware ridership, trips, and feeder supply for Gandhinagar."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "backend") not in sys.path:
    sys.path.insert(0, str(ROOT / "backend"))

from app.config import get_settings  # noqa: E402


STATION_BASE = {
    "gift": 42,
    "infocity": 55,
    "kudasan": 28,
    "raysan": 18,
    "gnlu": 16,
    "sec16": 24,
    "sec10": 31,
    "pathikashram": 36,
}

PEAK_AM = {8, 9}
PEAK_PM = {17, 18, 19}


def load_catalog(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def hourly_multiplier(hour: int, weekday: int, zone: str) -> float:
    """Office stations swell on weekday peaks; campus stays flatter."""
    is_weekend = weekday >= 5
    if hour in PEAK_AM:
        peak = 2.8 if zone == "office" else 1.9
    elif hour in PEAK_PM:
        peak = 3.1 if zone == "office" else 2.2
    elif 11 <= hour <= 14:
        peak = 1.2
    elif 21 <= hour or hour <= 5:
        peak = 0.18
    else:
        peak = 0.7
    if is_weekend:
        peak *= 0.55 if zone == "office" else 0.85
    return peak


def generate_ridership(stations: list[dict], days: int, start: datetime, rng: np.random.Generator) -> pd.DataFrame:
    rows: list[dict] = []
    for day in range(days):
        stamp = start + timedelta(days=day)
        for hour in range(24):
            ts = stamp.replace(hour=hour, minute=0, second=0)
            for station in stations:
                base = STATION_BASE[station["id"]]
                mult = hourly_multiplier(hour, ts.weekday(), station["zone"])
                rain = 1 if rng.random() < 0.08 else 0
                rain_boost = 1.15 if rain else 1.0
                exits = max(0, rng.normal(base * mult * rain_boost, 4.5))
                entries = max(0, rng.normal(base * mult * 0.92, 4.0))
                rows.append(
                    {
                        "timestamp": ts,
                        "station_id": station["id"],
                        "hour": hour,
                        "weekday": ts.weekday(),
                        "is_weekend": int(ts.weekday() >= 5),
                        "is_peak_am": int(hour in PEAK_AM),
                        "is_peak_pm": int(hour in PEAK_PM),
                        "rain": rain,
                        "exits": int(round(exits)),
                        "entries": int(round(entries)),
                    }
                )
    return pd.DataFrame(rows)


def generate_trips(
    stations: list[dict],
    zones: list[dict],
    days: int,
    start: datetime,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Sample last-mile trips that follow the same peak shape as ridership."""
    station_by_id = {s["id"]: s for s in stations}
    rows: list[dict] = []
    rider = 0
    for day in range(days):
        stamp = start + timedelta(days=day)
        for hour in (8, 9, 10, 17, 18, 19, 12, 15):
            for station in stations:
                n = int(max(2, STATION_BASE[station["id"]] * hourly_multiplier(hour, stamp.weekday(), station["zone"]) * 0.35))
                for _ in range(n):
                    zone = zones[int(rng.integers(0, len(zones)))]
                    jitter_lat = rng.normal(0, 0.0018)
                    jitter_lng = rng.normal(0, 0.0018)
                    minute = int(rng.integers(0, 60))
                    ts = stamp.replace(hour=hour, minute=minute, second=0)
                    rider += 1
                    rows.append(
                        {
                            "rider_id": f"R{rider:06d}",
                            "station_id": station["id"],
                            "station_lat": station_by_id[station["id"]]["lat"],
                            "station_lng": station_by_id[station["id"]]["lng"],
                            "drop_zone_id": zone["id"],
                            "drop_lat": zone["lat"] + jitter_lat,
                            "drop_lng": zone["lng"] + jitter_lng,
                            "ready_at": ts,
                            "party_size": int(rng.choice([1, 1, 1, 2])),
                        }
                    )
    return pd.DataFrame(rows)


def generate_vehicles(stations: list[dict], rng: np.random.Generator) -> pd.DataFrame:
    rows: list[dict] = []
    vid = 0
    for station in stations:
        autos = 6 if station["zone"] == "office" else 4
        buses = 2 if station["bays"] >= 3 else 1
        for _ in range(autos):
            vid += 1
            rows.append(
                {
                    "vehicle_id": f"EA-{vid:03d}",
                    "vehicle_type": "e-auto",
                    "station_id": station["id"],
                    "capacity": 3,
                    "supply_score": float(rng.uniform(0.7, 1.0)),
                }
            )
        for _ in range(buses):
            vid += 1
            rows.append(
                {
                    "vehicle_id": f"FB-{vid:03d}",
                    "vehicle_type": "feeder-bus",
                    "station_id": station["id"],
                    "capacity": 12,
                    "supply_score": float(rng.uniform(0.6, 0.95)),
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Write synthetic MetroSync datasets.")
    parser.add_argument("--days", type=int, default=21)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    settings = get_settings()
    catalog = load_catalog(settings.stations_path)
    rng = np.random.default_rng(args.seed)
    start = datetime(2026, 9, 20, 0, 0, 0)

    raw_dir = settings.data_dir / "raw"
    processed = settings.data_dir / "processed"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed.mkdir(parents=True, exist_ok=True)

    ridership = generate_ridership(catalog["stations"], args.days, start, rng)
    trips = generate_trips(catalog["stations"], catalog["drop_zones"], args.days, start, rng)
    vehicles = generate_vehicles(catalog["stations"], rng)

    ridership.to_csv(settings.ridership_path, index=False)
    trips.to_csv(settings.trips_path, index=False)
    vehicles.to_csv(settings.vehicles_path, index=False)
    ridership.to_parquet(processed / "ridership.parquet", index=False)
    trips.to_parquet(processed / "trips.parquet", index=False)

    print(f"ridership rows: {len(ridership)}")
    print(f"trip rows: {len(trips)}")
    print(f"vehicles: {len(vehicles)}")
    print(f"wrote {raw_dir}")


if __name__ == "__main__":
    main()
