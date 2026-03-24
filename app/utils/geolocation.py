from __future__ import annotations

import threading
import time
from collections import deque
from typing import Any

from geopy.distance import geodesic
from geopy.exc import GeocoderServiceError, GeocoderTimedOut, GeopyError
from geopy.geocoders import Nominatim


class GeolocationError(Exception):
    """Domain-level geolocation exception with status code."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


_DEFAULT_TIMEOUT_SECONDS = 5
_MAX_REQUESTS_PER_MINUTE = 50

_geolocator = Nominatim(user_agent="fastapi_app", timeout=_DEFAULT_TIMEOUT_SECONDS)

# Simple in-memory caches for repeated requests.
_forward_cache: dict[str, dict[str, float]] = {}
_reverse_cache: dict[tuple[float, float], dict[str, str]] = {}

# Basic process-local rate limit safeguard.
_rate_limit_lock = threading.Lock()
_request_times: deque[float] = deque()


def _check_rate_limit() -> None:
    now = time.time()
    with _rate_limit_lock:
        while _request_times and now - _request_times[0] > 60:
            _request_times.popleft()

        if len(_request_times) >= _MAX_REQUESTS_PER_MINUTE:
            raise GeolocationError("Too many geolocation requests, please retry shortly", status_code=429)

        _request_times.append(now)


def get_coordinates(address: str) -> dict[str, float]:
    """Geocode address text into latitude/longitude."""

    normalized_address = address.strip()
    if not normalized_address:
        raise GeolocationError("Address must not be empty", status_code=400)

    cached = _forward_cache.get(normalized_address)
    if cached is not None:
        return cached

    _check_rate_limit()
    try:
        location = _geolocator.geocode(normalized_address)
    except GeocoderTimedOut as exc:
        raise GeolocationError("Geocoding service timed out", status_code=500) from exc
    except GeocoderServiceError as exc:
        raise GeolocationError("Geocoding service unavailable", status_code=500) from exc
    except GeopyError as exc:
        raise GeolocationError("Geocoding request failed", status_code=500) from exc

    if location is None:
        raise GeolocationError("Address not found", status_code=400)

    result = {"latitude": float(location.latitude), "longitude": float(location.longitude)}
    _forward_cache[normalized_address] = result
    return result


def get_address(lat: float, lon: float) -> dict[str, str]:
    """Reverse geocode coordinates into a human-readable address."""

    # Rounded key improves hit ratio for tiny floating noise.
    cache_key = (round(lat, 6), round(lon, 6))
    cached = _reverse_cache.get(cache_key)
    if cached is not None:
        return cached

    _check_rate_limit()
    try:
        location = _geolocator.reverse((lat, lon), exactly_one=True)
    except GeocoderTimedOut as exc:
        raise GeolocationError("Reverse geocoding service timed out", status_code=500) from exc
    except GeocoderServiceError as exc:
        raise GeolocationError("Reverse geocoding service unavailable", status_code=500) from exc
    except GeopyError as exc:
        raise GeolocationError("Reverse geocoding request failed", status_code=500) from exc

    if location is None or not location.address:
        raise GeolocationError("Address not found for coordinates", status_code=400)

    result = {"address": str(location.address)}
    _reverse_cache[cache_key] = result
    return result


def calculate_distance(coord1: tuple[float, float], coord2: tuple[float, float]) -> dict[str, float]:
    """Calculate geodesic distance between two coordinates in kilometers."""

    try:
        distance_km = float(geodesic(coord1, coord2).kilometers)
    except (ValueError, TypeError) as exc:
        raise GeolocationError("Invalid coordinates for distance calculation", status_code=400) from exc
    except GeopyError as exc:
        raise GeolocationError("Distance calculation failed", status_code=500) from exc

    return {"distance_km": distance_km}

