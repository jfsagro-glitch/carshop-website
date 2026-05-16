#!/usr/bin/env python3
"""Continuous OEM pipeline orchestrator.

Runs the main OEM acquisition streams in waves and writes a persistent JSON log
with per-step status, timings, and produced artifacts.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DEFAULT_LOG_PATH = DATA_DIR / "oem_processing_log.json"
MAX_CAPTURE_CHARS = 12000


def utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def clip_text(value: str, limit: int = MAX_CAPTURE_CHARS) -> str:
    text = str(value or "")
    if len(text) <= limit:
        return text
    tail = text[-limit:]
    return f"... [truncated {len(text) - limit} chars] ...\n{tail}"


@dataclass
class StepResult:
    name: str
    command: list[str]
    started_at: str
    finished_at: str
    return_code: int
    duration_sec: float
    stdout: str
    stderr: str
    ok: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "command": self.command,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "return_code": self.return_code,
            "duration_sec": self.duration_sec,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "ok": self.ok,
        }


class OEMAsyncProcessor:
    def __init__(self, log_path: Path, fail_fast: bool = False, dry_run: bool = False):
        self.log_path = log_path
        self.fail_fast = fail_fast
        self.dry_run = dry_run
        self.python = Path(sys.executable)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.state = self._load_state()

    def _load_state(self) -> dict[str, Any]:
        if self.log_path.exists():
            try:
                payload = json.loads(self.log_path.read_text(encoding="utf-8"))
                if isinstance(payload, dict):
                    payload.setdefault("started_at", utc_now())
                    payload.setdefault("updated_at", utc_now())
                    payload.setdefault("runs", [])
                    payload.setdefault("stats", {})
                    payload.setdefault("mode", "continuous")
                    return payload
            except json.JSONDecodeError:
                pass
        return {
            "started_at": utc_now(),
            "updated_at": utc_now(),
            "mode": "continuous",
            "runs": [],
            "stats": {
                "cycles_total": 0,
                "cycles_ok": 0,
                "cycles_failed": 0,
                "steps_total": 0,
                "steps_ok": 0,
                "steps_failed": 0,
            },
        }

    def _save_state(self) -> None:
        self.state["updated_at"] = utc_now()
        self.log_path.write_text(json.dumps(self.state, ensure_ascii=False, indent=2), encoding="utf-8")

    def _kill_process_tree(self, pid: int) -> None:
        if sys.platform.startswith("win"):
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            return
        subprocess.run(
            ["pkill", "-TERM", "-P", str(pid)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def _run_step(self, name: str, command: list[str], timeout_sec: int | None = None) -> StepResult:
        started = utc_now()
        start_monotonic = time.monotonic()

        if self.dry_run:
            return StepResult(
                name=name,
                command=command,
                started_at=started,
                finished_at=utc_now(),
                return_code=0,
                duration_sec=0.0,
                stdout="[dry-run] step skipped",
                stderr="",
                ok=True,
            )

        proc = subprocess.Popen(
            command,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        try:
            stdout, stderr = proc.communicate(timeout=timeout_sec)
        except subprocess.TimeoutExpired:
            self._kill_process_tree(proc.pid)
            try:
                stdout, stderr = proc.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                stdout, stderr = proc.communicate()
            elapsed = round(time.monotonic() - start_monotonic, 3)
            stdout = clip_text(stdout or "")
            stderr = clip_text(stderr or "")
            if stderr:
                stderr = f"{stderr}\n[timeout] step exceeded {timeout_sec}s"
            else:
                stderr = f"[timeout] step exceeded {timeout_sec}s"
            return StepResult(
                name=name,
                command=command,
                started_at=started,
                finished_at=utc_now(),
                return_code=124,
                duration_sec=elapsed,
                stdout=stdout,
                stderr=stderr,
                ok=False,
            )
        elapsed = round(time.monotonic() - start_monotonic, 3)
        return StepResult(
            name=name,
            command=command,
            started_at=started,
            finished_at=utc_now(),
            return_code=proc.returncode or 0,
            duration_sec=elapsed,
            stdout=clip_text((stdout or "").strip()),
            stderr=clip_text((stderr or "").strip()),
            ok=proc.returncode == 0,
        )

    def _python_cmd(self, script_rel: str, *args: str) -> list[str]:
        return [str(self.python), str(ROOT / script_rel), *args]

    def _extract_found_count(self, step: StepResult) -> int:
        text = f"{step.stdout}\n{step.stderr}"
        match = re.search(r"Summary:\s*Found\s*(\d+)\s*OEM", text, flags=re.IGNORECASE)
        if match:
            return int(match.group(1))
        match = re.search(r"Completed:\s*\d+\s*gaps\s*searched,\s*(\d+)\s*OEM\s*found", text, flags=re.IGNORECASE)
        if match:
            return int(match.group(1))
        return -1

    def _extract_rows_count(self, step: StepResult) -> int:
        text = f"{step.stdout}\n{step.stderr}"
        match = re.search(r"\brows\s*=\s*(\d+)\b", text, flags=re.IGNORECASE)
        if match:
            return int(match.group(1))
        return -1

    def _count_ssl_errors(self, step: StepResult) -> int:
        text = f"{step.stdout}\n{step.stderr}"
        return len(re.findall(r"sitemap_error\s*=\s*SSLError", text, flags=re.IGNORECASE))

    def run_cycle(
        self,
        cycle_index: int,
        wave_size: int,
        workers: int,
        timeout: int,
        enable_vin_live: bool,
        run_verify: bool,
        vin_timeout_sec: int,
        verify_timeout_sec: int,
        vin_brands: str,
        official_ssl_retry: bool,
    ) -> bool:
        stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        cycle_started = utc_now()
        cycle_steps: list[dict[str, Any]] = []

        targeted_out = DATA_DIR / f"oem_supplier_targeted_gaps_cycle{cycle_index}_{stamp}.csv"
        targeted_failed = DATA_DIR / f"oem_gap_failed_cycle{cycle_index}_{stamp}.csv"
        official_out = DATA_DIR / f"oem_supplier_official_sites_cycle{cycle_index}_{stamp}.csv"
        vin_out = DATA_DIR / f"oem_supplier_vin_live_cycle{cycle_index}_{stamp}.csv"
        merged_out = DATA_DIR / "oem_supplier_merged_all.csv"
        verified_csv = DATA_DIR / f"oem_supplier_verified_cycle{cycle_index}_{stamp}.csv"
        verified_lookup_json = DATA_DIR / "oem_lookup_verified_complete.json"

        planned_steps: list[tuple[str, list[str]]] = [
            (
                "gap_import_high",
                self._python_cmd(
                    "tools/import_from_oem_gaps.py",
                    "--priority",
                    "high",
                    "--max-gaps",
                    str(wave_size),
                    "--workers",
                    str(workers),
                    "--timeout",
                    str(timeout),
                    "--checkpoint-every",
                    "25",
                    "--output",
                    str(targeted_out),
                    "--failed-output",
                    str(targeted_failed),
                ),
            ),
            (
                "official_sites_import",
                self._python_cmd(
                    "tools/import_official_oem_sites.py",
                    "--max-pages-per-brand",
                    "120",
                    "--output",
                    str(official_out),
                ),
            ),
        ]

        if enable_vin_live:
            planned_steps.append(
                (
                    "vin_epc_live",
                    self._python_cmd(
                        "tools/import_vin_epc_decoder.py",
                        "--mode",
                        "live",
                        "--brands",
                        vin_brands,
                        "--output",
                        str(vin_out),
                    ),
                )
            )

        if run_verify:
            planned_steps.append(
                (
                    "verify_oem_candidates",
                    self._python_cmd(
                        "tools/verify_oem_candidates.py",
                        "--output",
                        str(verified_csv),
                        "--limit",
                        str(max(500, wave_size * 2)),
                        "--workers",
                        str(workers),
                        "--timeout",
                        str(timeout + 4),
                    ),
                )
            )

        planned_steps.extend(
            [
                (
                    "merge_supplier_sources",
                    self._python_cmd(
                        "tools/merge_all_oem_sources.py",
                        "--source-dir",
                        str(DATA_DIR),
                        "--output",
                        str(merged_out),
                    ),
                ),
                (
                    "build_verified_lookup",
                    self._python_cmd(
                        "tools/build_verified_oem_lookup.py",
                        "--input",
                        str(merged_out),
                        "--output",
                        str(verified_lookup_json),
                    ),
                ),
            ]
        )

        cycle_ok = True
        gap_found = -1
        official_rows = -1
        official_ssl_errors = 0
        for name, cmd in planned_steps:
            timeout_override = None
            if name == "vin_epc_live":
                timeout_override = vin_timeout_sec
            elif name == "verify_oem_candidates":
                timeout_override = verify_timeout_sec
            result = self._run_step(name, cmd, timeout_sec=timeout_override)
            cycle_steps.append(result.as_dict())

            if name == "gap_import_high":
                gap_found = self._extract_found_count(result)

                # Plateau fallback: if nothing found, rerun against full worklist including
                # currently covered pairs to catch missed candidates from source updates.
                if gap_found == 0:
                    fallback_out = DATA_DIR / f"oem_supplier_targeted_retry_cycle{cycle_index}_{stamp}.csv"
                    fallback_failed = DATA_DIR / f"oem_gap_failed_retry_cycle{cycle_index}_{stamp}.csv"
                    retry_cmd = self._python_cmd(
                        "tools/import_from_oem_gaps.py",
                        "--gap-worklist",
                        str(DATA_DIR / "oem_gap_worklist.csv"),
                        "--priority",
                        "high",
                        "--max-gaps",
                        str(max(50, wave_size * 2)),
                        "--workers",
                        str(workers),
                        "--timeout",
                        str(timeout + 2),
                        "--include-covered",
                        "--output",
                        str(fallback_out),
                        "--failed-output",
                        str(fallback_failed),
                    )
                    retry_result = self._run_step("gap_import_plateau_retry", retry_cmd)
                    cycle_steps.append(retry_result.as_dict())
                    self.state["stats"]["steps_total"] += 1
                    if retry_result.ok:
                        self.state["stats"]["steps_ok"] += 1
                    else:
                        self.state["stats"]["steps_failed"] += 1
                        cycle_ok = False
                        if self.fail_fast:
                            break

            if name == "official_sites_import":
                official_rows = self._extract_rows_count(result)
                official_ssl_errors = self._count_ssl_errors(result)

                if official_ssl_retry and official_ssl_errors > 0:
                    ssl_retry_out = DATA_DIR / f"oem_supplier_official_sites_ssl_retry_cycle{cycle_index}_{stamp}.csv"
                    ssl_retry_cmd = self._python_cmd(
                        "tools/import_official_oem_sites.py",
                        "--brands",
                        "VW,AU,SK,SE,MB",
                        "--skip-ssl",
                        "--max-pages-per-brand",
                        "220",
                        "--output",
                        str(ssl_retry_out),
                    )
                    ssl_retry_result = self._run_step("official_sites_ssl_retry", ssl_retry_cmd)
                    cycle_steps.append(ssl_retry_result.as_dict())
                    self.state["stats"]["steps_total"] += 1
                    if ssl_retry_result.ok:
                        self.state["stats"]["steps_ok"] += 1
                    else:
                        self.state["stats"]["steps_failed"] += 1
                        cycle_ok = False
                        if self.fail_fast:
                            break

            self.state["stats"]["steps_total"] += 1
            if result.ok:
                self.state["stats"]["steps_ok"] += 1
            else:
                self.state["stats"]["steps_failed"] += 1
                cycle_ok = False
                if self.fail_fast:
                    break

        cycle_record = {
            "cycle": cycle_index,
            "started_at": cycle_started,
            "finished_at": utc_now(),
            "ok": cycle_ok,
            "wave_size": wave_size,
            "workers": workers,
            "timeout": timeout,
            "enable_vin_live": enable_vin_live,
            "run_verify": run_verify,
            "artifacts": {
                "targeted_out": str(targeted_out),
                "targeted_failed": str(targeted_failed),
                "official_out": str(official_out),
                "vin_out": str(vin_out),
                "merged_out": str(merged_out),
                "verified_lookup_json": str(verified_lookup_json),
            },
            "signals": {
                "gap_import_found": gap_found,
                "plateau_retry_triggered": gap_found == 0,
                "official_rows": official_rows,
                "official_ssl_errors": official_ssl_errors,
                "official_ssl_retry_triggered": official_ssl_retry and official_ssl_errors > 0,
            },
            "steps": cycle_steps,
        }
        self.state["runs"].append(cycle_record)
        self.state["stats"]["cycles_total"] += 1
        if cycle_ok:
            self.state["stats"]["cycles_ok"] += 1
        else:
            self.state["stats"]["cycles_failed"] += 1
        self._save_state()
        return cycle_ok


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run continuous OEM acquisition cycles")
    parser.add_argument("--cycles", type=int, default=1, help="How many cycles to run")
    parser.add_argument("--wave-size", type=int, default=250, help="Gaps per wave for targeted importer")
    parser.add_argument("--workers", type=int, default=8, help="Worker count for threaded tools")
    parser.add_argument("--timeout", type=int, default=8, help="HTTP timeout passed to tools")
    parser.add_argument("--sleep-between", type=int, default=0, help="Seconds between cycles")
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG_PATH, help="JSON state log path")
    parser.add_argument("--disable-vin-live", action="store_true", help="Skip VIN live run")
    parser.add_argument(
        "--vin-timeout-sec",
        type=int,
        default=180,
        help="Hard timeout for VIN live step (seconds)",
    )
    parser.add_argument(
        "--verify-timeout-sec",
        type=int,
        default=300,
        help="Hard timeout for verify_oem_candidates step (seconds)",
    )
    parser.add_argument(
        "--vin-brands",
        default="BM,TY,LX,HY,KI,NI,FO",
        help="Comma-separated brands for VIN live step",
    )
    parser.add_argument(
        "--disable-official-ssl-retry",
        action="store_true",
        help="Disable automatic SSL fallback retry for VAG/MB official sources",
    )
    parser.add_argument("--skip-verify", action="store_true", help="Skip verify_oem_candidates")
    parser.add_argument("--fail-fast", action="store_true", help="Stop current cycle on first failed step")
    parser.add_argument("--dry-run", action="store_true", help="Do not execute commands, only log plan")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    processor = OEMAsyncProcessor(
        log_path=args.log,
        fail_fast=args.fail_fast,
        dry_run=args.dry_run,
    )

    next_cycle = int(processor.state.get("stats", {}).get("cycles_total", 0)) + 1
    for cycle in range(next_cycle, next_cycle + args.cycles):
        ok = processor.run_cycle(
            cycle_index=cycle,
            wave_size=max(1, args.wave_size),
            workers=max(1, args.workers),
            timeout=max(1, args.timeout),
            enable_vin_live=not args.disable_vin_live,
            run_verify=not args.skip_verify,
            vin_timeout_sec=max(30, args.vin_timeout_sec),
            verify_timeout_sec=max(30, args.verify_timeout_sec),
            vin_brands=str(args.vin_brands),
            official_ssl_retry=not args.disable_official_ssl_retry,
        )
        print(f"cycle={cycle} ok={ok}")
        if cycle < (next_cycle + args.cycles - 1) and args.sleep_between > 0:
            time.sleep(args.sleep_between)

    print(f"log={processor.log_path}")


if __name__ == "__main__":
    main()
