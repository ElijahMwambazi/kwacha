from fastapi.testclient import TestClient


def test_raw_collection_stats_counts_review_statuses(client: TestClient) -> None:
    first_response = client.post(
        "/raw-collections",
        json={
            "item_name": "Rice",
            "shop_name": "Shop A",
            "price": 100,
            "quantity": 5,
            "unit": "kg",
        },
    )

    second_response = client.post(
        "/raw-collections",
        json={
            "item_name": "Sugar",
            "shop_name": "Shop B",
            "price": 80,
            "quantity": 4,
            "unit": "kg",
        },
    )

    third_response = client.post(
        "/raw-collections",
        json={
            "item_name": "Bread",
            "shop_name": "Shop C",
            "price": 20,
            "quantity": 1,
            "unit": "loaf",
        },
    )

    client.post(f"/raw-collections/{first_response.json()['id']}/approve")
    client.post(f"/raw-collections/{second_response.json()['id']}/reject")

    assert third_response.status_code == 201

    response = client.get("/raw-collections/stats")

    assert response.status_code == 200

    stats = response.json()

    assert stats["total_count"] == 3
    assert stats["pending_count"] == 1
    assert stats["approved_count"] == 1
    assert stats["rejected_count"] == 1