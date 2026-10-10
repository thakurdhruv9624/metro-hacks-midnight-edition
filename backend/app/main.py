from contextlib import asynccontextmanager
from pathlib import Path
import subprocess
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dashboard import router as dashboard_router
from app.api.forecast import router as forecast_router
from app.api.group import router as group_router
from app.api.rider import router as rider_router
from app.config import get_settings
from app.services.catalog import drop_zones, stations
from app.services.model_store import get_forecast_model


def _ensure_data() -> None:
    settings = get_settings()
    if settings.ridership_path.exists():
        return
    script = Path(__file__).resolve().parents[1] / "scripts" / "generate_synthetic.py"
    subprocess.run([sys.executable, str(script), "--days", "14"], check=True)


@asynccontextmanager
async def lifespan(_: FastAPI):
    _ensure_data()
    get_forecast_model()
    yield


app = FastAPI(title="MetroSync", version="0.1.0", lifespan=lifespan)
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(forecast_router)
app.include_router(group_router)
app.include_router(rider_router)
app.include_router(dashboard_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/stations")
def list_stations() -> dict:
    return {
        "stations": [item.model_dump() for item in stations()],
        "drop_zones": [item.model_dump() for item in drop_zones()],
    }
