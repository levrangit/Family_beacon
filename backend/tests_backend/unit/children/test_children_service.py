from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.children import CreateChildRequest, create_child, list_children


def _client(data=None, error=None):
    client = MagicMock()
    response = MagicMock()
    response.data = data
    if error:
        client.table.return_value.insert.return_value.execute.side_effect = error
    else:
        client.table.return_value.insert.return_value.execute.return_value = response
        client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = response
    return client


def test_create_child_returns_inserted_child(monkeypatch):
    client = _client([{"id": "child-1", "family_id": "family-1", "name": "Alice"}])
    monkeypatch.setattr("app.children.get_user_client", lambda token: client)

    result = create_child("token", "family-1", CreateChildRequest(name="Alice"))

    assert result["id"] == "child-1"
    client.table.assert_called_with("children")


def test_create_child_maps_rls_to_403(monkeypatch):
    client = _client(error=RuntimeError("new row violates row-level security policy"))
    monkeypatch.setattr("app.children.get_user_client", lambda token: client)

    with pytest.raises(HTTPException) as exc:
        create_child("token", "family-1", CreateChildRequest(name="Alice"))

    assert exc.value.status_code == 403


def test_create_child_maps_empty_result_to_500(monkeypatch):
    client = _client([])
    monkeypatch.setattr("app.children.get_user_client", lambda token: client)

    with pytest.raises(HTTPException) as exc:
        create_child("token", "family-1", CreateChildRequest(name="Alice"))

    assert exc.value.status_code == 500
    assert exc.value.detail == "Failed to create child"


def test_list_children_returns_children(monkeypatch):
    data = [{"id": "child-1", "family_id": "family-1", "name": "Alice"}]
    client = _client(data)
    monkeypatch.setattr("app.children.get_user_client", lambda token: client)

    result = list_children("token", "family-1")

    assert result == data
    client.table.return_value.select.return_value.eq.assert_called_once_with("family_id", "family-1")
