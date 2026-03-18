from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AddressBase(BaseModel):
    """Shared address fields with validation."""

    name: str = Field(min_length=1, max_length=255)
    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)

    # Extra validators for clearer error messages.
    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        if v < -90.0 or v > 90.0:
            raise ValueError("latitude must be between -90 and 90")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        if v < -180.0 or v > 180.0:
            raise ValueError("longitude must be between -180 and 180")
        return v


class AddressCreate(AddressBase):
    """Payload for creating an address."""


class AddressUpdate(BaseModel):
    """Payload for updating an address."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    latitude: Optional[float] = Field(default=None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(default=None, ge=-180.0, le=180.0)

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return v
        if v < -90.0 or v > 90.0:
            raise ValueError("latitude must be between -90 and 90")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return v
        if v < -180.0 or v > 180.0:
            raise ValueError("longitude must be between -180 and 180")
        return v


class AddressOut(AddressBase):
    """Response model for an address."""

    model_config = ConfigDict(from_attributes=True)

    id: int


class PaginatedAddressResponse(BaseModel):
    """Paginated response for GET /addresses."""

    items: List[AddressOut]
    limit: int
    offset: int
    total: int


class NearbyAddressResponse(BaseModel):
    """Response model for GET /addresses/nearby."""

    items: List["NearbyAddressItem"]
    lat: float
    lon: float
    distance_km: float


class NearbyAddressItem(AddressOut):
    """Address item enriched with computed distance."""

    distance_km: float


NearbyAddressResponse.model_rebuild()

