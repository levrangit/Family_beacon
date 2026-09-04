import httpx
from supabase import Client, ClientOptions, create_client

from app.config import (
    SUPABASE_KEY,
    SUPABASE_SERVICE_ROLE_KEY,
    SUPABASE_URL,
)


SUPABASE_HTTP_TIMEOUT = 120.0

_httpx_client: httpx.Client | None = None
supabase: Client | None = None
supabase_admin: Client | None = None

if SUPABASE_URL and SUPABASE_KEY:
    _httpx_client = httpx.Client(
        timeout=httpx.Timeout(SUPABASE_HTTP_TIMEOUT),
    )
    _client_options = ClientOptions(
        httpx_client=_httpx_client,
    )
    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
        options=_client_options,
    )

if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
    if _httpx_client is None:
        _httpx_client = httpx.Client(
            timeout=httpx.Timeout(SUPABASE_HTTP_TIMEOUT),
        )

    supabase_admin = create_client(
        SUPABASE_URL,
        SUPABASE_SERVICE_ROLE_KEY,
        options=ClientOptions(
            httpx_client=_httpx_client,
        ),
    )


def get_user_client(access_token: str) -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("Supabase configuration is missing")

    if _httpx_client is None:
        raise RuntimeError("Supabase HTTP client is not initialized")

    client = create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
        options=ClientOptions(
            httpx_client=_httpx_client,
        ),
    )

    client.postgrest.auth(access_token)

    return client


def get_admin_client() -> Client:
    if supabase_admin is None:
        raise RuntimeError("Supabase service role configuration is missing")

    return supabase_admin


def close_http_client() -> None:
    if _httpx_client is not None:
        _httpx_client.close()
