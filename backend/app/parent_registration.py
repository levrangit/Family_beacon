from pydantic import BaseModel, EmailStr


class ParentRegistrationRequest(BaseModel):
    telegram_id: int
    login: EmailStr
    password: str
