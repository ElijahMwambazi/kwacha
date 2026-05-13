from fastapi.testclient import TestClient


def test_price_trends_can_be_filtered_by_item(client: TestClient) -> None:
    first_item_response = client.post(
        "/items",
        json={
            "name": "Rice",
            "category": "Food",
            "brand": None,
            "default_unit": "kg",
        },
    )

    second_item_response = client.post(
        "/items",
        json={
            "name": "Sugar",
            "category": "Food",
            "brand": None,
            "default_unit": "kg",
        },
    )

    first_item_id = first_item_response.json()["id"]
    second_item_id = second_item_response.json()["id"]

    client.post(
        "/prices",
        json={
            "item_id": first_item_id,
            "shop_name": "Shop A",
            "location": "Lusaka",
            "price": 100,
            "quantity": 5,
            "unit": "kg",
        },
    )

    client.post(
        "/prices",
        json={
            "item_id": second_item_id,
            "shop_name": "Shop B",
            "location": "Lusaka",
            "price": 80,
            "quantity": 4,
            "unit": "kg",
        },
    )

    response = client.get(f"/analytics/price-trends?item_id={first_item_id}")

    assert response.status_code == 200

    trends = response.json()

    assert len(trends) == 1
    assert trends[0]["item_id"] == first_item_id
    assert trends[0]["item_name"] == "Rice"
    assert trends[0]["price_per_unit"] == 20


def test_shop_comparison_returns_average_price_per_unit(client: TestClient) -> None:
    item_response = client.post(
        "/items",
        json={
            "name": "Mealie Meal",
            "category": "Food",
            "brand": None,
            "default_unit": "kg",
        },
    )

    item_id = item_response.json()["id"]

    client.post(
        "/prices",
        json={
            "item_id": item_id,
            "shop_name": "Shop A",
            "location": "Lusaka",
            "price": 100,
            "quantity": 5,
            "unit": "kg",
        },
    )

    client.post(
        "/prices",
        json={
            "item_id": item_id,
            "shop_name": "Shop A",
            "location": "Lusaka",
            "price": 120,
            "quantity": 5,
            "unit": "kg",
        },
    )

    response = client.get(f"/analytics/shop-comparison?item_id={item_id}")

    assert response.status_code == 200

    comparison = response.json()

    assert len(comparison) == 1
    assert comparison[0]["item_id"] == item_id
    assert comparison[0]["item_name"] == "Mealie Meal"
    assert comparison[0]["shop_name"] == "Shop A"
    assert comparison[0]["observation_count"] == 2
    assert comparison[0]["min_price_per_unit"] == 20
    assert comparison[0]["max_price_per_unit"] == 24
    assert comparison[0]["avg_price_per_unit"] == 22