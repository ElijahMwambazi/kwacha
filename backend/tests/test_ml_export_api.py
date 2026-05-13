from fastapi.testclient import TestClient


def test_export_ml_prices_csv_includes_item_and_indicator_features(
    client: TestClient,
) -> None:
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

    client.post(
        "/indicators",
        json={
            "name": "exchange_rate_usd_zmw",
            "value": 25.5,
            "unit": "ZMW",
            "source": "BOZ",
            "observed_at": "2026-01-01T08:00:00",
        },
    )

    client.post(
        "/indicators",
        json={
            "name": "fuel_price_petrol",
            "value": 31.2,
            "unit": "ZMW/litre",
            "source": "ERB",
            "observed_at": "2026-01-01T08:00:00",
        },
    )

    client.post(
        "/indicators",
        json={
            "name": "official_inflation",
            "value": 14.2,
            "unit": "%",
            "source": "ZamStats",
            "observed_at": "2026-01-01T08:00:00",
        },
    )

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

    response = client.get("/export/ml-prices.csv")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "kwacha_ml_prices.csv" in response.headers["content-disposition"]

    assert "item_name" in response.text
    assert "price_per_unit" in response.text
    assert "exchange_rate_usd_zmw" in response.text
    assert "fuel_price_petrol" in response.text
    assert "official_inflation" in response.text
    assert "Rice" in response.text
    assert "25.5" in response.text
    assert "31.2" in response.text
    assert "14.2" in response.text


def test_export_ml_prices_csv_uses_latest_indicator_before_price_date(
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

    client.post(
        "/indicators",
        json={
            "name": "exchange_rate_usd_zmw",
            "value": 24.5,
            "unit": "ZMW",
            "source": "BOZ",
            "observed_at": "2026-01-01T08:00:00",
        },
    )

    client.post(
        "/indicators",
        json={
            "name": "exchange_rate_usd_zmw",
            "value": 26.5,
            "unit": "ZMW",
            "source": "BOZ",
            "observed_at": "2026-02-01T08:00:00",
        },
    )

    client.post(
        "/prices",
        json={
            "item_id": item_id,
            "shop_name": "Shop B",
            "location": "Lusaka",
            "price": 80,
            "quantity": 4,
            "unit": "kg",
            "observed_at": "2026-01-15T08:00:00",
        },
    )

    response = client.get("/export/ml-prices.csv")

    assert response.status_code == 200
    assert "24.5" in response.text
    assert "26.5" not in response.text