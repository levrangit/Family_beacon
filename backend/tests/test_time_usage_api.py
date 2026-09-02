from datetime import date

import requests


CHILD_ID = "2b0b5aaa-7654-4b06-b5f4-9d56abd3ee3d"
DEVICE_ID = "54839e05-e368-4dbc-8fd6-417b440bc983"


def test_time_usage_requires_authentication(parent_client):
    response = requests.get(
        f"{parent_client.base_url}/time-usage",
        timeout=10,
    )

    assert response.status_code == 401


def test_time_usage_can_be_listed(parent_client):
    response = parent_client.get(
        "/time-usage",
        timeout=10,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_time_usage_can_be_filtered_by_child_and_date(parent_client):
    usage_date = date.today().isoformat()

    response = parent_client.get(
        "/time-usage",
        params={
            "child_id": CHILD_ID,
            "usage_date": usage_date,
        },
        timeout=10,
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    for item in data:
        assert item["child_id"] == CHILD_ID
        assert item["usage_date"] == usage_date
        assert item["used_minutes"] >= 0


def test_time_usage_rejects_negative_minutes(parent_client):
    response = parent_client.post(
        f"/devices/{DEVICE_ID}/usage",
        json={
            "child_id": CHILD_ID,
            "usage_date": date.today().isoformat(),
            "additional_minutes": -1,
        },
        timeout=10,
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Usage minutes cannot be negative"
    }
