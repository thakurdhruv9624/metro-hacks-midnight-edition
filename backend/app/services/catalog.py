from __future__ import annotations

import json
from functools import lru_cache

from app.config import Settings, get_settings
from app.models.schemas import DropZone, Station


@lru_cache
def _raw(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def catalog(settings: Settings | None = None) -> dict:
    settings = settings or get_settings()
    return _raw(str(settings.stations_path))


def stations(settings: Settings | None = None) -> list[Station]:
    return [Station(**row) for row in catalog(settings)["stations"]]


def drop_zones(settings: Settings | None = None) -> list[DropZone]:
    return [DropZone(**row) for row in catalog(settings)["drop_zones"]]


def station_by_id(station_id: str, settings: Settings | None = None) -> Station:
    found = next((item for item in stations(settings) if item.id == station_id), None)
    if not found:
        raise KeyError(station_id)
    return found
