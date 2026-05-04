#!/usr/bin/env python3
"""
cleanup_cars.py — Авто-очистка устаревших записей авто из Supabase.

Алгоритм:
  1. PATCH cars WHERE last_seen < NOW() - INTERVAL '30 days'
               AND is_active = true
     → is_active = false   (пометить как неактивные)

  2. DELETE cars WHERE is_active = false
              AND updated_at < NOW() - INTERVAL '60 days'
     (физическое удаление очень старых неактивных записей)

Безопасно: ничего не делает если SUPABASE_URL / SUPABASE_SERVICE_KEY не заданы.

Запуск:
    python cleanup_cars.py
    python cleanup_cars.py --dry-run
    SUPABASE_URL=https://... SUPABASE_SERVICE_KEY=... python cleanup_cars.py
"""

import argparse
import os
import sys

try:
    import requests
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False


def _client():
    url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not url or not key:
        return None
    if not REQUESTS_OK:
        print("ERROR: requests не установлен. pip install requests", file=sys.stderr)
        return None
    return {"url": url, "key": key}


def _headers(cfg: dict) -> dict:
    return {
        "apikey": cfg["key"],
        "Authorization": f"Bearer {cfg['key']}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }


def deactivate_stale(cfg: dict, days: int = 30, dry_run: bool = False) -> int:
    """
    Помечает is_active=false все записи, у которых last_seen старше {days} дней.
    Возвращает количество изменённых строк (best-effort через HEAD count).
    """
    endpoint = f"{cfg['url']}/rest/v1/cars"
    params = {
        "is_active": "eq.true",
        "last_seen": f"lt.now()-interval '{days} days'",
    }
    if dry_run:
        # Считаем сколько будет затронуто
        count_headers = {**_headers(cfg), "Prefer": "count=exact"}
        r = requests.get(endpoint, params=params, headers=count_headers, timeout=30)
        r.raise_for_status()
        count = int(r.headers.get("Content-Range", "0/0").split("/")[-1] or 0)
        print(f"[DRY-RUN] Будет помечено неактивными: {count} записей (last_seen > {days}d)")
        return count

    r = requests.patch(
        endpoint,
        params=params,
        json={"is_active": False},
        headers=_headers(cfg),
        timeout=30,
    )
    r.raise_for_status()
    print(f"Помечено неактивными: записи с last_seen > {days} дней")
    return 0


def delete_old_inactive(cfg: dict, days: int = 60, dry_run: bool = False) -> int:
    """
    Удаляет записи, которые is_active=false И updated_at старше {days} дней.
    """
    endpoint = f"{cfg['url']}/rest/v1/cars"
    params = {
        "is_active": "eq.false",
        "updated_at": f"lt.now()-interval '{days} days'",
    }
    if dry_run:
        count_headers = {**_headers(cfg), "Prefer": "count=exact"}
        r = requests.get(endpoint, params=params, headers=count_headers, timeout=30)
        r.raise_for_status()
        count = int(r.headers.get("Content-Range", "0/0").split("/")[-1] or 0)
        print(f"[DRY-RUN] Будет удалено: {count} записей (is_active=false, updated_at > {days}d)")
        return count

    r = requests.delete(endpoint, params=params, headers=_headers(cfg), timeout=30)
    r.raise_for_status()
    print(f"Удалены неактивные записи старше {days} дней")
    return 0


def main() -> None:
    p = argparse.ArgumentParser(description="Авто-очистка устаревших авто в Supabase")
    p.add_argument("--stale-days",  type=int, default=30,
                   help="Через сколько дней без обновления пометить is_active=false (default: 30)")
    p.add_argument("--delete-days", type=int, default=60,
                   help="Через сколько дней удалять неактивные записи (default: 60)")
    p.add_argument("--dry-run", action="store_true",
                   help="Показать что будет сделано, но ничего не менять")
    args = p.parse_args()

    cfg = _client()
    if cfg is None:
        print("Supabase не настроен (SUPABASE_URL / SUPABASE_SERVICE_KEY не заданы) — пропуск.")
        sys.exit(0)

    try:
        deactivate_stale(cfg, days=args.stale_days, dry_run=args.dry_run)
        delete_old_inactive(cfg, days=args.delete_days, dry_run=args.dry_run)
        print("Очистка завершена.")
    except Exception as e:
        print(f"ОШИБКА при очистке: {e}", file=sys.stderr)
        if hasattr(e, "response") and e.response is not None:
            print(f"  Ответ: {e.response.text[:300]}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
