import httpx
from supabase import Client, ClientOptions, create_client

from app.config import SUPABASE_KEY, SUPABASE_URL


SUPABASE_HTTP_TIMEOUT = 120.0

_httpx_client: httpx.Client | None = None
supabase: Client | None = None

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


def close_http_client() -> None:
    if _httpx_client is not None:
        _httpx_client.close()
