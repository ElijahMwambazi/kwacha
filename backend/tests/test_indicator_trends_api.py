from fastapi.testclient import TestClient


def test_indicator_trends_can_be_filtered_by_name(client: TestClient) -> None:
    client.post(
        "/indicators",
        json={
            "name": "exchange_rate_usd_zmw",
            "value": 25.5,
            "unit": "ZMW",
            "source": "BOZ",
            "observed_at": "2026-05-13T08:00:00",
        },
    )

    client.post(
        "/indicators",
        json={
            "name": "official_inflation",
            "value": 14.2,
            "unit": "%",
            "source": "ZamStats",
            "observed_at": "2026-05-13T08:00:00",
        },
    )

    response = client.get("/analytics/indicator-trends?name=exchange_rate_usd_zmw")

    assert response.status_code == 200

    trends = response.json()

    assert len(trends) == 1
    assert trends[0]["name"] == "exchange_rate_usd_zmw"
    assert trends[0]["value"] == 25.5
    assert trends[0]["unit"] == "ZMW"
    assert trends[0]["source"] == "BOZ"


def test_indicator_trends_are_ordered_by_observed_at(client: TestClient) -> None:
    client.post(
        "/indicators",
        json={
            "name": "fuel_price_petrol",
            "value": 31.2,
            "unit": "ZMW/litre",
            "source": "ERB",
            "observed_at": "2026-06-01T08:00:00",
        },
    )

    client.post(
        "/indicators",
        json={
            "name": "fuel_price_petrol",
            "value": 29.8,
            "unit": "ZMW/litre",
            "source": "ERB",
            "observed_at": "2026-05-01T08:00:00",
        },
    )

    response = client.get("/analytics/indicator-trends?name=fuel_price_petrol")

    assert response.status_code == 200

    trends = response.json()

    assert len(trends) == 2
    assert trends[0]["value"] == 29.8
    assert trends[1]["value"] == 31.2