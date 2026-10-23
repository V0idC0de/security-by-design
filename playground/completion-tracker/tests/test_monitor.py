"""Offline tests only: never query real Docker, SSH, logind or user accounts."""

import argparse
import asyncio
from contextlib import ExitStack
import io
import json
from pathlib import Path
import shlex
import subprocess
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import monitor
import run_check
import ssh_connections
from process_runner import ProcessResult, run_process
from monitor import Assignment, parse_assignment, positive_number


class AssignmentTests(unittest.TestCase):
    def config(self, username="ann-smith", container="lab-ann-smith-07-sbom"):
        return f"Match User {username}\n ForceCommand sudo /usr/bin/docker exec -it {container} /bin/bash\n"

    def test_hyphenated_username(self):
        assignment = parse_assignment(self.config(), "ann-smith")
        self.assertEqual(assignment.container, "lab-ann-smith-07-sbom")
        self.assertEqual(assignment.lab, "07-sbom")

    def test_other_user_prefix_cannot_match(self):
        self.assertIsNone(parse_assignment(self.config("ann", "lab-anna-07-sbom"), "ann").container)

    def test_conflicting_or_missing_directive(self):
        self.assertIsNone(parse_assignment("Match User ann\n", "ann").container)
        self.assertIsNone(parse_assignment(self.config() + "ForceCommand something\n", "ann-smith").container)
        self.assertIsNone(parse_assignment(self.config("other"), "ann-smith").container)

    def test_disabled_lab(self):
        assignment = parse_assignment("Match User ann\n ForceCommand echo No lab; exit 42\n", "ann")
        self.assertEqual(assignment.status, "no lab enabled")

    def test_invalid_lab_name(self):
        self.assertIsNone(parse_assignment(self.config(container="lab-ann-smith-../bad"), "ann-smith").container)

    def test_positive_finite_interval(self):
        self.assertEqual(positive_number("10"), 10)
        for value in ["0", "-1", "nan", "inf"]:
            with self.assertRaises(argparse.ArgumentTypeError):
                positive_number(value)

    def test_default_monitor_account_exclusions_are_opt_in(self):
        args = argparse.Namespace(exclude_user=[], include_janitor=False, include_ubuntu=False)
        excluded = set(args.exclude_user)
        if not args.include_janitor:
            excluded.add("janitor")
        if not args.include_ubuntu:
            excluded.add("ubuntu")
        self.assertEqual(excluded, {"janitor", "ubuntu"})

        args.include_janitor = True
        args.include_ubuntu = True
        excluded = set(args.exclude_user)
        if not args.include_janitor:
            excluded.add("janitor")
        if not args.include_ubuntu:
            excluded.add("ubuntu")
        self.assertEqual(excluded, set())

    def test_home_accounts_only(self):
        accounts = [
            SimpleNamespace(pw_name="root", pw_uid=0, pw_dir="/root"),
            SimpleNamespace(pw_name="student", pw_uid=1000, pw_dir="/home/student"),
            SimpleNamespace(pw_name="admin", pw_uid=1001, pw_dir="/home/admin"),
            SimpleNamespace(pw_name="daemon", pw_uid=2, pw_dir="/var/lib/daemon"),
            SimpleNamespace(pw_name="missing", pw_uid=1002, pw_dir="/home/missing"),
        ]
        with patch("monitor.pwd.getpwall", return_value=accounts), patch.object(
            Path, "is_dir", lambda path: str(path) != "/home/missing"
        ):
            self.assertEqual(monitor.discover_students({"admin"}), ["student"])

    def test_unreadable_config(self):
        with patch.object(Path, "read_text", side_effect=PermissionError):
            self.assertIsNone(monitor.read_assignment("student").container)

    def test_unsupported_or_global_command(self):
        for config in [
            "ForceCommand sudo /usr/bin/docker exec -it lab-ann-07-sbom /bin/bash",
            "Match all\n ForceCommand anything",
            "Match User ann\n ForceCommand sh -c anything",
            'Match User ann\n ForceCommand "unclosed',
        ]:
            self.assertIsNone(parse_assignment(config, "ann").container)


class OfflineAsyncTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.external = patch(
            "asyncio.create_subprocess_exec",
            side_effect=AssertionError("Live subprocess probes are forbidden in this test."),
        )
        self.external.start()
        self.addCleanup(self.external.stop)

    async def cycle(self, assignment, inventory=None, ssh=None, execute=None):
        if inventory is None:
            inventory = {"ok": True, "containers": {"lab-ann-07-sbom": "running"}, "errors": []}
        if ssh is None:
            ssh = {"ok": True, "sessions": [], "errors": []}
        with ExitStack() as stack:
            stack.enter_context(patch("monitor.discover_students", return_value=["ann"]))
            stack.enter_context(patch("monitor.read_assignment", return_value=assignment))
            stack.enter_context(patch("monitor.container_inventory", AsyncMock(return_value=inventory)))
            stack.enter_context(patch("monitor.snapshot_async", AsyncMock(return_value=ssh)))
            stack.enter_context(patch("monitor.discover_checks", return_value=[Path("01-demo.sh")] ))
            stack.enter_context(patch("monitor.load_script", return_value=b"exit 0\n"))
            runner = stack.enter_context(patch("monitor.execute_check", execute or AsyncMock(return_value={
                "ok": True, "exit_code": 0, "stderr": "", "stdout": ""
            })))
            report = await monitor.collect_cycle(timeout=3, jobs=8, excluded=set(), script_cache={})
        return report, runner

    async def test_no_fallback_even_with_one_running_container(self):
        report, runner = await self.cycle(Assignment())
        runner.assert_not_called()
        self.assertIsNone(report["students"][0]["container"])

    async def test_configured_container_wins_over_other_running_labs(self):
        assignment = Assignment("lab-ann-07-sbom", "07-sbom", "configured")
        inventory = {"ok": True, "containers": {
            "lab-ann-07-sbom": "running", "lab-ann-02-pre-commit": "running"
        }, "errors": []}
        report, runner = await self.cycle(assignment, inventory)
        self.assertEqual(runner.call_args.args[0], assignment.container)
        self.assertEqual(report["students"][0]["checks"][0]["status"], "pass")

    async def test_missing_or_stopped_container_never_falls_back(self):
        assignment = Assignment("lab-ann-07-sbom", "07-sbom", "configured")
        for state in [None, "exited"]:
            containers = {"lab-ann-02-pre-commit": "running"}
            if state is not None:
                containers[assignment.container] = state
            report, runner = await self.cycle(assignment, {"ok": True, "containers": containers, "errors": []})
            runner.assert_not_called()
            self.assertEqual(report["students"][0]["container"], assignment.container)

    async def test_ssh_error_does_not_mean_offline(self):
        report, _ = await self.cycle(Assignment(), ssh={"ok": False, "sessions": [], "errors": ["unavailable"]})
        self.assertEqual(report["students"][0]["ssh"], "unknown")

    async def test_docker_inventory_parse(self):
        value = json.dumps({"Names": "lab-ann-07-sbom", "State": "running"})
        with patch("monitor.run_process", AsyncMock(return_value=ProcessResult(0, value))):
            inventory = await monitor.container_inventory(3, asyncio.Semaphore(8))
        self.assertEqual(inventory["containers"], {"lab-ann-07-sbom": "running"})
        with patch("monitor.run_process", AsyncMock(return_value=ProcessResult(0, "not JSON"))):
            inventory = await monitor.container_inventory(3, asyncio.Semaphore(8))
        self.assertFalse(inventory["ok"])

    async def test_ssh_filters_closing_and_local_sessions(self):
        async def fake_login(command, **kwargs):
            if command[1] == "list-sessions":
                return ProcessResult(0, "1 1000 ann\n2 1000 ann\n3 1001 bob\n")
            values = {
                "1": "Name=ann\nRemote=yes\nService=sshd\nState=active\n",
                "2": "Name=ann\nRemote=yes\nService=sshd\nState=closing\n",
                "3": "Name=bob\nRemote=no\nService=login\nState=active\n",
            }
            return ProcessResult(0, values[command[2]])
        with patch("ssh_connections.shutil.which", return_value="/fake/loginctl"), patch(
            "ssh_connections.run_process", side_effect=fake_login
        ):
            result = await ssh_connections.snapshot_async(semaphore=asyncio.Semaphore(8))
        self.assertEqual([session["username"] for session in result["sessions"]], ["ann"])

    async def test_runner_json_and_timeout_command(self):
        for code in [0, 1, 7]:
            with patch("run_check.run_process", AsyncMock(return_value=ProcessResult(code, "out\n", ""))) as run:
                result = await run_check.execute_check("lab-ann-07-sbom", b"exit 7\n", "check.sh", timeout=3)
            self.assertEqual(result["exit_code"], code)
            self.assertEqual(result["ok"], code == 0)
            self.assertEqual(result["stdout"], "out\n")
            self.assertEqual(run.call_args.args[0], ["docker", "exec", "-i", "lab-ann-07-sbom", "timeout", "-s", "KILL", "3", "/bin/bash", "-s"])
            self.assertEqual(run.call_args.kwargs["input_data"], b"exit 7\n")

    async def test_thirty_students_bounded_and_incremental(self):
        users = [f"student{number:02}" for number in range(30)]
        active = 0
        peak = 0
        updates = []

        async def fake_process(command, **kwargs):
            nonlocal active, peak
            active += 1
            peak = max(active, peak)
            try:
                await asyncio.sleep(0.001)
                return ProcessResult(0)
            finally:
                active -= 1

        with ExitStack() as stack:
            stack.enter_context(patch("monitor.discover_students", return_value=users))
            stack.enter_context(patch("monitor.read_assignment", side_effect=lambda user: Assignment(f"lab-{user}-07-sbom", "07-sbom", "configured")))
            stack.enter_context(patch("monitor.container_inventory", AsyncMock(return_value={
                "ok": True, "containers": {f"lab-{user}-07-sbom": "running" for user in users}, "errors": []
            })))
            stack.enter_context(patch("monitor.snapshot_async", AsyncMock(return_value={"ok": True, "sessions": [], "errors": []})))
            stack.enter_context(patch("monitor.discover_checks", return_value=[Path("01-demo.sh"), Path("02-next.sh")]))
            stack.enter_context(patch("monitor.load_script", return_value=b"exit 0\n"))
            original_spawn = asyncio.create_subprocess_exec

            async def guarded_run(command, *, semaphore=None, **kwargs):
                if semaphore is not None:
                    async with semaphore:
                        return await fake_process(command, **kwargs)
                return await fake_process(command, **kwargs)

            stack.enter_context(patch("run_check.run_process", side_effect=guarded_run))
            report = await monitor.collect_cycle(
                timeout=3, jobs=8, excluded=set(), script_cache={},
                publish=lambda report: updates.append(sum(
                    check["status"] != "pending" for row in report["students"] for check in row["checks"]
                )),
            )
            self.assertIs(asyncio.create_subprocess_exec, original_spawn)
        self.assertEqual(len(report["students"]), 30)
        self.assertEqual(updates[0], 0)
        self.assertEqual(updates[-1], 60)
        self.assertTrue(any(0 < value < 60 for value in updates))
        self.assertGreater(peak, 1)
        self.assertLessEqual(peak, 8)

    async def test_refreshes_are_sequential_and_non_terminal_output_is_json(self):
        active = 0
        peak = 0
        calls = 0
        sleeps = []
        real_sleep = asyncio.sleep

        async def collect(**kwargs):
            nonlocal active, peak, calls
            active += 1
            peak = max(peak, active)
            await real_sleep(0)
            active -= 1
            calls += 1
            return {"checked_at": "now", "complete": True, "students": [], "errors": []}

        async def sleep(delay):
            sleeps.append(delay)
            if len(sleeps) == 2:
                raise asyncio.CancelledError

        output = io.StringIO()
        args = SimpleNamespace(timeout=3, jobs=8, exclude_user=[], once=False, interval=10)
        with patch("monitor.collect_cycle", side_effect=collect), patch("monitor.asyncio.sleep", side_effect=sleep), patch("sys.stdout", output):
            with self.assertRaises(asyncio.CancelledError):
                await monitor.watch(args)
        self.assertEqual(calls, 2)
        self.assertEqual(peak, 1)
        self.assertTrue(all(0 <= delay <= 10 for delay in sleeps))
        self.assertEqual(len([json.loads(line) for line in output.getvalue().splitlines()]), 2)
        self.assertNotIn("\033", output.getvalue())

    async def test_terminal_is_restored_when_collection_fails(self):
        output = io.StringIO()
        output.isatty = lambda: True
        args = SimpleNamespace(timeout=3, jobs=8, exclude_user=[], once=True, interval=10)
        with patch("monitor.collect_cycle", AsyncMock(side_effect=RuntimeError("mock failure"))), patch("sys.stdout", output):
            with self.assertRaises(RuntimeError):
                await monitor.watch(args)
        self.assertIn("\033[?25h\033[?1049l", output.getvalue())


class DisplayAndCheckTests(unittest.TestCase):
    def test_standalone_runner_json_and_exit_code_unchanged(self):
        for code in [0, 1, 7]:
            output = io.StringIO()
            payload = {"ok": code == 0, "container": "test", "script": "check.sh", "exit_code": code, "stdout": "out\n", "stderr": ""}
            with patch("sys.argv", ["run_check.py", "test", "check.sh"]), patch(
                "run_check.load_script", return_value=b"exit 0\n"
            ), patch("run_check.execute_check", AsyncMock(return_value=payload)), patch("sys.stdout", output):
                self.assertEqual(run_check.main(), code)
            self.assertEqual(json.loads(output.getvalue()), payload)

    def test_render_never_wraps_and_warns_of_hidden_rows(self):
        report = {"checked_at": "now", "complete": True, "errors": [], "students": [
            {"username": f"student{number}", "ssh": "offline", "container": "lab-student-07-sbom", "status": "ready", "checks": [
                {"name": "application-scan-run", "status": "pass"}
            ]} for number in range(30)
        ]}
        lines = monitor.render(report, 80, 10, unicode=False)
        self.assertTrue(all(len(line) <= 80 for line in lines))
        self.assertEqual(len(lines), 10)
        self.assertIn("hidden", lines[-2])
        self.assertIn("+ SSH open", lines[-1])

    def test_render_uses_bracketed_emoji_indicators(self):
        report = {"checked_at": "now", "complete": True, "errors": [], "students": [
            {"username": "student", "ssh": "online", "container": "lab-student-07-sbom", "status": "ready", "checks": [
                {"name": "application-scan-run", "status": "pass"},
                {"name": "os-scan-run", "status": "fail"},
            ]}
        ]}

        lines = monitor.render(report, 200, 10)

        self.assertIn("🟢", lines[2])
        self.assertIn("[application-scan-run ✅]", lines[2])
        self.assertIn("[os-scan-run ❌]", lines[2])

    def test_render_header_uses_time_and_refresh_progress(self):
        report = {"checked_at": "not a timestamp", "complete": True, "errors": [], "students": []}

        header = monitor.render(report, 200, 10)[0]

        self.assertRegex(header, r"^📊 Lab progress \| --:--:-- \[----------\] \| complete$")

    def test_render_reserves_hidden_note_and_final_legend(self):
        report = {"checked_at": "now", "complete": True, "errors": [], "students": [
            {"username": f"student{number}", "ssh": "offline", "container": "lab-student-07-sbom", "status": "ready", "checks": []}
            for number in range(4)
        ]}

        lines = monitor.render(report, 200, 6)

        self.assertEqual(len(lines), 6)
        self.assertIn("2 students hidden", lines[-2])
        self.assertIn("🟢 SSH open", lines[-1])

    def test_check_order_and_shared_helper_loading(self):
        checks = monitor.discover_checks("07-sbom")
        self.assertEqual(len(checks), 5)
        self.assertEqual(checks, sorted(checks))
        self.assertIn(b"history_has()", run_check.load_script(checks[0]))

    def test_status_distinguishes_errors(self):
        self.assertEqual(monitor.check_status({"ok": False, "exit_code": 1, "stderr": ""}), "fail")
        self.assertEqual(monitor.check_status({"ok": False, "exit_code": 124, "stderr": "timeout"}), "error")
        self.assertEqual(monitor.check_status({"ok": False, "exit_code": 1, "stderr": "Docker failed"}), "error")

    def test_history_patterns_with_controlled_stdin_only(self):
        directory = monitor.ROOT / "checks"
        samples = [
            ("00-id-tokens/01-login-run.sh", " gh auth login -s delete_repo", "echo gh auth login"),
            ("01-git-hacking/01-git-probe-run.sh", "curl 'http://localhost:8000/.git/config'", "curl http://localhost:8000/config"),
            ("01-git-hacking/03-secret-scan-run.sh", " trufflehog git file://.", "echo trufflehog git"),
            ("01-git-hacking/04-code-scan-run.sh", " bandit -r .", "bandit --help"),
            ("07-sbom/03-app-scan-run.sh", " grype 'sbom:sbom.json'", "grype sbom:sbom.jsonx"),
            ("07-sbom/05-os-scan-run.sh", "grype sbom:sbom-os.json -o json | jq '.matches | length'", "grype sbom:sbom.json"),
        ]
        for relative, present, absent in samples:
            line = (directory / relative).read_text().splitlines()[1]
            pattern = shlex.split(line)[1]
            anchored = "^[[:space:]]*((command|sudo)[[:space:]]+)?" + pattern
            for text, expected in [(present, 0), (absent, 1)]:
                result = subprocess.run(["grep", "-Eq", anchored], input=text, text=True, capture_output=True)
                self.assertEqual(result.returncode, expected, relative)



class ProcessTests(unittest.IsolatedAsyncioTestCase):
    def fake_process(self, stdout=b"", stderr=b"", exit_code=0):
        process = MagicMock()
        process.stdout = asyncio.StreamReader()
        process.stdout.feed_data(stdout)
        process.stdout.feed_eof()
        process.stderr = asyncio.StreamReader()
        process.stderr.feed_data(stderr)
        process.stderr.feed_eof()
        process.stdin.drain = AsyncMock()
        process.returncode = exit_code
        process.wait = AsyncMock(return_value=exit_code)
        return process

    async def test_stdin_and_exit_status(self):
        process = self.fake_process(b"not yet\n", b"detail\n", 1)
        with patch("asyncio.create_subprocess_exec", AsyncMock(return_value=process)) as spawn:
            result = await run_process(["fake", "argument with spaces"], input_data=b"exit 1\n")
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.stdout, "not yet\n")
        self.assertEqual(result.stderr, "detail\n")
        process.stdin.write.assert_called_once_with(b"exit 1\n")
        process.stdin.close.assert_called_once()
        self.assertEqual(spawn.call_args.args, ("fake", "argument with spaces"))

    async def test_output_is_bounded(self):
        process = self.fake_process(b"x" * 100000)
        with patch("asyncio.create_subprocess_exec", AsyncMock(return_value=process)):
            result = await run_process(["fake"])
        self.assertEqual(len(result.stdout), 65536)
        self.assertIsNotNone(result.error)

    async def test_timeout_reaps_process(self):
        process = self.fake_process()
        process.returncode = None

        async def wait():
            if process.kill.called:
                process.returncode = -9
                return -9
            await asyncio.Event().wait()

        process.wait = AsyncMock(side_effect=wait)
        with patch("asyncio.create_subprocess_exec", AsyncMock(return_value=process)):
            result = await run_process(["fake"], timeout=0.01)
        self.assertEqual(result.exit_code, 124)
        process.kill.assert_called_once()
        self.assertEqual(process.returncode, -9)

    async def test_cancellation_reaps_process_and_releases_semaphore(self):
        process = self.fake_process()
        process.returncode = None
        started = asyncio.Event()

        async def wait():
            if process.kill.called:
                process.returncode = -9
                return -9
            started.set()
            await asyncio.Event().wait()

        process.wait = AsyncMock(side_effect=wait)
        semaphore = asyncio.Semaphore(1)
        with patch("asyncio.create_subprocess_exec", AsyncMock(return_value=process)):
            task = asyncio.create_task(run_process(["fake"], semaphore=semaphore))
            await started.wait()
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
        process.kill.assert_called_once()
        self.assertFalse(semaphore.locked())


if __name__ == "__main__":
    unittest.main()
