from datetime import datetime, timedelta, timezone

import pytest

from app.device_registration import (
    CreateDeviceRegistrationRequest,
    DeviceRegistrationDevice,
    SubmitDeviceRegistrationCodeRequest,
    create_device_registration_request,
    submit_device_registration_code,
)


class FakeResponse:
    def __init__(self, data):
        self.data = data


class FakeTable:
    def __init__(self, database, name):
        self.database = database
        self.name = name
        self.filters = []
        self.payload = None

    def select(self, *_fields):
        return self

    def insert(self, payload):
        self.payload = payload
        return self

    def update(self, payload):
        self.payload = payload
        return self

    def eq(self, field, value):
        self.filters.append((field, value))
        return self

    def in_(self, field, values):
        self.filters.append((field, tuple(values)))
        return self

    def limit(self, _value):
        return self

    def execute(self):
        if self.name == "children":
            telegram_id = dict(self.filters).get("telegram_id")
            child = self.database.children.get(telegram_id)
            return FakeResponse([{"id": child}] if child else [])

        if self.name != "device_registration_requests":
            return FakeResponse([])

        if self.payload and "request_code_hash" in self.payload:
            request = dict(self.payload)
            request["id"] = "request-001"
            self.database.request = request
            return FakeResponse([request])

        request = self.database.request
        if request is None:
            return FakeResponse([])

        filter_map = dict(
            (field, value)
            for field, value in self.filters
            if field != "status" or not isinstance(value, tuple)
        )

        if "request_code_hash" in filter_map:
            if request["request_code_hash"] != filter_map["request_code_hash"]:
                return FakeResponse([])

        if "id" in filter_map and request["id"] != filter_map["id"]:
            return FakeResponse([])

        status_filter = [value for field, value in self.filters if field == "status"]
        if status_filter and status_filter[-1] != request["status"]:
            return FakeResponse([])

        if self.payload:
            for key, value in self.payload.items():
                request[key] = value
            return FakeResponse([request])

        return FakeResponse([request])


class FakeAdminClient:
    def __init__(self):
        self.children = {111: "child-a", 222: "child-b"}
        self.request = None

    def table(self, name):
        return FakeTable(self, name)


def test_create_request_does_not_require_child_id(monkeypatch):
    database = FakeAdminClient()
    monkeypatch.setattr("app.device_registration.get_admin_client", lambda: database)
    monkeypatch.setattr("app.device_registration.generate_code", lambda: "ABCD-2345")
    monkeypatch.setattr("app.device_registration.hash_code", lambda value: f"hash:{value}")

    result = create_device_registration_request(
        CreateDeviceRegistrationRequest(
            device=DeviceRegistrationDevice(
                platform="windows",
                device_id="device-001",
                hostname="WIN-001",
                agent_version="0.1.0",
            )
        )
    )

    assert result["status"] == "pending"
    assert result["registration_code"] == "ABCD-2345"
    assert database.request["child_id"] is None


def test_first_child_claims_registration_code(monkeypatch):
    database = FakeAdminClient()
    monkeypatch.setattr("app.device_registration.get_admin_client", lambda: database)
    monkeypatch.setattr("app.device_registration.hash_code", lambda value: f"hash:{value}")

    database.request = {
        "id": "request-001",
        "child_id": None,
        "request_code_hash": "hash:ABCD-2345",
        "status": "pending",
        "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(),
    }

    result = submit_device_registration_code(
        SubmitDeviceRegistrationCodeRequest(
            telegram_id=111,
            registration_code="ABCD-2345",
        )
    )

    assert result["request_id"] == "request-001"
    assert result["child_id"] == "child-a"
    assert result["status"] == "code_submitted"
    assert database.request["child_id"] == "child-a"


def test_second_child_gets_already_used_and_does_not_take_request(monkeypatch):
    database = FakeAdminClient()
    monkeypatch.setattr("app.device_registration.get_admin_client", lambda: database)
    monkeypatch.setattr("app.device_registration.hash_code", lambda value: f"hash:{value}")

    database.request = {
        "id": "request-001",
        "child_id": "child-a",
        "request_code_hash": "hash:ABCD-2345",
        "status": "code_submitted",
        "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(),
    }

    with pytest.raises(Exception) as exc_info:
        submit_device_registration_code(
            SubmitDeviceRegistrationCodeRequest(
                telegram_id=222,
                registration_code="ABCD-2345",
            )
        )

    assert getattr(exc_info.value, "status_code", None) == 409
    assert getattr(exc_info.value, "detail", None) == "Device registration code is already used"
    assert database.request["child_id"] == "child-a"
    assert database.request["status"] == "code_submitted"


def test_concurrent_loser_is_treated_as_already_used(monkeypatch):
    database = FakeAdminClient()
    monkeypatch.setattr("app.device_registration.get_admin_client", lambda: database)
    monkeypatch.setattr("app.device_registration.hash_code", lambda value: f"hash:{value}")

    database.request = {
        "id": "request-001",
        "child_id": None,
        "request_code_hash": "hash:ABCD-2345",
        "status": "pending",
        "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(),
    }

    winner = submit_device_registration_code(
        SubmitDeviceRegistrationCodeRequest(
            telegram_id=111,
            registration_code="ABCD-2345",
        )
    )

    assert winner["child_id"] == "child-a"

    with pytest.raises(Exception) as exc_info:
        submit_device_registration_code(
            SubmitDeviceRegistrationCodeRequest(
                telegram_id=222,
                registration_code="ABCD-2345",
            )
        )

    assert getattr(exc_info.value, "status_code", None) == 409
    assert database.request["child_id"] == "child-a"
    assert database.request["status"] == "code_submitted"
