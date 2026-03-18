from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud.address import create_address, delete_address, get_address, list_addresses, list_nearby_addresses, update_address
from app.core.logger import get_logger
from app.db.session import get_db
from app.schemas.address import (
    AddressCreate,
    AddressOut,
    AddressUpdate,
    NearbyAddressItem,
    NearbyAddressResponse,
    PaginatedAddressResponse,
)


router = APIRouter(tags=["addresses"])

log = get_logger("address_book.api.addresses")


@router.post("/addresses", response_model=AddressOut, status_code=status.HTTP_201_CREATED)
def create_address_endpoint(address_in: AddressCreate, db: Session = Depends(get_db)) -> AddressOut:
    created = create_address(db, address_in=address_in)
    log.info("address created", extra={"address_id": created.id, "address_name": created.name})
    return created


@router.get("/addresses", response_model=PaginatedAddressResponse)
def list_addresses_endpoint(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> PaginatedAddressResponse:
    items, total = list_addresses(db, limit=limit, offset=offset)
    return PaginatedAddressResponse(items=items, limit=limit, offset=offset, total=total)


@router.get("/addresses/nearby", response_model=NearbyAddressResponse)
def nearby_addresses_endpoint(
    lat: float = Query(..., ge=-90.0, le=90.0),
    lon: float = Query(..., ge=-180.0, le=180.0),
    distance: float = Query(..., gt=0.0, description="Search radius in kilometers"),
    db: Session = Depends(get_db),
) -> NearbyAddressResponse:
    nearby_pairs = list_nearby_addresses(db, lat=lat, lon=lon, distance_km=distance)
    items: List[NearbyAddressItem] = [
        NearbyAddressItem(
            id=address.id,
            name=address.name,
            latitude=address.latitude,
            longitude=address.longitude,
            distance_km=dist,
        )
        for address, dist in nearby_pairs
    ]
    return NearbyAddressResponse(items=items, lat=lat, lon=lon, distance_km=distance)


@router.get("/addresses/{address_id}", response_model=AddressOut)
def get_address_endpoint(address_id: int, db: Session = Depends(get_db)) -> AddressOut:
    address = get_address(db, address_id=address_id)
    if address is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    return address


@router.put("/addresses/{address_id}", response_model=AddressOut)
def update_address_endpoint(
    address_id: int,
    address_in: AddressUpdate,
    db: Session = Depends(get_db),
) -> AddressOut:
    updated = update_address(db, address_id=address_id, address_in=address_in)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    log.info("address updated", extra={"address_id": updated.id, "address_name": updated.name})
    return updated


@router.delete("/addresses/{address_id}", status_code=status.HTTP_200_OK)
def delete_address_endpoint(address_id: int, db: Session = Depends(get_db)) -> dict[str, bool]:
    deleted = delete_address(db, address_id=address_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    log.info("address deleted", extra={"address_id": address_id})
    return {"ok": True}

