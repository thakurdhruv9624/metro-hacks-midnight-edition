from __future__ import annotations

from app.config import Settings, get_settings
from app.ml.forecast import ForecastModel, load_model, load_ridership, save_model, train


_model: ForecastModel | None = None


def get_forecast_model(settings: Settings | None = None) -> ForecastModel:
    global _model
    settings = settings or get_settings()
    if _model is not None:
        return _model
    if settings.model_path.exists():
        _model = load_model(settings.model_path)
        return _model
    if not settings.ridership_path.exists():
        raise FileNotFoundError("Ridership data is missing. Run generate_synthetic.py first.")
    df = load_ridership(settings.ridership_path)
    _model = train(df)
    save_model(_model, settings.model_path)
    return _model


def reset_model() -> None:
    global _model
    _model = None
