from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_stations() -> None:
    response = client.get("/stations")
    assert response.status_code == 200
    body = response.json()
    assert len(body["stations"]) >= 6
    assert len(body["drop_zones"]) >= 4


def test_forecast_and_dashboard() -> None:
    forecast = client.get("/forecast", params={"station": "infocity", "horizon": 60})
    assert forecast.status_code == 200
    assert forecast.json()["points"]
    dash = client.get("/dashboard")
    assert dash.status_code == 200
    assert dash.json()["stations"]


def test_group_and_trip() -> None:
    payload = {
        "station_id": "infocity",
        "riders": [
            {
                "rider_id": "a",
                "station_id": "infocity",
                "drop_lat": 23.1988,
                "drop_lng": 72.6372,
                "ready_at": datetime(2026, 10, 1, 9, 5).isoformat(),
                "party_size": 1,
            },
            {
                "rider_id": "b",
                "station_id": "infocity",
                "drop_lat": 23.1989,
                "drop_lng": 72.6374,
                "ready_at": datetime(2026, 10, 1, 9, 6).isoformat(),
                "party_size": 1,
            },
        ],
    }
    grouped = client.post("/group", json=payload)
    assert grouped.status_code == 200
    trip = client.post(
        "/rider/trip",
        json={"station_id": "infocity", "drop_text": "Infocity offices", "party_size": 1},
    )
    assert trip.status_code == 200
    body = trip.json()
    assert body["assignment"]["bay"] >= 1
    assert body["assignment"]["fare_inr"] > 0
    fetched = client.get(f"/rider/trip/{body['id']}")
    assert fetched.status_code == 200
