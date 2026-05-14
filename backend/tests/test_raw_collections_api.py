from fastapi.testclient import TestClient


def test_create_approve_raw_collection_creates_item_and_price(
    client: TestClient,
) -> None:
    create_response = client.post(
        "/raw-collections",
        json={
            "item_name": "Rice",
            "category": "Food",
            "brand": "Local",
            "shop_name": "Shop A",
            "location": "Lusaka",
            "price": 100,
            "quantity": 5,
            "unit": "kg",
            "source": "manual",
        },
    )

    assert create_response.status_code == 201

    raw = create_response.json()

    assert raw["status"] == "pending"

    approve_response = client.post(f"/raw-collections/{raw['id']}/approve")

    assert approve_response.status_code == 201

    approved = approve_response.json()

    assert approved["raw_collection"]["status"] == "approved"
    assert approved["item"]["name"] == "Rice"
    assert approved["price_observation"]["price_per_unit"] == 20

    assert len(client.get("/items").json()) == 1
    assert len(client.get("/prices").json()) == 1


def test_reject_raw_collection(client: TestClient) -> None:
    create_response = client.post(
        "/raw-collections",
        json={
            "item_name": "Sugar",
            "shop_name": "Shop B",
            "price": 80,
            "quantity": 4,
            "unit": "kg",
        },
    )

    raw_id = create_response.json()["id"]

    reject_response = client.post(f"/raw-collections/{raw_id}/reject")

    assert reject_response.status_code == 200
    assert reject_response.json()["status"] == "rejected"

    assert client.get("/items").json() == []
    assert client.get("/prices").json() == []


def test_list_pending_raw_collections(client: TestClient) -> None:
    first_response = client.post(
        "/raw-collections",
        json={
            "item_name": "Bread",
            "shop_name": "Shop A",
            "price": 20,
            "quantity": 1,
            "unit": "loaf",
        },
    )

    second_response = client.post(
        "/raw-collections",
        json={
            "item_name": "Eggs",
            "shop_name": "Shop B",
            "price": 95,
            "quantity": 1,
            "unit": "tray",
        },
    )

    client.post(f"/raw-collections/{second_response.json()['id']}/reject")

    pending_response = client.get("/raw-collections?status=pending")

    assert pending_response.status_code == 200

    pending = pending_response.json()

    assert len(pending) == 1
    assert pending[0]["id"] == first_response.json()["id"]