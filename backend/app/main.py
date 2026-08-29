from fastapi import FastAPI

from app.supabase_client import supabase


app = FastAPI(
    title="Family Beacon API",
    version="0.1.0",
)


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
