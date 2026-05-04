"""Проверка RLS и текущего состояния Supabase таблиц."""
import requests

SB = "https://jolyujjfxzhkswflqodz.supabase.co"
SERVICE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpvbHl1ampmeHpoa3N3Zmxxb2R6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3Nzg0NDU2MSwiZXhwIjoyMDkzNDIwNTYxfQ.Ex7h9hdsXba1fWcoqx3CSlImdrXTw7IVn5bsFsAM1j8"
ANON = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpvbHl1ampmeHpoa3N3Zmxxb2R6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc4NDQ1NjEsImV4cCI6MjA5MzQyMDU2MX0.LJt1YGmO2REOhSdoFAk_liWJiD9RjtR6zkmrDITTT-E"

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
