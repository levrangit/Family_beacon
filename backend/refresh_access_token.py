from pathlib import Path

import os
import re
import urllib.error
import urllib.request
import json

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parent
ENV_FILE = BACKEND_DIR / ".env"

load_dotenv(ENV_FILE)

supabase_url = os.getenv("SUPABASE_URL", "").strip()
email = os.getenv("TEST_EMAIL", "").strip()
password = os.getenv("TEST_PASSWORD", "").strip()

if not supabase_url:
    raise SystemExit("ERROR: SUPABASE_URL is missing")

if not email:
    raise SystemExit("ERROR: TEST_EMAIL is missing")

if not password:
    raise SystemExit("ERROR: TEST_PASSWORD is missing")

supabase_key = os.getenv("SUPABASE_KEY", "").strip()

if not supabase_key:
    raise SystemExit("ERROR: SUPABASE_KEY is missing")


url = f"{supabase_url.rstrip('/')}/auth/v1/token?grant_type=password"

payload = json.dumps({
    "email": email,
    "password": password,
}).encode("utf-8")

request = urllib.request.Request(
    url,
    data=payload,
    method="POST",
    headers={
        "apikey": supabase_key,
        "Content-Type": "application/json",
    },
)

try:
    with urllib.request.urlopen(request) as response:
        response_data = json.loads(response.read().decode("utf-8"))

except urllib.error.HTTPError as exc:
    body = exc.read().decode("utf-8", errors="replace")

    try:
        error_data = json.loads(body)
        message = (
            error_data.get("msg")
            or error_data.get("message")
            or error_data.get("error_description")
            or error_data.get("error")
            or "Authentication failed"
        )
    except json.JSONDecodeError:
        message = "Authentication failed"

    raise SystemExit(
        f"ERROR: Supabase login failed ({exc.code}): {message}"
    )

except Exception as exc:
    raise SystemExit(
        f"ERROR: Request failed: {exc}"
    )


access_token = response_data.get("access_token")

if not access_token:
    raise SystemExit(
        "ERROR: Supabase response does not contain access_token"
    )


env_text = ENV_FILE.read_text(encoding="utf-8")

new_line = f"ACCESS_TOKEN_JWT={access_token}"

pattern = r"(?m)^ACCESS_TOKEN_JWT=.*$"

if re.search(pattern, env_text):
    env_text = re.sub(
        pattern,
        new_line,
        env_text,
        count=1,
    )
else:
    if env_text and not env_text.endswith("\n"):
        env_text += "\n"

    env_text += new_line + "\n"


ENV_FILE.write_text(env_text, encoding="utf-8")

print("ACCESS_TOKEN_JWT updated successfully.")
print("EMAIL:", email)
print("TOKEN:", "SET")
print("TOKEN LENGTH:", len(access_token))
print("TOKEN PARTS:", access_token.count(".") + 1)
