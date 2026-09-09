from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from app import agent_installation


class FakeResponse:
    def __init__(self, data):
        self.data = data


class FakeQuery:
    def __init__(self, tables, table_name):
        self.tables = tables
        self.table_name = table_name
        self.filters = []
        self.payload = None

    def select(self, *_fields):
        return self

    def eq(self, field, value):
        self.filters.append((field, value))
        return self

    def order(self, *_args, **_kwargs):
        return self

    def limit(self, *_args):
        return self

    def insert(self, payload):
        self.payload = payload
        return self

    def update(self, payload):
        self.payload = payload
        return self

    def execute(self):
        rows = self.tables.setdefault(self.table_name, [])
        if self.payload is not None:
            if all(
                row.get(field) == value
                for row in rows
                for field, value in self.filters
            ) if rows else True:
                if self.payload.get("status") == "claimed":
                    for row in rows:
                        if all(row.get(field) == value for field, value in self.filters):
                            row.update(self.payload)
                            return FakeResponse([row])
                if "installation_code_hash" in self.payload:
                    row = {"id": "installation-1", **self.payload}
                    rows.append(row)
                    return FakeResponse([row])
        result = [
            row for row in rows
            if all(row.get(field) == value for field, value in self.filters)
        ]
        return FakeResponse(result)


class FakeClient:
    def __init__(self):
        self.tables = {
            "profiles": [
                {
                    "id": "parent-1",
                    "telegram_id": 123,
                    "role": "parent",
                    "is_active": True,
                }
            ],
            "family_members": [
                {
                    "profile_id": "parent-1",
                    "member_type": "parent",
                    "family_id": "family-1",
                }
            ],
            "agent_installations": [],
        }

    def table(self, name):
        return FakeQuery(self.tables, name)


def test_generate_agent_secret_is_unique_and_prefixed():
    first = agent_installation.generate_agent_secret()
    second = agent_installation.generate_agent_secret()

    assert first.startswith(agent_installation.AGENT_SECRET_PREFIX)
    assert second.startswith(agent_installation.AGENT_SECRET_PREFIX)
    assert first != second


def test_parent_can_create_installation(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(agent_installation, "get_admin_client", lambda: client)

    result = agent_installation.create_agent_installation(
        agent_installation.CreateAgentInstallationRequest(telegram_id=123)
    )

    assert result["installation_code"]
    assert result["status"] == "pending"
    assert result["installation_id"] == "installation-1"
    assert client.tables["agent_installations"][0]["family_id"] == "family-1"


def test_first_agent_claims_installation_and_second_is_rejected(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(agent_installation, "get_admin_client", lambda: client)

    created = agent_installation.create_agent_installation(
        agent_installation.CreateAgentInstallationRequest(telegram_id=123)
    )
    code = created["installation_code"]

    first = agent_installation.bootstrap_agent_installation(
        agent_installation.BootstrapAgentInstallationRequest(
            installation_code=code,
            agent_secret=agent_installation.generate_agent_secret(),
            platform="windows",
            device_id="device-1",
        )
    )
    assert first["status"] == "claimed"

    with pytest.raises(HTTPException) as exc_info:
        agent_installation.bootstrap_agent_installation(
            agent_installation.BootstrapAgentInstallationRequest(
                installation_code=code,
                agent_secret=agent_installation.generate_agent_secret(),
                platform="windows",
                device_id="device-2",
            )
        )

    assert exc_info.value.status_code == 409
    assert client.tables["agent_installations"][0]["device_id"] == "device-1"
