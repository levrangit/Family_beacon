"""API contract tests for Agent Installation endpoints."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_agent_installation_endpoint_exists():
    response = client.post(
        "/agent-installations",
        json={"telegram_id": 123456789},
    )

    assert response.status_code != 404


def test_create_agent_installation_requires_telegram_bot_authentication():
    response = client.post(
        "/agent-installations",
        json={"telegram_id": 123456789},
    )

    assert response.status_code == 401


def test_bootstrap_agent_installation_endpoint_exists():
    response = client.post(
        "/agent-installations/bootstrap",
        json={
            "installation_code": "ABC123",
            "agent_secret": "fb_agent_test",
            "platform": "windows",
            "device_id": "device-test-001",
        },
    )

    assert response.status_code != 404


def test_bootstrap_agent_installation_rejects_unsupported_platform():
    response = client.post(
        "/agent-installations/bootstrap",
        json={
            "installation_code": "ABC123",
            "agent_secret": "fb_agent_test",
            "platform": "android",
            "device_id": "device-test-001",
        },
    )

    assert response.status_code == 422
