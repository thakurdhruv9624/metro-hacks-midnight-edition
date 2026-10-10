from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    data_dir: Path = ROOT / "data"
    model_path: Path = ROOT / "data" / "processed" / "demand_model.joblib"
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "llama3.2"
    ollama_timeout_seconds: float = 6.0

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.api_cors_origins.split(",") if item.strip()]

    @property
    def stations_path(self) -> Path:
        return self.data_dir / "stations.json"

    @property
    def ridership_path(self) -> Path:
        return self.data_dir / "raw" / "ridership.csv"

    @property
    def trips_path(self) -> Path:
        return self.data_dir / "raw" / "trips.csv"

    @property
    def vehicles_path(self) -> Path:
        return self.data_dir / "raw" / "feeder_vehicles.csv"


@lru_cache
def get_settings() -> Settings:
    return Settings()
