import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from supabase import create_client


BACKEND_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BACKEND_DIR / ".env"

load_dotenv(ENV_FILE)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BASE_URL = os.getenv(
    "FAMILY_BEACON_API_URL",
    "http://127.0.0.1:8000",
)


class AuthTestClient:
    def __init__(self, user):
        self.user = user
        self.session = requests.Session()

        if not SUPABASE_URL:
            raise RuntimeError("SUPABASE_URL is not set")

        if not SUPABASE_KEY:
            raise RuntimeError("SUPABASE_KEY is not set")

        self._access_token = self._authenticate()

    def _authenticate(self) -> str:
        try:
            supabase = create_client(
                SUPABASE_URL,
                SUPABASE_KEY,
            )

            response = supabase.auth.sign_in_with_password(
                {
                    "email": self.user.email,
                    "password": self.user.password,
                }
            )

            if not response.session:
                raise RuntimeError("Test authentication did not return a session")

            if not response.session.access_token:
                raise RuntimeError("Test authentication did not return an access token")

            return response.session.access_token

        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError("Test authentication failed") from exc

    @property
    def access_token(self) -> str:
        return self._access_token

    @property
    def base_url(self) -> str:
        return BASE_URL

    def _headers(self, extra_headers=None):
        headers = {
            "Authorization": f"Bearer {self._access_token}",
        }

        if extra_headers:
            headers.update(extra_headers)

        return headers

    def get(self, path, **kwargs):
        headers = kwargs.pop("headers", None)
        return self.session.get(
            f"{BASE_URL}{path}",
            headers=self._headers(headers),
            **kwargs,
        )

    def post(self, path, **kwargs):
        headers = kwargs.pop("headers", None)
        return self.session.post(
            f"{BASE_URL}{path}",
            headers=self._headers(headers),
            **kwargs,
        )

    def put(self, path, **kwargs):
        headers = kwargs.pop("headers", None)
        return self.session.put(
            f"{BASE_URL}{path}",
            headers=self._headers(headers),
            **kwargs,
        )

    def patch(self, path, **kwargs):
        headers = kwargs.pop("headers", None)
        return self.session.patch(
            f"{BASE_URL}{path}",
            headers=self._headers(headers),
            **kwargs,
        )

    def delete(self, path, **kwargs):
        headers = kwargs.pop("headers", None)
        return self.session.delete(
            f"{BASE_URL}{path}",
            headers=self._headers(headers),
            **kwargs,
        )

    def close(self):
        self.session.close()
