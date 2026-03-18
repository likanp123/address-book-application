from __future__ import annotations

import math


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compute the great-circle distance between two points (in kilometers).

    Uses the Haversine formula assuming a spherical Earth.
    """

    # Earth radius in kilometers.
    earth_radius_km = 6371.0

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat / 2.0) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2.0) ** 2
    c = 2.0 * math.asin(math.sqrt(a))

    return earth_radius_km * c

