from supabase import Client, create_client

from app.config import SUPABASE_KEY, SUPABASE_URL


supabase: Client | None = None

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
    )


def get_user_client(access_token: str) -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("Supabase configuration is missing")

    client = create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
    )

    client.postgrest.auth(access_token)

    return client
