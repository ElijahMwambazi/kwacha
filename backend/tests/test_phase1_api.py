from fastapi.testclient import TestClient


def test_create_list_update_and_delete_item(client: TestClient) -> None:
    create_response = client.post(
        "/items",
        json={
            "name": "Mealie Meal",
            "category": "Food",
            "brand": "Breakfast",
            "default_unit": "kg",
        },
    )

    assert create_response.status_code == 201

    item = create_response.json()

    assert item["id"] == 1
    assert item["name"] == "Mealie Meal"
    assert item["category"] == "Food"
    assert item["brand"] == "Breakfast"
    assert item["default_unit"] == "kg"

    list_response = client.get("/items")

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    update_response = client.patch(
        f"/items/{item['id']}",
        json={
            "brand": "Updated Brand",
            "default_unit": "bag",
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["brand"] == "Updated Brand"
    assert update_response.json()["default_unit"] == "bag"

    delete_response = client.delete(f"/items/{item['id']}")

    assert delete_response.status_code == 204

    final_list_response = client.get("/items")

    assert final_list_response.status_code == 200
    assert final_list_response.json() == []


def test_create_list_update_and_delete_price_observation(client: TestClient) -> None:
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

    create_response = client.post(
        "/prices",
        json={
            "item_id": item_id,
            "shop_name": "Shoprite",
            "location": "Lusaka",
            "price": 55,
            "quantity": 2,
            "unit": "kg",
        },
    )

    assert create_response.status_code == 201

    price = create_response.json()

    assert price["item_id"] == item_id
    assert price["price"] == 55
    assert price["quantity"] == 2
    assert price["price_per_unit"] == 27.5

    list_response = client.get("/prices")

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    update_response = client.patch(
        f"/prices/{price['id']}",
        json={
            "price": 60,
            "quantity": 2,
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["price"] == 60
    assert update_response.json()["price_per_unit"] == 30

    delete_response = client.delete(f"/prices/{price['id']}")

    assert delete_response.status_code == 204

    final_list_response = client.get("/prices")

    assert final_list_response.status_code == 200
    assert final_list_response.json() == []


def test_basket_total_uses_latest_price_observation(client: TestClient) -> None:
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

    first_price_response = client.post(
        "/prices",
        json={
            "item_id": item_id,
            "shop_name": "Shop A",
            "location": "Lusaka",
            "price": 100,
            "quantity": 5,
            "unit": "kg",
            "observed_at": "2026-01-01T08:00:00",
        },
    )

    second_price_response = client.post(
        "/prices",
        json={
            "item_id": item_id,
            "shop_name": "Shop B",
            "location": "Lusaka",
            "price": 120,
            "quantity": 5,
            "unit": "kg",
            "observed_at": "2026-01-02T08:00:00",
        },
    )

    assert first_price_response.status_code == 201
    assert second_price_response.status_code == 201

    basket_response = client.post(
        "/basket",
        json={
            "item_id": item_id,
            "quantity": 3,
            "unit": "kg",
        },
    )

    assert basket_response.status_code == 201

    total_response = client.get("/basket/total")

    assert total_response.status_code == 200

    total = total_response.json()

    assert total["currency"] == "ZMW"
    assert total["total"] == 72
    assert len(total["items"]) == 1
    assert total["items"][0]["item_name"] == "Rice"
    assert total["items"][0]["price_per_unit"] == 24
    assert total["items"][0]["line_total"] == 72
    assert total["items"][0]["shop_name"] == "Shop B"
    assert total["items"][0]["status"] == "priced"


def test_basket_total_handles_missing_price(client: TestClient) -> None:
    item_response = client.post(
        "/items",
        json={
            "name": "Cooking Oil",
            "category": "Food",
            "brand": None,
            "default_unit": "litre",
        },
    )

    item_id = item_response.json()["id"]

    basket_response = client.post(
        "/basket",
        json={
            "item_id": item_id,
            "quantity": 2,
            "unit": "litre",
        },
    )

    assert basket_response.status_code == 201

    total_response = client.get("/basket/total")

    assert total_response.status_code == 200

    total = total_response.json()

    assert total["total"] == 0
    assert len(total["items"]) == 1
    assert total["items"][0]["item_name"] == "Cooking Oil"
    assert total["items"][0]["latest_price"] is None
    assert total["items"][0]["line_total"] is None
    assert total["items"][0]["status"] == "missing_price"


def test_adding_existing_basket_item_updates_quantity(client: TestClient) -> None:
    item_response = client.post(
        "/items",
        json={
            "name": "Beans",
            "category": "Food",
            "brand": None,
            "default_unit": "kg",
        },
    )

    item_id = item_response.json()["id"]

    first_basket_response = client.post(
        "/basket",
        json={
            "item_id": item_id,
            "quantity": 1,
            "unit": "kg",
        },
    )

    second_basket_response = client.post(
        "/basket",
        json={
            "item_id": item_id,
            "quantity": 3,
            "unit": "kg",
        },
    )

    assert first_basket_response.status_code == 201
    assert second_basket_response.status_code == 201

    basket_list_response = client.get("/basket")
    basket_items = basket_list_response.json()

    assert len(basket_items) == 1
    assert basket_items[0]["quantity"] == 3


def test_deleting_item_removes_related_prices_and_basket_entries(
    client: TestClient,
) -> None:
    item_response = client.post(
        "/items",
        json={
            "name": "Bread",
            "category": "Food",
            "brand": None,
            "default_unit": "loaf",
        },
    )

    item_id = item_response.json()["id"]

    price_response = client.post(
        "/prices",
        json={
            "item_id": item_id,
            "shop_name": "Shoprite",
            "location": "Lusaka",
            "price": 20,
            "quantity": 1,
            "unit": "loaf",
        },
    )

    basket_response = client.post(
        "/basket",
        json={
            "item_id": item_id,
            "quantity": 2,
            "unit": "loaf",
        },
    )

    assert price_response.status_code == 201
    assert basket_response.status_code == 201

    delete_response = client.delete(f"/items/{item_id}")

    assert delete_response.status_code == 204

    assert client.get("/items").json() == []
    assert client.get("/prices").json() == []
    assert client.get("/basket").json() == []
    assert client.get("/basket/total").json()["items"] == []


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