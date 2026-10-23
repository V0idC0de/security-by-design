#!/usr/bin/env python3
"""Read the configured user's Bash history from a Docker container as JSON."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import re
import subprocess
import sys
from typing import Any


def parse_entries(history: str) -> list[dict[str, Any]]:
    lines = history.splitlines()
    has_timestamps = any(re.fullmatch(r"#\d+", line) for line in lines)
    if not has_timestamps:
        return [
            {"timestamp": None, "command": line}
            for line in lines
            if line
        ]

    entries: list[dict[str, Any]] = []
    current_timestamp: int | None = None
    command_lines: list[str] = []

    def flush() -> None:
        if command_lines:
            timestamp = None
            if current_timestamp is not None:
                timestamp = datetime.fromtimestamp(
                    current_timestamp, timezone.utc
                ).isoformat(timespec="seconds").replace("+00:00", "Z")
            entries.append(
                {"timestamp": timestamp, "command": "\n".join(command_lines)}
            )
            command_lines.clear()

    for line in lines:
        match = re.fullmatch(r"#(\d+)", line)
        if match:
            flush()
            current_timestamp = int(match.group(1))
        else:
            command_lines.append(line)
    flush()
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("container", help="Docker container name or ID")
    args = parser.parse_args()

    read_history = r"""
history_file=${HISTFILE:-"$HOME/.bash_history"}
printf '%s\n' "$history_file"
if [ -r "$history_file" ]; then
    cat -- "$history_file"
else
    printf 'History file is not readable: %s\n' "$history_file" >&2
    exit 4
fi
"""
    try:
        result = subprocess.run(
            ["docker", "exec", args.container, "/bin/bash", "-c", read_history],
            capture_output=True,
            text=True,
            errors="replace",
            check=False,
        )
    except FileNotFoundError:
        payload = {
            "ok": False,
            "container": args.container,
            "error": "docker executable was not found.",
            "exit_code": 127,
            "entries": [],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 127

    output_lines = result.stdout.splitlines()
    history_file = output_lines[0] if output_lines else None
    history_text = "\n".join(output_lines[1:])
    payload = {
        "ok": result.returncode == 0,
        "container": args.container,
        "history_file": history_file,
        "entries": parse_entries(history_text) if result.returncode == 0 else [],
        "error": result.stderr.strip() or None,
        "exit_code": result.returncode,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())