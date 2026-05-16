from fastapi.testclient import TestClient


def test_download_raw_price_import_template(client: TestClient) -> None:
    response = client.get("/imports/raw-prices-template.csv")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "kwacha_raw_price_import_template.csv" in response.headers[
        "content-disposition"
    ]

    assert "item_name" in response.text
    assert "shop_name" in response.text
    assert "source" in response.text
    assert "notes" in response.text
    assert "Mealie Meal" in response.text