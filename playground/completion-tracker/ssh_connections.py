#!/usr/bin/env python3
"""Report remote SSH sessions known to systemd-logind as JSON."""

from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
import json
import math
import shutil
import sys
import time
from typing import Any

from process_runner import run_process

def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


async def snapshot_async(
    *, timeout: float = 3, semaphore: asyncio.Semaphore | None = None
) -> dict[str, Any]:
    checked_at = timestamp()
    if shutil.which("loginctl") is None:
        return {
            "ok": False,
            "source": "systemd-logind",
            "checked_at": checked_at,
            "sessions": [],
            "errors": ["loginctl is unavailable; this host cannot report logind sessions."],
        }

    listed = await run_process(
        ["loginctl", "list-sessions", "--no-legend"], timeout=timeout, semaphore=semaphore
    )
    if listed.exit_code != 0 or listed.error:
        return {
            "ok": False,
            "source": "systemd-logind",
            "checked_at": checked_at,
            "sessions": [],
            "errors": [listed.error or listed.stderr.strip() or "loginctl could not list sessions."],
        }

    sessions: list[dict[str, str]] = []
    errors: list[str] = []
    properties = [
        "Name",
        "Remote",
        "RemoteHost",
        "Service",
        "Type",
        "Class",
        "State",
        "TTY",
    ]
    async def inspect_session(session_id: str) -> None:
        shown = await run_process(
            [
                "loginctl",
                "show-session",
                session_id,
                *[f"--property={property_name}" for property_name in properties],
            ],
            timeout=timeout,
            semaphore=semaphore,
        )
        if shown.exit_code != 0 or shown.error:
            errors.append(
                f"Could not inspect session {session_id}: "
                f"{shown.error or shown.stderr.strip() or 'loginctl returned an error.'}"
            )
            return

        values = dict(
            line.split("=", 1) for line in shown.stdout.splitlines() if "=" in line
        )
        service = values.get("Service", "")
        if values.get("Remote", "").lower() != "yes":
            return
        if service and "ssh" not in service.lower():
            return
        if values.get("State") == "closing":
            return

        sessions.append(
            {
                "session_id": session_id,
                "username": values.get("Name", ""),
                "remote_host": values.get("RemoteHost", ""),
                "service": service,
                "type": values.get("Type", ""),
                "class": values.get("Class", ""),
                "state": values.get("State", ""),
                "tty": values.get("TTY", ""),
            }
        )

    await asyncio.gather(
        *(inspect_session(line.split()[0]) for line in listed.stdout.splitlines() if line.split())
    )
    sessions.sort(key=lambda session: (session["username"], session["session_id"]))
    return {
        "ok": not errors,
        "source": "systemd-logind",
        "checked_at": checked_at,
        "sessions": sessions,
        "errors": errors,
    }


def snapshot() -> dict[str, Any]:
    return asyncio.run(snapshot_async(semaphore=asyncio.Semaphore(8)))


def emit(value: dict[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2), flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--watch",
        action="store_true",
        help="emit repeated JSON snapshots, one JSON object per line",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="seconds between snapshots in watch mode (default: 2)",
    )
    args = parser.parse_args()
    if not math.isfinite(args.interval) or args.interval <= 0:
        parser.error("--interval must be greater than zero")

    if not args.watch:
        result = snapshot()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["ok"] else 2

    try:
        while True:
            result = snapshot()
            print(json.dumps(result, ensure_ascii=False), flush=True)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())