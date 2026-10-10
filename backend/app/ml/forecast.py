"""Gradient boosting demand forecaster for station exits."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

FEATURE_COLS = ["hour", "weekday", "is_weekend", "is_peak_am", "is_peak_pm", "rain", "station_id"]


@dataclass
class ForecastModel:
    pipeline: Pipeline
    trained_at: datetime


def build_pipeline() -> Pipeline:
    encode = ColumnTransformer(
        transformers=[
            ("station", OneHotEncoder(handle_unknown="ignore"), ["station_id"]),
            ("numeric", "passthrough", ["hour", "weekday", "is_weekend", "is_peak_am", "is_peak_pm", "rain"]),
        ]
    )
    model = GradientBoostingRegressor(
        n_estimators=120,
        learning_rate=0.08,
        max_depth=3,
        random_state=42,
    )
    return Pipeline([("prep", encode), ("gb", model)])


def load_ridership(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["timestamp"])
    if df.empty:
        raise ValueError("Ridership file is empty.")
    return df


def train(df: pd.DataFrame) -> ForecastModel:
    pipeline = build_pipeline()
    x = df[FEATURE_COLS]
    y = df["exits"].astype(float)
    pipeline.fit(x, y)
    return ForecastModel(pipeline=pipeline, trained_at=datetime.utcnow())


def save_model(model: ForecastModel, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)


def load_model(path: Path) -> ForecastModel:
    return joblib.load(path)


def feature_frame(station_ids: list[str], start: datetime, horizon_minutes: int, rain: int = 0) -> pd.DataFrame:
    steps = max(1, horizon_minutes // 60)
    rows: list[dict] = []
    for station_id in station_ids:
        for i in range(steps):
            ts = start.replace(minute=0, second=0, microsecond=0) + timedelta(hours=i)
            hour = ts.hour
            rows.append(
                {
                    "timestamp": ts,
                    "station_id": station_id,
                    "hour": hour,
                    "weekday": ts.weekday(),
                    "is_weekend": int(ts.weekday() >= 5),
                    "is_peak_am": int(hour in {8, 9}),
                    "is_peak_pm": int(hour in {17, 18, 19}),
                    "rain": rain,
                }
            )
    return pd.DataFrame(rows)


def predict(model: ForecastModel, frame: pd.DataFrame) -> pd.DataFrame:
    preds = model.pipeline.predict(frame[FEATURE_COLS])
    out = frame.copy()
    out["predicted_exits"] = np.clip(preds, 0, None)
    residual = 0.18
    out["confidence_low"] = np.clip(out["predicted_exits"] * (1 - residual), 0, None)
    out["confidence_high"] = out["predicted_exits"] * (1 + residual)
    return out
