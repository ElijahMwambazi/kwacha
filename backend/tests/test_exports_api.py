from fastapi.testclient import TestClient

def test_export_items_csv(client: TestClient) -> None:
    client.post(
        "/items",
        json={
            "name": "Salt",
            "category": "Food",
            "brand": None,
            "default_unit": "kg",
        },
    )

    response = client.get("/export/items.csv")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "kwacha_items.csv" in response.headers["content-disposition"]
    assert "Salt" in response.text
    assert "default_unit" in response.text


def test_export_prices_csv(client: TestClient) -> None:
    item_response = client.post(
        "/items",
        json={
            "name": "Milk",
            "category": "Food",
            "brand": None,
            "default_unit": "litre",
        },
    )

    client.post(
        "/prices",
        json={
            "item_id": item_response.json()["id"],
            "shop_name": "Pick n Pay",
            "location": "Lusaka",
            "price": 35,
            "quantity": 1,
            "unit": "litre",
        },
    )

    response = client.get("/export/prices.csv")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "kwacha_price_observations.csv" in response.headers["content-disposition"]
    assert "Milk" in response.text
    assert "Pick n Pay" in response.text


def test_export_basket_csv(client: TestClient) -> None:
    item_response = client.post(
        "/items",
        json={
            "name": "Eggs",
            "category": "Food",
            "brand": None,
            "default_unit": "tray",
        },
    )

    item_id = item_response.json()["id"]

    client.post(
        "/prices",
        json={
            "item_id": item_id,
            "shop_name": "Market",
            "location": "Lusaka",
            "price": 95,
            "quantity": 1,
            "unit": "tray",
        },
    )

    client.post(
        "/basket",
        json={
            "item_id": item_id,
            "quantity": 2,
            "unit": "tray",
        },
    )

    response = client.get("/export/basket.csv")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "kwacha_basket.csv" in response.headers["content-disposition"]
    assert "Eggs" in response.text
    assert "priced" in response.text