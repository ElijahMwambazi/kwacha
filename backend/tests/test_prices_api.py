from fastapi.testclient import TestClient

def test_create_list_update_and_delete_price_observation(client: TestClient) -> None:
    item_response = client.post(
        "/items",
        json={
            "name": "Sugar",
            "category": "Food",
            "brand": None,
            "default_unit": "kg",
        },
    )

    item_id = item_response.json()["id"]

    create_response = client.post(
        "/prices",
        json={
            "item_id": item_id,
            "shop_name": "Shoprite",
            "location": "Lusaka",
            "price": 55,
            "quantity": 2,
            "unit": "kg",
        },
    )

    assert create_response.status_code == 201

    price = create_response.json()

    assert price["item_id"] == item_id
    assert price["price"] == 55
    assert price["quantity"] == 2
    assert price["price_per_unit"] == 27.5

    list_response = client.get("/prices")

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    update_response = client.patch(
        f"/prices/{price['id']}",
        json={
            "price": 60,
            "quantity": 2,
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["price"] == 60
    assert update_response.json()["price_per_unit"] == 30

    delete_response = client.delete(f"/prices/{price['id']}")

    assert delete_response.status_code == 204

    final_list_response = client.get("/prices")

    assert final_list_response.status_code == 200
    assert final_list_response.json() == []