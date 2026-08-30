import os

import requests


BASE_URL = os.getenv("FAMILY_BEACON_API_URL", "http://127.0.0.1:8000")
ACCESS_TOKEN = os.getenv("SUPABASE_ACCESS_TOKEN")


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


def test_health():
    response = requests.get(f"{BASE_URL}/health", timeout=10)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_devices_requires_authentication():
    response = requests.get(f"{BASE_URL}/devices", timeout=10)

    assert response.status_code == 401


if __name__ == "__main__":
    test_health()
    test_devices_requires_authentication()

    print("DEVICES API BASIC TESTS OK")


def test_device_status_without_last_seen():
    from app.devices import get_device_status

    assert get_device_status(None) == "offline"


def test_device_status_recent_last_seen():
    from datetime import datetime, timezone

    from app.devices import get_device_status

    last_seen = datetime.now(timezone.utc).isoformat()

    assert get_device_status(last_seen) == "online"


def test_device_status_old_last_seen():
    from datetime import datetime, timedelta, timezone

    from app.devices import get_device_status

    last_seen = (
        datetime.now(timezone.utc) - timedelta(minutes=3)
    ).isoformat()

    assert get_device_status(last_seen) == "offline"
