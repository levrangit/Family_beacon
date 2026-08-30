import os
from datetime import date

import requests


BASE_URL = os.getenv("FAMILY_BEACON_API_URL", "http://127.0.0.1:8000")
ACCESS_TOKEN = os.getenv("SUPABASE_ACCESS_TOKEN")


CHILD_ID = "2b0b5aaa-7654-4b06-b5f4-9d56abd3ee3d"
DEVICE_ID = "54839e05-e368-4dbc-8fd6-417b440bc983"


def auth_headers():
    if not ACCESS_TOKEN:
        raise RuntimeError(
            "SUPABASE_ACCESS_TOKEN is not set. "
            "Set it locally before running this test."
        )

    return {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }


def test_time_usage_requires_authentication():
    response = requests.get(
        f"{BASE_URL}/time-usage",
        timeout=10,
    )

    assert response.status_code == 401


def test_time_usage_can_be_listed():
    response = requests.get(
        f"{BASE_URL}/time-usage",
        headers=auth_headers(),
        timeout=10,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_time_usage_can_be_filtered_by_child_and_date():
    usage_date = date.today().isoformat()

    response = requests.get(
        f"{BASE_URL}/time-usage",
        params={
            "child_id": CHILD_ID,
            "usage_date": usage_date,
        },
        headers=auth_headers(),
        timeout=10,
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    for item in data:
        assert item["child_id"] == CHILD_ID
        assert item["usage_date"] == usage_date
        assert item["used_minutes"] >= 0


def test_time_usage_rejects_negative_minutes():
    response = requests.post(
        f"{BASE_URL}/devices/{DEVICE_ID}/usage",
        headers=auth_headers(),
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
