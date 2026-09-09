"""API contract tests for the currently implemented Device Registration Workflow v1 slice."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_device_registration_create_request_endpoint_exists():
    response = client.post(
        "/device-registration/requests",
        json={
            "device": {
                "platform": "windows",
                "device_id": "device-test-001",
                "hostname": "WIN-TEST",
                "agent_version": "0.1.0",
            },
        },
    )

    assert response.status_code != 404


def test_device_registration_submit_code_endpoint_exists():
    response = client.post(
        "/device-registration/submit-code",
        json={
            "telegram_id": 123456789,
            "registration_code": "ABC123",
        },
    )

    assert response.status_code != 404
