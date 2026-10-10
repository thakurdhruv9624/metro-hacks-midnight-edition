from datetime import datetime

import pandas as pd

from app.ml.forecast import build_pipeline, feature_frame, predict, train


def _toy_ridership() -> pd.DataFrame:
    rows = []
    for day in range(5):
        for hour in range(24):
            for station in ("gift", "infocity"):
                peak = 40 if hour in {8, 9, 18} else 10
                rows.append(
                    {
                        "timestamp": datetime(2026, 9, 21 + day, hour),
                        "station_id": station,
                        "hour": hour,
                        "weekday": day,
                        "is_weekend": int(day >= 5),
                        "is_peak_am": int(hour in {8, 9}),
                        "is_peak_pm": int(hour in {17, 18, 19}),
                        "rain": 0,
                        "exits": peak + (5 if station == "infocity" else 0),
                    }
                )
    return pd.DataFrame(rows)


def test_train_predicts_non_negative() -> None:
    model = train(_toy_ridership())
    frame = feature_frame(["gift", "infocity"], datetime(2026, 10, 1, 9), 60)
    out = predict(model, frame)
    assert (out["predicted_exits"] >= 0).all()
    assert len(out) == 2


def test_pipeline_has_gradient_boosting() -> None:
    pipe = build_pipeline()
    assert pipe.named_steps["gb"].__class__.__name__ == "GradientBoostingRegressor"
