from __future__ import annotations

from typing import Any

from app.utils.geolocation import GeolocationError


def test_geocode_success(client: Any, monkeypatch: Any) -> None:
    def fake_get_coordinates(address: str) -> dict[str, float]:
        assert address == "221B Baker Street, London"
        return {"latitude": 51.5237, "longitude": -0.1585}

    monkeypatch.setattr("app.api.routes.geolocation.get_coordinates", fake_get_coordinates)

    resp = client.post("/geo/geocode", json={"address": "221B Baker Street, London"})
    assert resp.status_code == 200, resp.text
    assert resp.json() == {"latitude": 51.5237, "longitude": -0.1585}


def test_geocode_invalid_address_returns_400(client: Any, monkeypatch: Any) -> None:
    def fake_get_coordinates(address: str) -> dict[str, float]:
        raise GeolocationError("Address not found", status_code=400)

    monkeypatch.setattr("app.api.routes.geolocation.get_coordinates", fake_get_coordinates)

    resp = client.post("/geo/geocode", json={"address": "invalid address"})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Address not found"


def test_reverse_geocode_success(client: Any, monkeypatch: Any) -> None:
    def fake_get_address(lat: float, lon: float) -> dict[str, str]:
        assert lat == 28.6139
        assert lon == 77.209
        return {"address": "New Delhi, Delhi, India"}

    monkeypatch.setattr("app.api.routes.geolocation.get_address", fake_get_address)

    resp = client.post("/geo/reverse-geocode", json={"latitude": 28.6139, "longitude": 77.2090})
    assert resp.status_code == 200, resp.text
    assert resp.json() == {"address": "New Delhi, Delhi, India"}


def test_distance_success(client: Any, monkeypatch: Any) -> None:
    def fake_calculate_distance(coord1: tuple[float, float], coord2: tuple[float, float]) -> dict[str, float]:
        assert coord1 == (28.6139, 77.209)
        assert coord2 == (19.076, 72.8777)
        return {"distance_km": 1150.42}

    monkeypatch.setattr("app.api.routes.geolocation.calculate_distance", fake_calculate_distance)

    resp = client.post(
        "/geo/distance",
        json={"lat1": 28.6139, "lon1": 77.2090, "lat2": 19.0760, "lon2": 72.8777},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json() == {"distance_km": 1150.42}


def test_distance_validation_error(client: Any) -> None:
    # lat1 is outside valid range [-90, 90].
    resp = client.post(
        "/geo/distance",
        json={"lat1": 120.0, "lon1": 77.2090, "lat2": 19.0760, "lon2": 72.8777},
    )
    assert resp.status_code == 422

