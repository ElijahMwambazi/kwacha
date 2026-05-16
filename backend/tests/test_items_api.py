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