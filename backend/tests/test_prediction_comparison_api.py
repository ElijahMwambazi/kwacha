from fastapi.testclient import TestClient


def test_compare_item_predictions_returns_baseline_without_trained_model(
    client: TestClient,
) -> None:
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

    response = client.get(f"/predictions/items/{item_id}/compare?window=3")

    assert response.status_code == 200

    comparison = response.json()

    assert comparison["item_id"] == item_id
    assert comparison["item_name"] == "Rice"
    assert comparison["baseline"]["method"] == "moving_average"
    assert comparison["baseline"]["predicted_price_per_unit"] == 24
    assert comparison["ml"] is None
    assert comparison["ml_error"]


def test_compare_item_predictions_returns_baseline_and_ml_after_training(
    client: TestClient,
) -> None:
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
        (90, "2026-01-02T08:00:00"),
        (100, "2026-01-03T08:00:00"),
        (110, "2026-01-04T08:00:00"),
        (120, "2026-01-05T08:00:00"),
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

    train_response = client.post("/predictions/train-price-model")

    assert train_response.status_code == 201

    response = client.get(f"/predictions/items/{item_id}/compare?window=3")

    assert response.status_code == 200

    comparison = response.json()

    assert comparison["baseline"]["method"] == "moving_average"
    assert comparison["ml"]["method"] == "random_forest_regressor"
    assert comparison["ml"]["predicted_price_per_unit"] > 0
    assert comparison["ml_error"] is None