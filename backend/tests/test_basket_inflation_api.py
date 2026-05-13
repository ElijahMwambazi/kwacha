from fastapi.testclient import TestClient


def test_basket_inflation_returns_monthly_basket_totals(client: TestClient) -> None:
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

    client.post(
        "/prices",
        json={
            "item_id": item_id,
            "shop_name": "Shop A",
            "location": "Lusaka",
            "price": 100,
            "quantity": 5,
            "unit": "kg",
            "observed_at": "2026-01-15T08:00:00",
        },
    )

    client.post(
        "/prices",
        json={
            "item_id": item_id,
            "shop_name": "Shop A",
            "location": "Lusaka",
            "price": 125,
            "quantity": 5,
            "unit": "kg",
            "observed_at": "2026-02-15T08:00:00",
        },
    )

    client.post(
        "/basket",
        json={
            "item_id": item_id,
            "quantity": 2,
            "unit": "kg",
        },
    )

    response = client.get("/analytics/basket-inflation")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    assert data[0]["month"] == "2026-01"
    assert data[0]["basket_total"] == 40
    assert data[0]["monthly_change_percent"] is None
    assert data[0]["priced_items_count"] == 1
    assert data[0]["missing_items_count"] == 0

    assert data[1]["month"] == "2026-02"
    assert data[1]["basket_total"] == 50
    assert data[1]["monthly_change_percent"] == 25
    assert data[1]["priced_items_count"] == 1
    assert data[1]["missing_items_count"] == 0


def test_basket_inflation_handles_missing_prices_for_some_items(
    client: TestClient,
) -> None:
    first_item_response = client.post(
        "/items",
        json={
            "name": "Rice",
            "category": "Food",
            "brand": None,
            "default_unit": "kg",
        },
    )

    second_item_response = client.post(
        "/items",
        json={
            "name": "Sugar",
            "category": "Food",
            "brand": None,
            "default_unit": "kg",
        },
    )

    first_item_id = first_item_response.json()["id"]
    second_item_id = second_item_response.json()["id"]

    client.post(
        "/prices",
        json={
            "item_id": first_item_id,
            "shop_name": "Shop A",
            "location": "Lusaka",
            "price": 100,
            "quantity": 5,
            "unit": "kg",
            "observed_at": "2026-01-15T08:00:00",
        },
    )

    client.post(
        "/basket",
        json={
            "item_id": first_item_id,
            "quantity": 2,
            "unit": "kg",
        },
    )

    client.post(
        "/basket",
        json={
            "item_id": second_item_id,
            "quantity": 3,
            "unit": "kg",
        },
    )

    response = client.get("/analytics/basket-inflation")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["month"] == "2026-01"
    assert data[0]["basket_total"] == 40
    assert data[0]["priced_items_count"] == 1
    assert data[0]["missing_items_count"] == 1