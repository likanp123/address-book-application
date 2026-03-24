from __future__ import annotations

from pydantic import BaseModel, Field


class GeocodeRequest(BaseModel):
    """Request payload for forward geocoding."""

    address: str = Field(min_length=3, max_length=500)


class GeocodeResponse(BaseModel):
    """Response payload for forward geocoding."""

    latitude: float
    longitude: float


class ReverseGeocodeRequest(BaseModel):
    """Request payload for reverse geocoding."""

    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)


class ReverseGeocodeResponse(BaseModel):
    """Response payload for reverse geocoding."""

    address: str


class DistanceRequest(BaseModel):
    """Request payload for distance calculation between two coordinates."""

    lat1: float = Field(ge=-90.0, le=90.0)
    lon1: float = Field(ge=-180.0, le=180.0)
    lat2: float = Field(ge=-90.0, le=90.0)
    lon2: float = Field(ge=-180.0, le=180.0)


class DistanceResponse(BaseModel):
    """Response payload for distance calculation."""

    distance_km: float

