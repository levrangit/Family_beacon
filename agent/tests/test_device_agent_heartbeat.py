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


def test_heartbeat_sends_post_with_device_token_and_agent_version(monkeypatch):
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
                "agent_version": "0.3.1",
                "is_online": True,
                "update_status": "idle",
                "target_agent_version": None,
            }
        )

    monkeypatch.setattr(
        "device_agent.api.requests.post",
        fake_post,
    )

    api = DeviceAgentAPI(
        backend_url="http://test-backend",
        device_token="test-device-token",
        agent_version="0.3.1",
    )

    result = api.heartbeat()

    assert result == {
        "id": "device-001",
        "agent_version": "0.3.1",
        "is_online": True,
        "update_status": "idle",
        "target_agent_version": None,
    }

    assert calls == [
        {
            "url": "http://test-backend/device/heartbeat",
            "kwargs": {
                "headers": {
                    "Authorization": "Bearer test-device-token",
                    "Content-Type": "application/json",
                },
                "json": {
                    "agent_version": "0.3.1",
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
        agent_version="0.3.1",
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
        agent_version="0.3.1",
    )

    with pytest.raises(
        RuntimeError,
        match="Device token is not configured",
    ):
        api.heartbeat()


def test_heartbeat_requires_agent_version(monkeypatch):
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
        device_token="test-device-token",
        agent_version="",
    )

    with pytest.raises(
        RuntimeError,
        match="Agent version is not configured",
    ):
        api.heartbeat()
