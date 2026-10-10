from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Station(BaseModel):
    id: str
    name: str
    line: str
    lat: float
    lng: float
    bays: int
    zone: str


class DropZone(BaseModel):
    id: str
    name: str
    lat: float
    lng: float
    aliases: list[str] = Field(default_factory=list)


class ForecastPoint(BaseModel):
    station_id: str
    station_name: str
    timestamp: datetime
    predicted_exits: float
    confidence_low: float
    confidence_high: float


class ForecastResponse(BaseModel):
    generated_at: datetime
    horizon_minutes: int
    points: list[ForecastPoint]


class RiderRequest(BaseModel):
    station_id: str
    drop_text: str
    party_size: int = 1
    tap_in_at: datetime | None = None


class ParsedDrop(BaseModel):
    zone_id: str
    zone_name: str
    lat: float
    lng: float
    confidence: float
    source: Literal["ollama", "rules"]


class PickupAssignment(BaseModel):
    bay: int
    slot_start: datetime
    slot_end: datetime
    vehicle_id: str
    vehicle_type: Literal["e-auto", "feeder-bus"]
    group_id: str
    group_size: int
    fare_inr: int
    walk_minutes: int
    eta_minutes: int


class Trip(BaseModel):
    id: str
    station_id: str
    station_name: str
    drop: ParsedDrop
    assignment: PickupAssignment
    summary: str
    status: Literal["assigned", "boarding", "complete"]
    created_at: datetime
    door_to_door_minutes: int
    wait_minutes: int


class GroupRider(BaseModel):
    rider_id: str
    station_id: str
    drop_lat: float
    drop_lng: float
    ready_at: datetime
    party_size: int = 1


class GroupRequest(BaseModel):
    riders: list[GroupRider]
    station_id: str | None = None


class GroupCluster(BaseModel):
    group_id: str
    vehicle_type: Literal["e-auto", "feeder-bus"]
    centroid_lat: float
    centroid_lng: float
    rider_ids: list[str]
    bay: int
    slot_start: datetime
    occupancy: int


class GroupResponse(BaseModel):
    clusters: list[GroupCluster]
    ungrouped: list[str]


class StationDemand(BaseModel):
    station_id: str
    station_name: str
    predicted_exits: float
    vehicles_available: int
    occupancy_pct: float
    avg_wait_minutes: float
    heat: float


class VehicleRow(BaseModel):
    vehicle_id: str
    vehicle_type: Literal["e-auto", "feeder-bus"]
    station_id: str
    occupancy: int
    capacity: int
    status: str


class DashboardResponse(BaseModel):
    generated_at: datetime
    stations: list[StationDemand]
    vehicles: list[VehicleRow]
    city_avg_wait: float
    city_occupancy: float


class MetricPair(BaseModel):
    label: str
    unit: str
    baseline: float
    metrosync: float
    delta_pct: float


class ComparisonResponse(BaseModel):
    generated_at: datetime
    metrics: list[MetricPair]
    narrative: str
