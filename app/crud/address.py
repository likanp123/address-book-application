from __future__ import annotations

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.address import Address
from app.schemas.address import AddressCreate, AddressUpdate
from app.utils.distance import haversine_distance_km


def create_address(db: Session, address_in: AddressCreate) -> Address:
    """Create and persist a new address."""

    address = Address(
        name=address_in.name,
        latitude=address_in.latitude,
        longitude=address_in.longitude,
    )
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


def get_address(db: Session, address_id: int) -> Optional[Address]:
    """Fetch a single address by id."""

    return db.scalar(select(Address).where(Address.id == address_id))


def list_addresses(db: Session, *, limit: int, offset: int) -> tuple[list[Address], int]:
    """List addresses with pagination.

    Returns (items, total).
    """

    total = db.scalar(select(func.count()).select_from(Address)) or 0
    stmt = select(Address).order_by(Address.id).limit(limit).offset(offset)
    items = list(db.scalars(stmt).all())
    return items, int(total)


def update_address(db: Session, address_id: int, address_in: AddressUpdate) -> Optional[Address]:
    """Update an existing address. Returns updated object or None if missing."""

    address = get_address(db, address_id)
    if address is None:
        return None

    update_fields: dict[str, object] = address_in.model_dump(exclude_unset=True)
    for field_name, value in update_fields.items():
        setattr(address, field_name, value)

    db.add(address)
    db.commit()
    db.refresh(address)
    return address


def delete_address(db: Session, address_id: int) -> bool:
    """Delete an address by id. Returns True if deleted, else False."""

    address = get_address(db, address_id)
    if address is None:
        return False

    db.delete(address)
    db.commit()
    return True


def list_nearby_addresses(
    db: Session, *, lat: float, lon: float, distance_km: float
) -> list[tuple[Address, float]]:
    """List addresses within a distance (km) using Haversine distance.

    Note: This implementation fetches all addresses and filters in Python.
    For large datasets, consider doing filtering at the database level or
    applying a bounding box pre-filter.
    """

    stmt = select(Address)
    addresses = list(db.scalars(stmt).all())

    nearby: list[tuple[Address, float]] = []
    for address in addresses:
        dist = haversine_distance_km(lat, lon, address.latitude, address.longitude)
        if dist <= distance_km:
            nearby.append((address, dist))

    nearby.sort(key=lambda pair: pair[1])
    return nearby

