"""Проверка RLS и текущего состояния Supabase таблиц."""
import os
import requests

SB = os.environ.get("SUPABASE_URL", "").rstrip("/")
SERVICE = os.environ.get("SUPABASE_SERVICE_KEY", "")
ANON = os.environ.get("SUPABASE_ANON_KEY", "")

if not SB or not SERVICE or not ANON:
    raise SystemExit(
        "ERROR: set SUPABASE_URL, SUPABASE_SERVICE_KEY, and SUPABASE_ANON_KEY "
        "in the environment. Never hardcode Supabase keys in source files."
    )

print("=== RLS check (anon key) ===")
for table in ("cars", "leads", "parts", "search_events"):
    r = requests.get(
        f"{SB}/rest/v1/{table}?limit=1",
        headers={"apikey": ANON, "Authorization": "Bearer " + ANON},
    )
    status = "OK READ" if r.status_code == 200 else f"BLOCKED ({r.status_code})"
    print(f"  {table}: {status}")

print()
print("=== Counts (service key) ===")
h = {"apikey": SERVICE, "Authorization": "Bearer " + SERVICE, "Prefer": "count=exact"}
for table in ("cars", "parts", "leads", "search_events"):
    r = requests.get(f"{SB}/rest/v1/{table}?select=id", headers=h)
    cnt = r.headers.get("Content-Range", "?").split("/")[-1]
    print(f"  {table}: {cnt}")

print()
print("=== Active cars by region ===")
for region in ("georgia", "europe"):
    r = requests.get(
        f"{SB}/rest/v1/cars?is_active=eq.true&region=eq.{region}&select=id",
        headers=h,
    )
    cnt = r.headers.get("Content-Range", "?").split("/")[-1]
    print(f"  {region}: {cnt} active")
