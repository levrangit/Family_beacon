from typing import Any

from pydantic import BaseModel, EmailStr


class ParentRegistrationRequest(BaseModel):
    telegram_id: int
    login: EmailStr
    password: str


def register_parent(
    supabase_client: Any,
    request: ParentRegistrationRequest,
) -> dict[str, str]:
    response = supabase_client.auth.sign_up(
        {
            "email": str(request.login),
            "password": request.password,
            "options": {
                "data": {
                    "telegram_id": request.telegram_id,
                }
            },
        }
    )

    if response.user is None:
        raise ValueError("Supabase did not return a user")

    if response.session is None:
        raise ValueError("Supabase did not return a session")

    return {
        "user_id": str(response.user.id),
        "access_token": str(response.session.access_token),
    }
