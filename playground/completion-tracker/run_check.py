#!/usr/bin/env python3
"""Run a local Bash check script in a container and return its exit status."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
import sys
from typing import Any

from process_runner import run_process


def load_script(path: Path) -> bytes:
    content = path.read_bytes()
    checks = Path(__file__).resolve().parent / "checks"
    if path.resolve().parent.parent == checks:
        content = (checks / "common.bash").read_bytes() + b"\n" + content
    return content


async def execute_check(
    container: str,
    script: bytes,
    script_name: str,
    *,
    timeout: float | None = None,
    semaphore: asyncio.Semaphore | None = None,
) -> dict[str, Any]:
    command = ["docker", "exec", "-i", container]
    if timeout is not None:
        command += ["timeout", "-s", "KILL", f"{timeout:g}"]
    command += ["/bin/bash", "-s"]
    result = await run_process(
        command,
        input_data=script,
        timeout=timeout + 1 if timeout is not None else None,
        semaphore=semaphore,
    )
    stderr = result.stderr
    if result.error:
        stderr = f"{stderr}\n{result.error}".strip()
    return {
        "ok": result.exit_code == 0 and result.error is None,
        "container": container,
        "script": script_name,
        "exit_code": result.exit_code,
        "stdout": result.stdout,
        "stderr": stderr,
    }


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("container", help="Docker container name or ID")
    parser.add_argument("script", type=Path, help="local Bash script to run in the container")
    args = parser.parse_args()

    try:
        script = load_script(args.script)
    except OSError as error:
        emit(
            {
                "ok": False,
                "container": args.container,
                "script": str(args.script),
                "exit_code": 2,
                "stdout": "",
                "stderr": str(error),
            }
        )
        return 2

    result = asyncio.run(execute_check(args.container, script, str(args.script)))
    emit(result)
    return result["exit_code"]


if __name__ == "__main__":
    sys.exit(main())