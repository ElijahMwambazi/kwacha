from fastapi.testclient import TestClient


def test_train_price_model_and_predict_next_price(client: TestClient) -> None:
    item_response = client.post(
        "/items",
        json={
            "name": "Rice",
            "category": "Food",
            "brand": "Local",
            "default_unit": "kg",
        },
    )

    item_id = item_response.json()["id"]

    for price, observed_at in [
        (100, "2026-01-01T08:00:00"),
        (110, "2026-01-02T08:00:00"),
        (120, "2026-01-03T08:00:00"),
        (130, "2026-01-04T08:00:00"),
        (140, "2026-01-05T08:00:00"),
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

    train_response = client.post("/predictions/train-price-model")

    assert train_response.status_code == 201
    assert train_response.json()["training_rows"] == 4
    assert train_response.json()["model_path"]

    prediction_response = client.get(
        f"/predictions/items/{item_id}/ml-next-price"
    )

    assert prediction_response.status_code == 200

    prediction = prediction_response.json()

    assert prediction["item_id"] == item_id
    assert prediction["item_name"] == "Rice"
    assert prediction["method"] == "random_forest_regressor"
    assert prediction["predicted_price_per_unit"] > 0
    assert prediction["model"]["training_rows"] == 4


def test_train_price_model_requires_history(client: TestClient) -> None:
    response = client.post("/predictions/train-price-model")

    assert response.status_code == 400
    assert "Not enough price history" in response.json()["detail"]