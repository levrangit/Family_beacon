from dataclasses import dataclass


@dataclass
class RegistrationSession:
    telegram_id: int
    role: str | None = None
    state: str | None = None
    login: str | None = None
    invite_code: str | None = None
    child_name: str | None = None

    def start_parent_registration(self) -> None:
        self.role = "parent"
        self.state = "waiting_login"

    def start_child_registration(self) -> None:
        self.role = "child"
        self.state = "waiting_invite_code"

    def complete_parent_registration(self, password: str) -> dict[str, str | int]:
        if not self.login:
            raise ValueError("Login is required")

        if not password.strip():
            raise ValueError("Password is required")

        self.state = "completed"

        return {
            "telegram_id": self.telegram_id,
            "login": self.login,
            "password": password,
        }

    def set_login(self, login: str) -> None:
        if not login.strip():
            raise ValueError("Login is required")

        self.login = login
        self.state = "waiting_password"

    def set_invite_code(self, invite_code: str) -> None:
        normalized_code = invite_code.strip().upper()
        if not normalized_code:
            raise ValueError("Invite code is required")

        self.invite_code = normalized_code
        self.state = "waiting_child_name"

    def complete_child_registration(self, child_name: str) -> dict[str, str | int]:
        if not self.invite_code:
            raise ValueError("Invite code is required")

        if not child_name.strip():
            raise ValueError("Child name is required")

        self.child_name = child_name.strip()
        self.state = "completed"

        return {
            "telegram_id": self.telegram_id,
            "invite_code": self.invite_code,
            "child_name": self.child_name,
        }
