from dataclasses import dataclass


@dataclass
class RegistrationSession:
    telegram_id: int
    role: str | None = None
    state: str | None = None
    login: str | None = None

    def start_parent_registration(self) -> None:
        self.role = "parent"
        self.state = "waiting_login"

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
