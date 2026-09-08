"""Registration request state for the Device Agent."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class RegistrationRequest:
    """Backend-issued registration request held locally by the Agent."""

    request_id: str
    registration_code: str
    created_at: datetime
    expires_at: datetime

    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.expires_at


class RegistrationCoordinator:
    """Track the single Backend-authoritative registration attempt for an Agent."""

    def __init__(self) -> None:
        self._request: RegistrationRequest | None = None

    @property
    def request(self) -> RegistrationRequest | None:
        """Return the active Backend-issued request, if it has not expired."""
        request = self._request
        if request is None:
            return None
        if request.is_expired:
            self._request = None
            return None
        return request

    def set_request(
        self,
        *,
        request_id: str,
        registration_code: str,
        expires_at: datetime,
        created_at: datetime | None = None,
    ) -> RegistrationRequest:
        """Store a registration request returned by the Backend."""
        if not request_id:
            raise ValueError("request_id is required")
        if not registration_code:
            raise ValueError("registration_code is required")
        if expires_at.tzinfo is None:
            raise ValueError("expires_at must be timezone-aware")

        request = RegistrationRequest(
            request_id=request_id,
            registration_code=registration_code,
            created_at=created_at or datetime.now(timezone.utc),
            expires_at=expires_at,
        )
        self._request = request
        return request

    def cancel(self) -> None:
        """Forget the local registration request."""
        self._request = None
