from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from app.ml.forecast import feature_frame, predict
from app.models.schemas import ForecastPoint, ForecastResponse
from app.services.catalog import station_by_id, stations
from app.services.model_store import get_forecast_model

router = APIRouter()


@router.get("/forecast", response_model=ForecastResponse)
def get_forecast(
    station: str | None = Query(default=None),
    horizon: int = Query(default=60, ge=30, le=180),
) -> ForecastResponse:
    try:
        model = get_forecast_model()
        catalog_stations = stations()
        if station:
            catalog_stations = [station_by_id(station)]
        ids = [item.id for item in catalog_stations]
        names = {item.id: item.name for item in catalog_stations}
        frame = feature_frame(ids, datetime.utcnow(), horizon)
        pred = predict(model, frame)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown station {exc}") from exc

    points = [
        ForecastPoint(
            station_id=row["station_id"],
            station_name=names[row["station_id"]],
            timestamp=row["timestamp"].to_pydatetime(),
            predicted_exits=round(float(row["predicted_exits"]), 1),
            confidence_low=round(float(row["confidence_low"]), 1),
            confidence_high=round(float(row["confidence_high"]), 1),
        )
        for _, row in pred.iterrows()
    ]
    return ForecastResponse(generated_at=datetime.utcnow(), horizon_minutes=horizon, points=points)
