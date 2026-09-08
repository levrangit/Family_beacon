"""RED API contract tests for Device Registration Workflow v1.

These tests intentionally describe endpoints that are not implemented yet.
They must turn green only when the Backend exposes the central workflow API.
"""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_device_registration_create_request_endpoint_exists():
    response = client.post(
        "/device-registration/requests",
        json={
            "child_id": "00000000-0000-0000-0000-000000000001",
            "registration_code": "ABC123",
            "device": {
                "platform": "windows",
                "device_id": "device-test-001",
                "hostname": "WIN-TEST",
                "agent_version": "0.1.0",
            },
        },
    )

    assert response.status_code != 404


def test_device_registration_parent_approval_endpoint_exists():
    response = client.post(
        "/device-registration/requests/00000000-0000-0000-0000-000000000001/approve"
    )

    assert response.status_code != 404


def test_device_registration_parent_rejection_endpoint_exists():
    response = client.post(
        "/device-registration/requests/00000000-0000-0000-0000-000000000001/reject"
    )

    assert response.status_code != 404


def test_device_registration_request_status_endpoint_exists():
    response = client.get(
        "/device-registration/requests/00000000-0000-0000-0000-000000000001"
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
