#!/usr/bin/env python3
import os
import requests
import json

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    try:
        from import_to_supabase import SUPABASE_URL, SUPABASE_SERVICE_KEY
    except:
        print("ERROR: Supabase credentials not found")
        exit(1)

# Check how many parts are in the database
headers = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
}

# Count all parts
url = f"{SUPABASE_URL}/rest/v1/parts?select=count()"
try:
    resp = requests.get(url, headers=headers, timeout=10)
    if resp.status_code == 200:
        count_header = resp.headers.get('content-range', '0-0/0')
        print(f"Count header: {count_header}")
        if '/' in count_header:
            total = int(count_header.split('/')[-1])
            print(f"✓ Total parts in Supabase: {total:,}")
        else:
            print(f"Total rows response: {resp.text}")
    else:
        print(f"Error: Status {resp.status_code}")
        print(resp.text)
except Exception as e:
    print(f"Error checking count: {e}")

# Check sample parts with OEM
url2 = f"{SUPABASE_URL}/rest/v1/parts?oem_number=not.is.null&limit=5"
try:
    resp2 = requests.get(url2, headers=headers, timeout=10)
    if resp2.status_code == 200:
        parts = resp2.json()
        print(f"\n✓ Sample parts with OEM (first 5):")
        for i, part in enumerate(parts[:3], 1):
            print(f"  {i}. {part.get('name', 'N/A')[:40]} - OEM: {part.get('oem_number', 'N/A')}")
    else:
        print(f"Error fetching parts: {resp2.status_code}")
except Exception as e:
    print(f"Error fetching sample: {e}")
