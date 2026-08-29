import os

from dotenv import load_dotenv
from fastapi import FastAPI
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

app = FastAPI(
    title="Family Beacon API",
    version="0.1.0",
)

supabase: Client | None = None

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/supabase-check")
async def supabase_check() -> dict[str, bool | str]:
    if supabase is None:
        return {
            "connected": False,
            "error": "Supabase configuration is missing",
        }

    try:
        response = supabase.rpc("health_check").execute()

        return {
            "connected": True,
            "query_ok": response.data is not None,
        }

    except Exception as exc:
        return {
            "connected": False,
            "error": str(exc),
        }
