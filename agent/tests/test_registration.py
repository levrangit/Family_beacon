from datetime import timedelta

import pytest

from agent.device_agent.registration import RegistrationCoordinator


def test_start_creates_temporary_registration_request() -> None:
    coordinator = RegistrationCoordinator(ttl_minutes=10)

    request = coordinator.start()

    assert coordinator.request == request
    assert len(request.registration_code) == 6
    assert request.registration_code.isalnum()
    assert request.expires_at - request.created_at == timedelta(minutes=10)
    assert request.request_id


def test_start_replaces_previous_request() -> None:
    coordinator = RegistrationCoordinator()

    first = coordinator.start()
    second = coordinator.start()

    assert first.request_id != second.request_id
    assert coordinator.request == second


def test_cancel_removes_active_request() -> None:
    coordinator = RegistrationCoordinator()
    coordinator.start()

    coordinator.cancel()

    assert coordinator.request is None


def test_invalid_ttl_is_rejected() -> None:
    with pytest.raises(ValueError, match="ttl_minutes"):
        RegistrationCoordinator(ttl_minutes=0)
