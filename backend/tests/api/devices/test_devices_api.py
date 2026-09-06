import requests

from tests.support.auth.client import BASE_URL


def test_health():
    response = requests.get(
        f"{BASE_URL}/health",
        timeout=10,
    )

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_devices_requires_authentication():
    response = requests.get(
        f"{BASE_URL}/devices",
        timeout=10,
    )

    assert response.status_code == 401


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
