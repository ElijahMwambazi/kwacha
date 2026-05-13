from fastapi.testclient import TestClient


def test_predict_next_item_price_uses_moving_average(client: TestClient) -> None:
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

    for price, observed_at in [
        (100, "2026-01-01T08:00:00"),
        (120, "2026-01-02T08:00:00"),
        (140, "2026-01-03T08:00:00"),
    ]:
        client.post(
            "/prices",
            json={
                "item_id": item_id,
                "shop_name": "Shop A",
                "location": "Lusaka",
                "price": price,
                "quantity": 5,
                "unit": "kg",
                "observed_at": observed_at,
            },
        )

    response = client.get(f"/predictions/items/{item_id}/next-price?window=3")

    assert response.status_code == 200

    prediction = response.json()

    assert prediction["item_id"] == item_id
    assert prediction["item_name"] == "Rice"
    assert prediction["method"] == "moving_average"
    assert prediction["observations_used"] == 3
    assert prediction["predicted_price_per_unit"] == 24
    assert prediction["latest_price_per_unit"] == 28
    assert prediction["latest_change_percent"] == 16.67
    assert prediction["confidence"] == "low"


def test_predict_next_basket_total(client: TestClient) -> None:
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

    for price, observed_at in [
        (80, "2026-01-01T08:00:00"),
        (100, "2026-01-02T08:00:00"),
    ]:
        client.post(
            "/prices",
            json={
                "item_id": item_id,
                "shop_name": "Shop B",
                "location": "Lusaka",
                "price": price,
                "quantity": 4,
                "unit": "kg",
                "observed_at": observed_at,
            },
        )

    client.post(
        "/basket",
        json={
            "item_id": item_id,
            "quantity": 3,
            "unit": "kg",
        },
    )

    response = client.get("/predictions/basket/next-total?window=2")

    assert response.status_code == 200

    prediction = response.json()

    assert prediction["method"] == "moving_average"
    assert prediction["predicted_total"] == 67.5
    assert len(prediction["items"]) == 1
    assert prediction["items"][0]["item_name"] == "Sugar"
    assert prediction["items"][0]["predicted_price_per_unit"] == 22.5
    assert prediction["items"][0]["predicted_line_total"] == 67.5


def test_predict_next_item_price_returns_404_without_history(
    client: TestClient,
) -> None:
    item_response = client.post(
        "/items",
        json={
            "name": "Bread",
            "category": "Food",
            "brand": None,
            "default_unit": "loaf",
        },
    )

    item_id = item_response.json()["id"]

    response = client.get(f"/predictions/items/{item_id}/next-price")

    assert response.status_code == 404
    assert response.json()["detail"] == "No price observations found for item"