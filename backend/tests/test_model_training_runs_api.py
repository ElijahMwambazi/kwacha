from fastapi.testclient import TestClient


def test_training_price_model_creates_training_run(client: TestClient) -> None:
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
    assert train_response.json()["training_run_id"] == 1

    runs_response = client.get("/predictions/price-model/training-runs")

    assert runs_response.status_code == 200

    runs = runs_response.json()

    assert len(runs) == 1
    assert runs[0]["id"] == 1
    assert runs[0]["model_name"] == "price_model"
    assert runs[0]["model_type"] == "random_forest_regressor"
    assert runs[0]["target"] == "price_per_unit"
    assert runs[0]["training_rows"] == 2