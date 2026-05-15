from fastapi.testclient import TestClient


def test_bulk_approve_raw_collections(client: TestClient) -> None:
    for item_name, price in [
        ("Rice", 100),
        ("Sugar", 80),
    ]:
        response = client.post(
            "/raw-collections",
            json={
                "item_name": item_name,
                "category": "Food",
                "shop_name": "Shop A",
                "location": "Lusaka",
                "price": price,
                "quantity": 5,
                "unit": "kg",
                "source": "manual",
            },
        )

        assert response.status_code == 201

    approve_response = client.post("/raw-collections/bulk/approve")

    assert approve_response.status_code == 201

    result = approve_response.json()

    assert result["approved_count"] == 2
    assert result["created_items_count"] == 2
    assert result["created_price_observations_count"] == 2

    pending_response = client.get("/raw-collections?status=pending")
    approved_response = client.get("/raw-collections?status=approved")

    assert pending_response.json() == []
    assert len(approved_response.json()) == 2
    assert len(client.get("/items").json()) == 2
    assert len(client.get("/prices").json()) == 2


def test_bulk_reject_raw_collections(client: TestClient) -> None:
    for item_name, price in [
        ("Bread", 20),
        ("Eggs", 95),
    ]:
        response = client.post(
            "/raw-collections",
            json={
                "item_name": item_name,
                "shop_name": "Shop B",
                "price": price,
                "quantity": 1,
                "unit": "unit",
            },
        )

        assert response.status_code == 201

    reject_response = client.post("/raw-collections/bulk/reject")

    assert reject_response.status_code == 200

    result = reject_response.json()

    assert result["rejected_count"] == 2

    pending_response = client.get("/raw-collections?status=pending")
    rejected_response = client.get("/raw-collections?status=rejected")

    assert pending_response.json() == []
    assert len(rejected_response.json()) == 2
    assert client.get("/items").json() == []
    assert client.get("/prices").json() == []