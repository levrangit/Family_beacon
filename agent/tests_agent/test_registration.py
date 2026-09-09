from datetime import datetime, timedelta, timezone

import pytest

from agent.device_agent.registration import RegistrationCoordinator


def test_set_request_stores_backend_issued_registration_request() -> None:
    coordinator = RegistrationCoordinator()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    request = coordinator.set_request(
        request_id="request-001",
        registration_code="ABCD-2345",
        expires_at=expires_at,
    )

    assert coordinator.request == request
    assert request.request_id == "request-001"
    assert request.registration_code == "ABCD-2345"
    assert request.expires_at == expires_at


def test_set_request_replaces_previous_request() -> None:
    coordinator = RegistrationCoordinator()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    first = coordinator.set_request(
        request_id="request-001",
        registration_code="ABCD-2345",
        expires_at=expires_at,
    )
    second = coordinator.set_request(
        request_id="request-002",
        registration_code="EFGH-6789",
        expires_at=expires_at,
    )

    assert first.request_id != second.request_id
    assert coordinator.request == second


def test_cancel_removes_active_request() -> None:
    coordinator = RegistrationCoordinator()
    coordinator.set_request(
        request_id="request-001",
        registration_code="ABCD-2345",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    coordinator.cancel()

    assert coordinator.request is None


def test_set_request_requires_timezone_aware_expiry() -> None:
    coordinator = RegistrationCoordinator()

    with pytest.raises(ValueError, match="timezone-aware"):
        coordinator.set_request(
            request_id="request-001",
            registration_code="ABCD-2345",
            expires_at=datetime.now(),
        )
