from fastapi.testclient import TestClient


def test_update_pending_raw_collection(client: TestClient) -> None:
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
            "notes": "old note",
        },
    )

    assert create_response.status_code == 201

    raw_id = create_response.json()["id"]

    update_response = client.patch(
        f"/raw-collections/{raw_id}",
        json={
            "item_name": "Rice Premium",
            "category": "Food",
            "brand": "Updated Brand",
            "shop_name": "Shop B",
            "location": "Kitwe",
            "price": 125,
            "quantity": 5,
            "unit": "kg",
            "source": "edited",
            "notes": "updated note",
        },
    )

    assert update_response.status_code == 200

    updated = update_response.json()

    assert updated["item_name"] == "Rice Premium"
    assert updated["brand"] == "Updated Brand"
    assert updated["shop_name"] == "Shop B"
    assert updated["location"] == "Kitwe"
    assert updated["price"] == 125
    assert updated["quantity"] == 5
    assert updated["source"] == "edited"
    assert updated["notes"] == "updated note"

    approve_response = client.post(f"/raw-collections/{raw_id}/approve")

    assert approve_response.status_code == 201

    approved = approve_response.json()

    assert approved["item"]["name"] == "Rice Premium"
    assert approved["price_observation"]["shop_name"] == "Shop B"
    assert approved["price_observation"]["location"] == "Kitwe"
    assert approved["price_observation"]["price"] == 125
    assert approved["price_observation"]["price_per_unit"] == 25


def test_cannot_update_approved_raw_collection(client: TestClient) -> None:
    create_response = client.post(
        "/raw-collections",
        json={
            "item_name": "Sugar",
            "shop_name": "Shop A",
            "price": 80,
            "quantity": 4,
            "unit": "kg",
        },
    )

    raw_id = create_response.json()["id"]

    approve_response = client.post(f"/raw-collections/{raw_id}/approve")

    assert approve_response.status_code == 201

    update_response = client.patch(
        f"/raw-collections/{raw_id}",
        json={
            "price": 100,
        },
    )

    assert update_response.status_code == 400
    assert update_response.json()["detail"] == "Only pending raw collections can be updated"