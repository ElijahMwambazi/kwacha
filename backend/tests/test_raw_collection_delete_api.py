
from fastapi.testclient import TestClient


def test_delete_pending_raw_collection(client: TestClient) -> None:
    create_response = client.post(
        "/raw-collections",
        json={
            "item_name": "Rice",
            "shop_name": "Shop A",
            "price": 100,
            "quantity": 5,
            "unit": "kg",
        },
    )

    assert create_response.status_code == 201

    raw_id = create_response.json()["id"]

    delete_response = client.delete(f"/raw-collections/{raw_id}")

    assert delete_response.status_code == 204

    assert client.get("/raw-collections").json() == []
    assert client.get("/raw-collections/stats").json() == {
        "total_count": 0,
        "pending_count": 0,
        "approved_count": 0,
        "rejected_count": 0,
    }


def test_delete_approved_raw_collection_does_not_delete_approved_price(
    client: TestClient,
) -> None:
    create_response = client.post(
        "/raw-collections",
        json={
            "item_name": "Sugar",
            "shop_name": "Shop B",
            "price": 80,
            "quantity": 4,
            "unit": "kg",
        },
    )

    raw_id = create_response.json()["id"]

    approve_response = client.post(f"/raw-collections/{raw_id}/approve")

    assert approve_response.status_code == 201

    delete_response = client.delete(f"/raw-collections/{raw_id}")

    assert delete_response.status_code == 204

    assert client.get("/raw-collections").json() == []
    assert len(client.get("/items").json()) == 1
    assert len(client.get("/prices").json()) == 1


def test_delete_missing_raw_collection_returns_404(client: TestClient) -> None:
    response = client.delete("/raw-collections/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Raw collection not found"