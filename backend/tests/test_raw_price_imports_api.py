from io import BytesIO

from fastapi.testclient import TestClient


def test_import_raw_price_collections_csv_creates_pending_raw_rows(
    client: TestClient,
) -> None:
    csv_content = "\n".join(
        [
            "item_name,category,brand,shop_name,location,price,quantity,unit,observed_at,source,notes",
            "Rice,Food,Local,Shop A,Lusaka,100,5,kg,2026-01-15T08:00:00,csv,test row",
            "Sugar,Food,,Shop B,Lusaka,80,4,kg,2026-01-16T08:00:00,csv,test row",
        ]
    )

    response = client.post(
        "/imports/raw-prices.csv",
        files={
            "file": (
                "raw-prices.csv",
                BytesIO(csv_content.encode("utf-8")),
                "text/csv",
            )
        },
    )

    assert response.status_code == 201
    assert response.json()["imported_count"] == 2
    assert response.json()["status"] == "pending_review"

    raw_response = client.get("/raw-collections?status=pending")

    assert raw_response.status_code == 200

    raw_rows = raw_response.json()

    assert len(raw_rows) == 2
    assert raw_rows[0]["status"] == "pending"
    assert raw_rows[1]["status"] == "pending"

    assert client.get("/items").json() == []
    assert client.get("/prices").json() == []


def test_import_raw_price_collections_csv_rolls_back_on_invalid_row(
    client: TestClient,
) -> None:
    csv_content = "\n".join(
        [
            "item_name,category,brand,shop_name,location,price,quantity,unit,observed_at",
            "Rice,Food,Local,Shop A,Lusaka,100,5,kg,2026-01-15T08:00:00",
            "Sugar,Food,,Shop B,Lusaka,not-a-number,4,kg,2026-01-16T08:00:00",
        ]
    )

    response = client.post(
        "/imports/raw-prices.csv",
        files={
            "file": (
                "raw-prices.csv",
                BytesIO(csv_content.encode("utf-8")),
                "text/csv",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"]["message"] == (
        "Raw CSV import failed. No rows were imported."
    )

    assert client.get("/raw-collections?status=pending").json() == []