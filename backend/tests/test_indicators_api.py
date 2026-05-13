from fastapi.testclient import TestClient


def test_create_list_update_and_delete_public_indicator(
    client: TestClient,
) -> None:
    create_response = client.post(
        "/indicators",
        json={
            "name": "exchange_rate_usd_zmw",
            "value": 25.5,
            "unit": "ZMW",
            "source": "BOZ",
            "observed_at": "2026-05-13T08:00:00",
        },
    )

    assert create_response.status_code == 201

    indicator = create_response.json()

    assert indicator["id"] == 1
    assert indicator["name"] == "exchange_rate_usd_zmw"
    assert indicator["value"] == 25.5
    assert indicator["unit"] == "ZMW"
    assert indicator["source"] == "BOZ"

    list_response = client.get("/indicators")

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    filtered_response = client.get("/indicators?name=exchange_rate_usd_zmw")

    assert filtered_response.status_code == 200
    assert len(filtered_response.json()) == 1

    update_response = client.patch(
        f"/indicators/{indicator['id']}",
        json={
            "name": "exchange_rate_usd_zmw",
            "value": 26.25,
            "unit": "ZMW",
            "source": "BOZ",
            "observed_at": "2026-05-14T08:00:00",
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["value"] == 26.25

    delete_response = client.delete(f"/indicators/{indicator['id']}")

    assert delete_response.status_code == 204

    assert client.get("/indicators").json() == []