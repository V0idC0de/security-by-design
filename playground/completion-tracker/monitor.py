#!/usr/bin/env python3
"""Live lab progress dashboard for the instructor's VM (Python 3.12)."""

from __future__ import annotations

import argparse
import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import pwd
import re
import shlex
import shutil
import sys
import time
from typing import Any, Callable

from process_runner import run_process
from run_check import execute_check, load_script
from ssh_connections import snapshot_async

ROOT = Path(__file__).resolve().parent
CONFIG_DIR = Path("/etc/ssh/sshd_config.d")
CHECK_NAME = re.compile(r"[0-9]{2}-[a-z0-9-]+\.sh")


@dataclass(frozen=True)
class Assignment:
    container: str | None = None
    lab: str | None = None
    status: str = "config unavailable"


def discover_students(excluded: set[str]) -> list[str]:
    students = []
    for account in pwd.getpwall():
        home = Path(account.pw_dir)
        if account.pw_uid == 0 or account.pw_name == "root" or account.pw_name in excluded:
            continue
        if home.resolve().is_relative_to("/home") and home != Path("/home") and home.is_dir():
            students.append(account.pw_name)
    return sorted(set(students))


def parse_assignment(config: str, username: str) -> Assignment:
    commands: list[str] = []
    matched = False
    for raw_line in config.splitlines():
        try:
            tokens = shlex.split(raw_line, comments=True)
        except ValueError:
            return Assignment(status="invalid SSH config")
        if not tokens:
            continue
        directive = tokens[0].lower()
        if directive == "match":
            if matched or len(tokens) != 3 or tokens[1].lower() != "user" or tokens[2] != username:
                return Assignment(status="unexpected Match User")
            matched = True
        elif directive == "forcecommand":
            if not matched:
                return Assignment(status="ForceCommand outside Match User")
            commands.append(raw_line.strip().split(None, 1)[1] if len(tokens) > 1 else "")
    if not matched or len(commands) != 1:
        return Assignment(status="missing/conflicting ForceCommand")
    command = shlex.split(commands[0], comments=True)
    if command and command[0] == "echo" and re.search(r";\s*exit\s+42\s*$", commands[0]):
        return Assignment(status="no lab enabled")
    if len(command) != 6 or command[:4] != ["sudo", "/usr/bin/docker", "exec", "-it"] or command[-1] != "/bin/bash":
        return Assignment(status="unsupported ForceCommand")
    container = command[4]
    prefix = f"lab-{username}-"
    if not container.startswith(prefix):
        return Assignment(status="container/user mismatch")
    lab = container[len(prefix):]
    if not re.fullmatch(r"[0-9]{2}-[a-zA-Z0-9][a-zA-Z0-9_.-]*", lab):
        return Assignment(status="invalid lab name")
    return Assignment(container, lab, "configured")


def read_assignment(username: str) -> Assignment:
    try:
        config = (CONFIG_DIR / f"00-labuser-{username}.conf").read_text()
    except OSError:
        return Assignment()
    except UnicodeError:
        return Assignment(status="invalid SSH config encoding")
    return parse_assignment(config, username)


async def container_inventory(timeout: float, semaphore: asyncio.Semaphore) -> dict[str, Any]:
    result = await run_process(
        ["docker", "ps", "--all", "--format", "{{json .}}"],
        timeout=timeout,
        semaphore=semaphore,
    )
    if result.exit_code or result.error:
        return {"ok": False, "containers": {}, "errors": [result.error or result.stderr.strip() or "Docker inventory failed."]}
    try:
        containers = {}
        for line in result.stdout.splitlines():
            item = json.loads(line)
            containers[item["Names"]] = item["State"]
    except (ValueError, KeyError, TypeError):
        return {"ok": False, "containers": {}, "errors": ["Invalid Docker inventory JSON."]}
    return {"ok": True, "containers": containers, "errors": []}


def discover_checks(lab: str, directory: Path = ROOT / "checks") -> list[Path]:
    return sorted(
        path for path in (directory / lab).glob("*.sh")
        if path.is_file() and not path.is_symlink() and CHECK_NAME.fullmatch(path.name)
    )


def check_status(result: dict[str, Any]) -> str:
    if result["ok"]:
        return "pass"
    if result["exit_code"] == 1 and not result["stderr"]:
        return "fail"
    return "error"


async def collect_cycle(
    *,
    timeout: float,
    jobs: int,
    excluded: set[str],
    script_cache: dict[Path, bytes],
    publish: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    semaphore = asyncio.Semaphore(jobs)
    students = discover_students(excluded)
    assignments = {username: read_assignment(username) for username in students}
    inventory, ssh = await asyncio.gather(
        container_inventory(timeout, semaphore),
        snapshot_async(timeout=timeout, semaphore=semaphore),
    )
    connected = {
        session["username"] for session in ssh["sessions"]
        if session.get("state") != "closing"
    }
    report: dict[str, Any] = {
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "complete": False,
        "errors": inventory["errors"] + ssh["errors"],
        "students": [],
    }
    work: list[tuple[dict[str, Any], dict[str, Any], Path]] = []
    for username in students:
        assignment = assignments[username]
        row: dict[str, Any] = {
            "username": username,
            "ssh": "online" if username in connected else "offline" if ssh["ok"] else "unknown",
            "container": assignment.container,
            "lab": assignment.lab,
            "status": assignment.status,
            "checks": [],
        }
        report["students"].append(row)
        if assignment.container is None:
            continue
        if not inventory["ok"]:
            row["status"] = "Docker unavailable"
            continue
        state = inventory["containers"].get(assignment.container)
        if state != "running":
            row["status"] = state or "container missing"
            continue
        paths = discover_checks(assignment.lab or "")
        row["status"] = "checking" if paths else "no checks"
        for path in paths:
            check = {"name": path.stem[3:], "status": "pending", "exit_code": None, "detail": ""}
            row["checks"].append(check)
            work.append((row, check, path))
    if publish:
        publish(report)

    async def evaluate(row: dict[str, Any], check: dict[str, Any], path: Path) -> None:
        try:
            if path not in script_cache:
                script_cache[path] = load_script(path)
            result = await execute_check(
                row["container"], script_cache[path], str(path), timeout=timeout, semaphore=semaphore
            )
            check.update(
                status=check_status(result),
                exit_code=result["exit_code"],
                detail=result["stderr"] if check_status(result) == "error" else "",
            )
        except OSError as error:
            check.update(status="error", detail=str(error))
        if all(item["status"] != "pending" for item in row["checks"]):
            row["status"] = "ready" if all(item["status"] != "error" for item in row["checks"]) else "check error"
        if publish:
            publish(report)

    async with asyncio.TaskGroup() as tasks:
        for row, check, path in work:
            tasks.create_task(evaluate(row, check, path))
    report["complete"] = True
    return report


def clean(text: str) -> str:
    return "".join(character if character.isprintable() else " " for character in text)


def render(
    report: dict[str, Any], width: int, height: int, *, unicode: bool = True, refresh_interval: float = 10.0
) -> list[str]:
    symbols = {
        "pass": "✅" if unicode else "+",
        "fail": "❌" if unicode else "x",
        "error": "⚠️" if unicode else "?",
        "pending": "⏳" if unicode else ".",
    }
    ssh_symbols = {"online": "🟢", "offline": "⚫", "unknown": "❓"} if unicode else {
        "online": "+", "offline": "-", "unknown": "?"
    }
    rows = report["students"]
    user_width = min(18, max((len(row["username"]) for row in rows), default=7))
    container_width = min(48, max((len(row["container"] or "-") for row in rows), default=9))
    snapshot: datetime | None = None
    try:
        snapshot = datetime.fromisoformat(report["checked_at"])
        elapsed = max(0.0, (datetime.now(timezone.utc) - snapshot).total_seconds())
    except (TypeError, ValueError):
        elapsed = 0.0
    progress = min(1.0, elapsed / refresh_interval) if refresh_interval > 0 else 1.0
    progress_width = 10
    filled = round(progress * progress_width)
    refresh_bar = "#" * filled + "-" * (progress_width - filled)
    title_icon = "📊" if unicode else "*"
    clock = snapshot.strftime("%H:%M:%S") if snapshot is not None else "--:--:--"
    lines = [f"{title_icon} Lab progress | {clock} [{refresh_bar}] | {'complete' if report['complete'] else 'checking'}"]
    lines.append(f"SSH {'Student':<{user_width}}  {'Configured container':<{container_width}}  Checks")
    clipped = False
    available = max(0, height - 3)
    if len(rows) > available:
        available = max(0, height - 4)
    for row in rows[:available]:
        indicator = ssh_symbols[row["ssh"]]
        checks = "  ".join(f"[{item['name']} {symbols[item['status']]}]" for item in row["checks"])
        if row["status"] not in {"ready", "checking"}:
            checks = f"[{row['status']}] {checks}"
        line = f" {indicator}  {row['username']:<{user_width}.{user_width}}  {row['container'] or '-':<{container_width}.{container_width}}  {checks}"
        line = clean(line)
        clipped |= len(line) > width or len(row["username"]) > user_width or len(row["container"] or "") > container_width
        lines.append(line[:max(0, width)])
    footer = "🟢 SSH open | ⚫ offline | ❓ unknown | ✅ complete | ❌ incomplete | ⚠️ error | ⏳ pending | Ctrl+C exits" if unicode else "+ SSH open | - offline | ? unknown/error | . pending | Ctrl+C exits"
    if len(rows) > available:
        lines.append(f"{len(rows) - available} students hidden: increase terminal height.")
    if clipped:
        lines.append("Columns clipped: widen terminal.")
    if report["errors"]:
        lines.append("Discovery error: " + "; ".join(report["errors"]))
    lines.append(clean(footer)[:max(0, width)])
    return [clean(line)[:max(0, width)] for line in lines[:height]]


async def watch(args: argparse.Namespace) -> None:
    terminal = sys.stdout.isatty()
    cache: dict[Path, bytes] = {}
    excluded = set(args.exclude_user)
    if not getattr(args, "include_janitor", False):
        excluded.add("janitor")
    if not getattr(args, "include_ubuntu", False):
        excluded.add("ubuntu")
    supports_unicode = True
    try:
        "\u2713\u2717".encode(sys.stdout.encoding or "utf-8")
    except UnicodeEncodeError:
        supports_unicode = False
    last_redraw = 0.0

    def redraw(report: dict[str, Any], force: bool = False) -> None:
        nonlocal last_redraw
        if not terminal or (not force and time.monotonic() - last_redraw < 0.1):
            return
        last_redraw = time.monotonic()
        size = shutil.get_terminal_size((140, 36))
        lines = render(report, size.columns - 1, size.lines, unicode=supports_unicode, refresh_interval=args.interval)
        sys.stdout.write("\033[H" + "\n".join(line + "\033[K" for line in lines) + "\033[J")
        sys.stdout.flush()

    if terminal:
        sys.stdout.write("\033[?1049h\033[?25l")
    try:
        while True:
            started = time.monotonic()
            report = await collect_cycle(
                timeout=args.timeout, jobs=args.jobs, excluded=excluded,
                script_cache=cache, publish=redraw if terminal else None,
            )
            report["elapsed_seconds"] = round(time.monotonic() - started, 2)
            report["overdue"] = report["elapsed_seconds"] > args.interval
            if terminal:
                if report["overdue"]:
                    report["errors"].append(f"Refresh took {report['elapsed_seconds']}s (target {args.interval:g}s).")
                redraw(report, force=True)
            else:
                print(json.dumps(report, ensure_ascii=True), flush=True)
            if args.once:
                return
            remaining = max(0, args.interval - (time.monotonic() - started))
            if terminal:
                while remaining > 0:
                    await asyncio.sleep(min(0.1, remaining))
                    redraw(report, force=True)
                    remaining = max(0, args.interval - (time.monotonic() - started))
            else:
                await asyncio.sleep(remaining)
    finally:
        if terminal:
            sys.stdout.write("\033[?25h\033[?1049l")
            sys.stdout.flush()


def positive_number(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed) or parsed <= 0:
        raise argparse.ArgumentTypeError("must be a positive finite number")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interval", type=positive_number, default=10.0)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--timeout", type=positive_number, default=3.0)
    parser.add_argument("--exclude-user", action="append", default=[])
    parser.add_argument("--include-janitor", action="store_true", help="include the janitor account")
    parser.add_argument("--include-ubuntu", action="store_true", help="include the ubuntu account")
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error("--jobs must be at least 1")
    try:
        asyncio.run(watch(args))
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
