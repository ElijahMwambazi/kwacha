from fastapi.testclient import TestClient


def test_approving_duplicate_raw_collection_returns_conflict(
    client: TestClient,
) -> None:
    first_raw_response = client.post(
        "/raw-collections",
        json={
            "item_name": "Rice",
            "shop_name": "Shop A",
            "location": "Lusaka",
            "price": 100,
            "quantity": 5,
            "unit": "kg",
            "collected_at": "2026-01-15T08:00:00",
        },
    )

    second_raw_response = client.post(
        "/raw-collections",
        json={
            "item_name": "Rice",
            "shop_name": "Shop A",
            "location": "Lusaka",
            "price": 100,
            "quantity": 5,
            "unit": "kg",
            "collected_at": "2026-01-15T08:00:00",
        },
    )

    assert first_raw_response.status_code == 201
    assert second_raw_response.status_code == 201

    first_raw_id = first_raw_response.json()["id"]
    second_raw_id = second_raw_response.json()["id"]

    approve_first_response = client.post(
        f"/raw-collections/{first_raw_id}/approve"
    )

    assert approve_first_response.status_code == 201

    approve_second_response = client.post(
        f"/raw-collections/{second_raw_id}/approve"
    )

    assert approve_second_response.status_code == 409
    assert approve_second_response.json()["detail"]["message"] == (
        "Duplicate price observation detected"
    )

    assert len(client.get("/prices").json()) == 1

    rejected_rows = client.get("/raw-collections?status=rejected").json()

    assert len(rejected_rows) == 1
    assert rejected_rows[0]["id"] == second_raw_id
    assert "duplicate_price_observation_id" in rejected_rows[0]["notes"]


def test_bulk_approve_skips_duplicate_raw_collections(client: TestClient) -> None:
    for _ in range(2):
      response = client.post(
          "/raw-collections",
          json={
              "item_name": "Sugar",
              "shop_name": "Shop B",
              "location": "Lusaka",
              "price": 80,
              "quantity": 4,
              "unit": "kg",
              "collected_at": "2026-01-16T08:00:00",
          },
      )

      assert response.status_code == 201

    bulk_response = client.post("/raw-collections/bulk/approve")

    assert bulk_response.status_code == 201

    result = bulk_response.json()

    assert result["approved_count"] == 1
    assert result["created_price_observations_count"] == 1
    assert result["duplicate_count"] == 1
    assert len(result["duplicate_raw_collection_ids"]) == 1

    assert len(client.get("/prices").json()) == 1
    assert len(client.get("/raw-collections?status=approved").json()) == 1
    assert len(client.get("/raw-collections?status=rejected").json()) == 1