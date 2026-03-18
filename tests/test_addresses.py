from __future__ import annotations

from typing import Any


def test_create_address(client: Any) -> None:
    payload = {"name": "Home", "latitude": 0.0, "longitude": 0.0}
    resp = client.post("/addresses", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["name"] == "Home"
    assert data["latitude"] == 0.0
    assert data["longitude"] == 0.0
    assert isinstance(data["id"], int)


def test_list_addresses_pagination(client: Any) -> None:
    client.post("/addresses", json={"name": "A", "latitude": 0.0, "longitude": 0.0})
    client.post("/addresses", json={"name": "B", "latitude": 1.0, "longitude": 1.0})

    resp = client.get("/addresses?limit=1&offset=0")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["limit"] == 1
    assert data["offset"] == 0
    assert data["total"] == 2
    assert len(data["items"]) == 1


def test_get_update_delete_address(client: Any) -> None:
    create_resp = client.post("/addresses", json={"name": "Temp", "latitude": 0.0, "longitude": 0.0})
    address_id = create_resp.json()["id"]

    get_resp = client.get(f"/addresses/{address_id}")
    assert get_resp.status_code == 200, get_resp.text
    assert get_resp.json()["name"] == "Temp"

    update_resp = client.put(
        f"/addresses/{address_id}",
        json={"name": "Updated", "latitude": 10.0, "longitude": 20.0},
    )
    assert update_resp.status_code == 200, update_resp.text
    assert update_resp.json()["name"] == "Updated"
    assert update_resp.json()["latitude"] == 10.0
    assert update_resp.json()["longitude"] == 20.0

    del_resp = client.delete(f"/addresses/{address_id}")
    assert del_resp.status_code == 200, del_resp.text
    assert del_resp.json() == {"ok": True}

    missing_resp = client.get(f"/addresses/{address_id}")
    assert missing_resp.status_code == 404


def test_nearby_filtering_haversine(client: Any) -> None:
    # Two addresses close together at the equator.
    # 0.05 degrees longitude ~ 5.56 km at the equator (approx).
    client.post("/addresses", json={"name": "P1", "latitude": 0.0, "longitude": 0.0})
    client.post("/addresses", json={"name": "P2", "latitude": 0.0, "longitude": 0.05})
    # Far away address
    client.post("/addresses", json={"name": "Far", "latitude": 1.0, "longitude": 1.0})

    resp = client.get("/addresses/nearby?lat=0&lon=0&distance=10")
    assert resp.status_code == 200, resp.text
    data = resp.json()

    item_names = sorted([item["name"] for item in data["items"]])
    assert item_names == ["P1", "P2"]

