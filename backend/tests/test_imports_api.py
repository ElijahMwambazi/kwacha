from io import BytesIO

from fastapi.testclient import TestClient


def test_import_price_observations_csv_creates_items_and_prices(
    client: TestClient,
) -> None:
    csv_content = "\n".join(
        [
            "item_name,category,brand,shop_name,location,price,quantity,unit,observed_at",
            "Rice,Food,,Shop A,Lusaka,100,5,kg,2026-01-15T08:00:00",
            "Sugar,Food,,Shop B,Lusaka,80,4,kg,2026-01-16T08:00:00",
        ]
    )

    response = client.post(
        "/imports/prices.csv",
        files={
            "file": (
                "prices.csv",
                BytesIO(csv_content.encode("utf-8")),
                "text/csv",
            )
        },
    )

    assert response.status_code == 201
    assert response.json()["imported_count"] == 2
    assert response.json()["created_item_count"] == 2

    items_response = client.get("/items")
    prices_response = client.get("/prices")

    assert len(items_response.json()) == 2
    assert len(prices_response.json()) == 2


def test_import_price_observations_csv_rolls_back_on_invalid_row(
    client: TestClient,
) -> None:
    csv_content = "\n".join(
        [
            "item_name,category,brand,shop_name,location,price,quantity,unit,observed_at",
            "Rice,Food,,Shop A,Lusaka,100,5,kg,2026-01-15T08:00:00",
            "Sugar,Food,,Shop B,Lusaka,not-a-number,4,kg,2026-01-16T08:00:00",
        ]
    )

    response = client.post(
        "/imports/prices.csv",
        files={
            "file": (
                "prices.csv",
                BytesIO(csv_content.encode("utf-8")),
                "text/csv",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"]["message"] == "CSV import failed. No rows were imported."

    assert client.get("/items").json() == []
    assert client.get("/prices").json() == []


def test_import_price_observations_csv_requires_expected_columns(
    client: TestClient,
) -> None:
    csv_content = "\n".join(
        [
            "item_name,shop_name,price",
            "Rice,Shop A,100",
        ]
    )

    response = client.post(
        "/imports/prices.csv",
        files={
            "file": (
                "prices.csv",
                BytesIO(csv_content.encode("utf-8")),
                "text/csv",
            )
        },
    )

    assert response.status_code == 400
    assert "Missing required columns" in response.json()["detail"]

def test_download_price_import_template(client: TestClient) -> None:
    response = client.get("/imports/prices-template.csv")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "kwacha_price_import_template.csv" in response.headers["content-disposition"]

    assert "item_name" in response.text
    assert "shop_name" in response.text
    assert "price" in response.text
    assert "quantity" in response.text
    assert "Mealie Meal" in response.text