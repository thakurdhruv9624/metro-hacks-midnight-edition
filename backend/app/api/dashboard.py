from datetime import datetime

import pandas as pd
from fastapi import APIRouter, HTTPException

from app.ml.forecast import feature_frame, predict
from app.models.schemas import ComparisonResponse, DashboardResponse, StationDemand, VehicleRow
from app.services.catalog import stations
from app.services.comparison import build_comparison
from app.services.model_store import get_forecast_model
from app.config import get_settings

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard() -> DashboardResponse:
    settings = get_settings()
    try:
        model = get_forecast_model(settings)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    catalog_stations = stations(settings)
    ids = [item.id for item in catalog_stations]
    names = {item.id: item.name for item in catalog_stations}
    pred = predict(model, feature_frame(ids, datetime.utcnow(), 60))
    demand_map = {
        sid: float(group["predicted_exits"].sum()) for sid, group in pred.groupby("station_id")
    }
    max_demand = max(demand_map.values()) if demand_map else 1.0

    vehicles_df = pd.read_csv(settings.vehicles_path) if settings.vehicles_path.exists() else pd.DataFrame()
    vehicle_rows: list[VehicleRow] = []
    occupancy_by_station: dict[str, list[float]] = {sid: [] for sid in ids}

    if not vehicles_df.empty:
        now_hour = datetime.utcnow().hour
        peak = 1.0 if now_hour in {8, 9, 17, 18, 19} else 0.55
        for _, row in vehicles_df.iterrows():
            cap = int(row["capacity"])
            occ = min(cap, max(0, int(round(cap * peak * float(row["supply_score"])))))
            occupancy_by_station.setdefault(row["station_id"], []).append(occ / cap)
            vehicle_rows.append(
                VehicleRow(
                    vehicle_id=row["vehicle_id"],
                    vehicle_type=row["vehicle_type"],
                    station_id=row["station_id"],
                    occupancy=occ,
                    capacity=cap,
                    status="loading" if occ > 0 else "ready",
                )
            )

    station_rows: list[StationDemand] = []
    waits: list[float] = []
    occs: list[float] = []
    for station in catalog_stations:
        demand = demand_map.get(station.id, 0.0)
        fleet = [v for v in vehicle_rows if v.station_id == station.id]
        occ = (
            sum(v.occupancy / v.capacity for v in fleet) / len(fleet) * 100 if fleet else 0.0
        )
        wait = round(3.5 + (demand / 40.0) * (1.4 - occ / 100), 1)
        waits.append(wait)
        occs.append(occ)
        station_rows.append(
            StationDemand(
                station_id=station.id,
                station_name=names[station.id],
                predicted_exits=round(demand, 1),
                vehicles_available=len(fleet),
                occupancy_pct=round(occ, 1),
                avg_wait_minutes=wait,
                heat=round(demand / max_demand, 3),
            )
        )

    return DashboardResponse(
        generated_at=datetime.utcnow(),
        stations=station_rows,
        vehicles=vehicle_rows[:24],
        city_avg_wait=round(sum(waits) / len(waits), 1) if waits else 0.0,
        city_occupancy=round(sum(occs) / len(occs), 1) if occs else 0.0,
    )


@router.get("/comparison", response_model=ComparisonResponse)
def get_comparison() -> ComparisonResponse:
    try:
        return build_comparison()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
