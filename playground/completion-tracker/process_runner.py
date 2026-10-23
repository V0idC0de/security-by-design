"""Bounded, cancellable subprocess execution for the tracker (Python 3.12)."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass


@dataclass
class ProcessResult:
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    error: str | None = None


async def _read(stream: asyncio.StreamReader) -> tuple[str, bool]:
    chunks = bytearray()
    truncated = False
    while chunk := await stream.read(8192):
        available = 65536 - len(chunks)
        chunks.extend(chunk[:available])
        truncated |= len(chunk) > available
    return chunks.decode("utf-8", errors="replace"), truncated


async def run_process(
    command: list[str],
    *,
    input_data: bytes | None = None,
    timeout: float | None = 3,
    semaphore: asyncio.Semaphore | None = None,
) -> ProcessResult:
    if semaphore is not None:
        async with semaphore:
            return await run_process(command, input_data=input_data, timeout=timeout)

    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            stdin=asyncio.subprocess.PIPE if input_data is not None else asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except OSError as error:
        return ProcessResult(127, error=str(error))

    async def send_input() -> None:
        if process.stdin is not None:
            try:
                process.stdin.write(input_data or b"")
                await process.stdin.drain()
            except (BrokenPipeError, ConnectionResetError):
                pass
            finally:
                process.stdin.close()

    try:
        assert process.stdout is not None and process.stderr is not None
        async with asyncio.timeout(timeout):
            stdout, stderr, _, exit_code = await asyncio.gather(
                _read(process.stdout), _read(process.stderr), send_input(), process.wait()
            )
        if stdout[1] or stderr[1]:
            return ProcessResult(exit_code, stdout[0], stderr[0], "Output exceeded 64 KiB per stream.")
        return ProcessResult(exit_code, stdout[0], stderr[0])
    except TimeoutError:
        return ProcessResult(124, error=f"Command timed out after {timeout:g} seconds.")
    finally:
        if process.returncode is None:
            try:
                process.kill()
            except ProcessLookupError:
                pass
            await process.wait()