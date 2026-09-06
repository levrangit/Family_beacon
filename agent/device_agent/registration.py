"""Registration request primitives for the Device Agent.

This module owns the local Agent-side registration lifecycle only. The
persistent Registration Request and its authoritative temporary code will be
moved behind a Backend client when the backend contract is implemented.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import secrets
import string


_CODE_ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"


@dataclass(frozen=True)
class RegistrationRequest:
    """Temporary local representation of a registration attempt."""

    request_id: str
    registration_code: str
    created_at: datetime
    expires_at: datetime

    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.expires_at


class RegistrationCoordinator:
    """Create and track one temporary registration attempt per Agent."""

    def __init__(self, *, ttl_minutes: int = 10) -> None:
        if ttl_minutes <= 0:
            raise ValueError("ttl_minutes must be positive")
        self._ttl = timedelta(minutes=ttl_minutes)
        self._request: RegistrationRequest | None = None

    @property
    def request(self) -> RegistrationRequest | None:
        """Return the active request, if any and not expired."""
        request = self._request
        if request is None:
            return None
        if request.is_expired:
            self._request = None
            return None
        return request

    def start(self) -> RegistrationRequest:
        """Start a new temporary registration attempt."""
        now = datetime.now(timezone.utc)
        request = RegistrationRequest(
            request_id=secrets.token_urlsafe(18),
            registration_code=self._generate_code(),
            created_at=now,
            expires_at=now + self._ttl,
        )
        self._request = request
        return request

    def cancel(self) -> None:
        """Cancel the active local registration attempt."""
        self._request = None

    @staticmethod
    def _generate_code(length: int = 6) -> str:
        return "".join(secrets.choice(_CODE_ALPHABET) for _ in range(length))
