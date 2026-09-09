"""Unit tests for Device Agent Named Pipe server connection handling."""

from __future__ import annotations

from agent.device_agent.ipc.named_pipe_server import NamedPipeIPCServer
from agent.device_agent.ipc.protocol import MAX_MESSAGE_SIZE, decode_message, encode_message


class FakeConnection:
    def __init__(self, requests: list[dict[str, str]]) -> None:
        self._messages = [encode_message(request) for request in requests]
        self._messages.append(EOFError())
        self.responses: list[dict[str, str]] = []

    def recv_bytes(self, maxsize: int) -> bytes:
        assert maxsize == MAX_MESSAGE_SIZE
        message = self._messages.pop(0)
        if isinstance(message, EOFError):
            raise message
        return message

    def send_bytes(self, data: bytes) -> None:
        self.responses.append(decode_message(data))


def test_server_handles_multiple_requests_on_one_connection() -> None:
    requests = [
        {"type": "status"},
        {"type": "registration.start"},
        {"type": "registration.cancel"},
    ]
    connection = FakeConnection(requests)

    server = NamedPipeIPCServer.__new__(NamedPipeIPCServer)
    server._running = True
    server._handler = lambda request: {"ok": True, "type": request["type"]}

    server._serve_connection(connection)

    assert connection.responses == [
        {"ok": True, "type": "status"},
        {"ok": True, "type": "registration.start"},
        {"ok": True, "type": "registration.cancel"},
    ]
