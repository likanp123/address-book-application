from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from fastapi.concurrency import run_in_threadpool

from app.core.logger import get_logger
from app.schemas.geolocation import (
    DistanceRequest,
    DistanceResponse,
    GeocodeRequest,
    GeocodeResponse,
    ReverseGeocodeRequest,
    ReverseGeocodeResponse,
)
from app.utils.geolocation import GeolocationError, calculate_distance, get_address, get_coordinates


geolocation_router = APIRouter()
log = get_logger("address_book.api.geolocation")


@geolocation_router.post("/geocode", response_model=GeocodeResponse, status_code=status.HTTP_200_OK)
async def geocode_address(payload: GeocodeRequest) -> GeocodeResponse:
    """Convert an address string to coordinates."""

    try:
        result = await run_in_threadpool(get_coordinates, payload.address)
    except GeolocationError as exc:
        log.warning("geocode failed", extra={"error_message": exc.message})
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    except Exception as exc:
        log.exception("unexpected geocode error")
        raise HTTPException(status_code=500, detail="Unexpected geocoding error") from exc

    log.info("geocode succeeded", extra={"address": payload.address})
    return GeocodeResponse(**result)


@geolocation_router.post("/reverse-geocode", response_model=ReverseGeocodeResponse, status_code=status.HTTP_200_OK)
async def reverse_geocode(payload: ReverseGeocodeRequest) -> ReverseGeocodeResponse:
    """Convert coordinates into a human-readable address."""

    try:
        result = await run_in_threadpool(get_address, payload.latitude, payload.longitude)
    except GeolocationError as exc:
        log.warning("reverse geocode failed", extra={"error_message": exc.message})
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    except Exception as exc:
        log.exception("unexpected reverse geocode error")
        raise HTTPException(status_code=500, detail="Unexpected reverse geocoding error") from exc

    log.info("reverse geocode succeeded")
    return ReverseGeocodeResponse(**result)


@geolocation_router.post("/distance", response_model=DistanceResponse, status_code=status.HTTP_200_OK)
async def distance_between_coordinates(payload: DistanceRequest) -> DistanceResponse:
    """Calculate geodesic distance (in km) between two coordinates."""

    coord1 = (payload.lat1, payload.lon1)
    coord2 = (payload.lat2, payload.lon2)

    try:
        result = await run_in_threadpool(calculate_distance, coord1, coord2)
    except GeolocationError as exc:
        log.warning("distance calculation failed", extra={"error_message": exc.message})
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    except Exception as exc:
        log.exception("unexpected distance calculation error")
        raise HTTPException(status_code=500, detail="Unexpected distance calculation error") from exc

    return DistanceResponse(**result)

