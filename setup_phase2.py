"""
Phase 2 setup script:
1. Fix RLS on leads / search_events (remove any SELECT for anon)
2. Add notified_at column to leads
3. Add TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID to GitHub Secrets
"""
import os
import sys
import base64
import json
import requests

# ── Config ────────────────────────────────────────────────────────────────────
# All secrets must be set as environment variables before running this script.
# Example (PowerShell):
#   $env:SUPABASE_URL         = "https://xxx.supabase.co"
#   $env:SUPABASE_SERVICE_KEY = "eyJ..."
#   $env:SB_PAT               = "sbp_..."
#   $env:SB_PROJECT_REF       = "jolyujjfxzhkswflqodz"
#   $env:GITHUB_TOKEN         = "ghp_..."
#   $env:GITHUB_OWNER         = "jfsagro-glitch"
#   $env:GITHUB_REPO          = "carshop-website"
#   $env:TG_BOT_TOKEN         = "123456:..."
#   $env:TG_CHAT_ID           = "408817675"

SUPABASE_URL    = os.environ["SUPABASE_URL"]
SB_SERVICE_KEY  = os.environ["SUPABASE_SERVICE_KEY"]
SB_PAT          = os.environ["SB_PAT"]
PROJECT_REF     = os.environ.get("SB_PROJECT_REF", "jolyujjfxzhkswflqodz")

GITHUB_TOKEN    = os.environ["GITHUB_TOKEN"]
GITHUB_OWNER    = os.environ.get("GITHUB_OWNER", "jfsagro-glitch")
GITHUB_REPO     = os.environ.get("GITHUB_REPO", "carshop-website")

TG_BOT_TOKEN    = os.environ["TG_BOT_TOKEN"]
TG_CHAT_ID      = os.environ["TG_CHAT_ID"]

# ── Helper: run SQL via Supabase Management API ───────────────────────────────
def run_sql(sql: str, label: str = "SQL") -> bool:
    url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
    r = requests.post(
        url,
        headers={"Authorization": f"Bearer {SB_PAT}", "Content-Type": "application/json"},
        json={"query": sql},
        timeout=30,
    )
    if r.status_code in (200, 201):
        print(f"  ✓ {label}")
        return True
    else:
        print(f"  ✗ {label}: {r.status_code} {r.text[:200]}")
        return False


# ── Step 1: Fix RLS ───────────────────────────────────────────────────────────
def fix_rls():
    print("\n=== Step 1: Fix RLS ===")
    sql = """
-- Remove any existing SELECT policies on leads (anon should only INSERT)
DO $$
DECLARE
    pol record;
BEGIN
    FOR pol IN
        SELECT policyname
        FROM pg_policies
        WHERE tablename = 'leads'
          AND cmd = 'SELECT'
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON leads', pol.policyname);
    END LOOP;
END$$;

-- Remove any existing SELECT policies on search_events
DO $$
DECLARE
    pol record;
BEGIN
    FOR pol IN
        SELECT policyname
        FROM pg_policies
        WHERE tablename = 'search_events'
          AND cmd = 'SELECT'
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON search_events', pol.policyname);
    END LOOP;
END$$;

-- Ensure only INSERT is allowed for anon on leads
DROP POLICY IF EXISTS "public_insert_leads" ON leads;
CREATE POLICY "public_insert_leads"
  ON leads FOR INSERT
  TO anon
  WITH CHECK (true);

-- Ensure only INSERT is allowed for anon on search_events
DROP POLICY IF EXISTS "public_insert_search_events" ON search_events;
CREATE POLICY "public_insert_search_events"
  ON search_events FOR INSERT
  TO anon
  WITH CHECK (true);
"""
    return run_sql(sql, "Fix RLS: leads + search_events SELECT removed")


# ── Step 2: Add notified_at column to leads ───────────────────────────────────
def add_notified_at():
    print("\n=== Step 2: Add notified_at to leads ===")
    sql = """
ALTER TABLE leads ADD COLUMN IF NOT EXISTS notified_at timestamptz DEFAULT NULL;
CREATE INDEX IF NOT EXISTS idx_leads_notified ON leads(notified_at) WHERE notified_at IS NULL;
"""
    return run_sql(sql, "Add notified_at column + index")


# ── Step 3: GitHub Secrets ────────────────────────────────────────────────────
def _get_repo_public_key():
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/secrets/public-key"
    r = requests.get(
        url,
        headers={"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"},
        timeout=15,
    )
    if r.status_code == 200:
        return r.json()
    else:
        print(f"  ✗ get public key: {r.status_code} {r.text[:200]}")
        return None


def _encrypt_secret(public_key_b64: str, secret_value: str) -> str:
    try:
        from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PublicKey
        from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
        import secrets as _secrets

        pub_key_bytes = base64.b64decode(public_key_b64)
        # Use PyNaCl-style sealed box via cryptography library
        # Generate ephemeral key pair
        eph_private = X25519PrivateKey.generate()
        eph_public_bytes = eph_private.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        shared_key = eph_private.exchange(
            X25519PublicKey.from_public_bytes(pub_key_bytes)
        )
        # key derivation + encryption via libsodium sealed box would need PyNaCl
        # Fall back to PyNaCl below
        raise ImportError("use pynacl")
    except Exception:
        pass

    try:
        from nacl import encoding, public
        pub_key = public.PublicKey(public_key_b64.encode("utf-8"), encoding.Base64Encoder())
        sealed_box = public.SealedBox(pub_key)
        encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
        return base64.b64encode(encrypted).decode("utf-8")
    except ImportError:
        # If PyNaCl unavailable — GitHub also accepts plaintext via their API
        # but only for orgs with GHES. For repos, encryption is required.
        # Try installing PyNaCl quickly
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyNaCl", "-q"])
        from nacl import encoding, public
        pub_key = public.PublicKey(public_key_b64.encode("utf-8"), encoding.Base64Encoder())
        sealed_box = public.SealedBox(pub_key)
        encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
        return base64.b64encode(encrypted).decode("utf-8")


def set_github_secret(secret_name: str, secret_value: str, key_id: str, pub_key_b64: str) -> bool:
    encrypted = _encrypt_secret(pub_key_b64, secret_value)
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/secrets/{secret_name}"
    r = requests.put(
        url,
        headers={"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"},
        json={"encrypted_value": encrypted, "key_id": key_id},
        timeout=15,
    )
    if r.status_code in (201, 204):
        print(f"  ✓ GitHub secret {secret_name} set")
        return True
    else:
        print(f"  ✗ GitHub secret {secret_name}: {r.status_code} {r.text[:200]}")
        return False


def setup_github_secrets():
    print("\n=== Step 3: GitHub Secrets for Telegram ===")
    key_info = _get_repo_public_key()
    if not key_info:
        return False
    key_id = key_info["key_id"]
    pub_key = key_info["key"]

    ok = True
    ok &= set_github_secret("TELEGRAM_BOT_TOKEN", TG_BOT_TOKEN, key_id, pub_key)
    ok &= set_github_secret("TELEGRAM_CHAT_ID",   TG_CHAT_ID,   key_id, pub_key)
    return ok


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    results = []
    results.append(("Fix RLS",             fix_rls()))
    results.append(("Add notified_at",     add_notified_at()))
    results.append(("GitHub TG secrets",   setup_github_secrets()))

    print("\n=== Summary ===")
    for label, ok in results:
        print(f"  {'✓' if ok else '✗'} {label}")

    if all(ok for _, ok in results):
        print("\nAll done. Proceed to create notify_leads.py and update workflow.")
        sys.exit(0)
    else:
        sys.exit(1)
