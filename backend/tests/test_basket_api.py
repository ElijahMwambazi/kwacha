from fastapi.testclient import TestClient

def test_basket_total_uses_latest_price_observation(client: TestClient) -> None:
    item_response = client.post(
        "/items",
        json={
            "name": "Rice",
            "category": "Food",
            "brand": None,
            "default_unit": "kg",
        },
    )

    item_id = item_response.json()["id"]

    first_price_response = client.post(
        "/prices",
        json={
            "item_id": item_id,
            "shop_name": "Shop A",
            "location": "Lusaka",
            "price": 100,
            "quantity": 5,
            "unit": "kg",
            "observed_at": "2026-01-01T08:00:00",
        },
    )

    second_price_response = client.post(
        "/prices",
        json={
            "item_id": item_id,
            "shop_name": "Shop B",
            "location": "Lusaka",
            "price": 120,
            "quantity": 5,
            "unit": "kg",
            "observed_at": "2026-01-02T08:00:00",
        },
    )

    assert first_price_response.status_code == 201
    assert second_price_response.status_code == 201

    basket_response = client.post(
        "/basket",
        json={
            "item_id": item_id,
            "quantity": 3,
            "unit": "kg",
        },
    )

    assert basket_response.status_code == 201

    total_response = client.get("/basket/total")

    assert total_response.status_code == 200

    total = total_response.json()

    assert total["currency"] == "ZMW"
    assert total["total"] == 72
    assert len(total["items"]) == 1
    assert total["items"][0]["item_name"] == "Rice"
    assert total["items"][0]["price_per_unit"] == 24
    assert total["items"][0]["line_total"] == 72
    assert total["items"][0]["shop_name"] == "Shop B"
    assert total["items"][0]["status"] == "priced"

def test_basket_total_handles_missing_price(client: TestClient) -> None:
    item_response = client.post(
        "/items",
        json={
            "name": "Cooking Oil",
            "category": "Food",
            "brand": None,
            "default_unit": "litre",
        },
    )

    item_id = item_response.json()["id"]

    basket_response = client.post(
        "/basket",
        json={
            "item_id": item_id,
            "quantity": 2,
            "unit": "litre",
        },
    )

    assert basket_response.status_code == 201

    total_response = client.get("/basket/total")

    assert total_response.status_code == 200

    total = total_response.json()

    assert total["total"] == 0
    assert len(total["items"]) == 1
    assert total["items"][0]["item_name"] == "Cooking Oil"
    assert total["items"][0]["latest_price"] is None
    assert total["items"][0]["line_total"] is None
    assert total["items"][0]["status"] == "missing_price"

def test_adding_existing_basket_item_updates_quantity(client: TestClient) -> None:
    item_response = client.post(
        "/items",
        json={
            "name": "Beans",
            "category": "Food",
            "brand": None,
            "default_unit": "kg",
        },
    )

    item_id = item_response.json()["id"]

    first_basket_response = client.post(
        "/basket",
        json={
            "item_id": item_id,
            "quantity": 1,
            "unit": "kg",
        },
    )

    second_basket_response = client.post(
        "/basket",
        json={
            "item_id": item_id,
            "quantity": 3,
            "unit": "kg",
        },
    )

    assert first_basket_response.status_code == 201
    assert second_basket_response.status_code == 201

    basket_list_response = client.get("/basket")
    basket_items = basket_list_response.json()

    assert len(basket_items) == 1
    assert basket_items[0]["quantity"] == 3