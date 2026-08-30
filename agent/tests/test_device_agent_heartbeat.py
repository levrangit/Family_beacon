import pytest

from device_agent.api import DeviceAgentAPI


class FakeResponse:
    def __init__(self, status_code=200, payload=None, content=True):
        self.status_code = status_code
        self._payload = payload
        self.content = b"{}" if content else b""

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(
                f"HTTP {self.status_code}"
            )

    def json(self):
        return self._payload


def test_heartbeat_sends_post_with_device_token(monkeypatch):
    calls = []

    def fake_post(url, **kwargs):
        calls.append(
            {
                "url": url,
                "kwargs": kwargs,
            }
        )

        return FakeResponse(
            payload={
                "id": "device-001",
                "is_online": True,
            }
        )

    monkeypatch.setattr(
        "device_agent.api.requests.post",
        fake_post,
    )

    api = DeviceAgentAPI(
        backend_url="http://test-backend",
        device_token="test-device-token",
    )

    result = api.heartbeat()

    assert result == {
        "id": "device-001",
        "is_online": True,
    }

    assert calls == [
        {
            "url": "http://test-backend/device/heartbeat",
            "kwargs": {
                "headers": {
                    "Authorization": "Bearer test-device-token",
                    "Content-Type": "application/json",
                },
                "timeout": 10,
            },
        }
    ]


def test_heartbeat_raises_on_http_error(monkeypatch):
    def fake_post(url, **kwargs):
        return FakeResponse(status_code=500)

    monkeypatch.setattr(
        "device_agent.api.requests.post",
        fake_post,
    )

    api = DeviceAgentAPI(
        backend_url="http://test-backend",
        device_token="test-device-token",
    )

    with pytest.raises(RuntimeError, match="HTTP 500"):
        api.heartbeat()


def test_heartbeat_requires_device_token(monkeypatch):
    def fake_post(url, **kwargs):
        raise AssertionError(
            "HTTP request must not be sent"
        )

    monkeypatch.setattr(
        "device_agent.api.requests.post",
        fake_post,
    )

    api = DeviceAgentAPI(
        backend_url="http://test-backend",
        device_token="",
    )

    with pytest.raises(
        RuntimeError,
        match="Device token is not configured",
    ):
        api.heartbeat()
