from fastapi.testclient import TestClient


def test_price_model_status_is_untrained_by_default(client: TestClient) -> None:
    response = client.get("/predictions/price-model/status")

    assert response.status_code == 200

    status = response.json()

    assert status["is_trained"] is False
    assert status["trained_at"] is None
    assert status["training_rows"] == 0
    assert status["metrics"] is None


def test_price_model_status_after_training_and_reset(client: TestClient) -> None:
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
        (110, "2026-01-02T08:00:00"),
        (120, "2026-01-03T08:00:00"),
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

    trained_status_response = client.get("/predictions/price-model/status")

    assert trained_status_response.status_code == 200

    trained_status = trained_status_response.json()

    assert trained_status["is_trained"] is True
    assert trained_status["trained_at"] is not None
    assert trained_status["training_rows"] == 2
    assert trained_status["metrics"] is not None

    reset_response = client.delete("/predictions/price-model")

    assert reset_response.status_code == 200

    reset_status = reset_response.json()

    assert reset_status["is_trained"] is False
    assert reset_status["trained_at"] is None
    assert reset_status["training_rows"] == 0
    assert reset_status["metrics"] is None