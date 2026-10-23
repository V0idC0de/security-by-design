# Completion Tracker

Live instructor dashboard for the lab VM. **Python 3.12 is the tested and supported version.** No Python packages are required. Run the tools on the VM, normally as root, with access to Docker and `loginctl`.

## Usage

Run from this directory:

```bash
python monitor.py
python monitor.py --interval 10 --jobs 8 --timeout 3 --exclude-user instructor
python monitor.py --include-janitor --include-ubuntu
```

The monitor refreshes until Ctrl+C. Defaults are a 10-second interval, eight concurrent checks, and a three-second timeout per check. Use `--once` for one JSON snapshot:

```bash
python monitor.py --once | python -m json.tool
```

Each terminal row contains the SSH state, username, configured container, and ordered checks. Check labels use `[check-name marker]`.

| Indicator | Meaning |
| --- | --- |
| `🟢` / `⚫` / `❓` | SSH active / inactive / unavailable |
| `✅` / `❌` | Check passed / evidence not found |
| `⚠️` / `⏳` | Check error / still running |

The header shows the last snapshot time and a progress bar toward the next refresh. The legend is always the final line; if rows do not fit, the hidden-student count appears immediately above it. Widen the terminal if rows are clipped.

The `janitor` and `ubuntu` accounts are excluded by default. Include them with the no-value flags `--include-janitor` and `--include-ubuntu`. Use repeatable `--exclude-user NAME` options for other accounts.

## How information is retrieved

- **Students:** non-root accounts with existing home directories under `/home`; orphan directories are ignored.
- **Active lab:** the generated `/etc/ssh/sshd_config.d/00-labuser-USERNAME.conf`. The monitor parses the expected `Match User` and Docker `ForceCommand` and derives the lab from the configured container name.
- **Container state:** one Docker inventory query per refresh verifies that the configured container is running. Other containers are never used as fallbacks.
- **SSH state:** one `loginctl` snapshot per refresh lists remote, non-closing SSH sessions. A collector error is shown as unavailable, not offline.
- **Progress checks:** numbered scripts under `checks/LAB/` are run inside the configured container. They inspect local files, Git state, and Bash history; they do not run scanners, Terraform, cloud APIs, or network calls.
- **History:** interactive lab shells append commands to the default user's `$HISTFILE` at each prompt. Checks read that history inside the container; the dashboard does not display raw histories.

The output is activity evidence, not a tamper-proof audit, proof of command success, or proof that a student understood the result. Browser-only actions and remote resource existence are intentionally not checked. History and check output may contain sensitive student activity and must be access-controlled.

## Standalone tools

```bash
python ssh_connections.py
python ssh_connections.py --watch --interval 2
python container_history.py lab-student-02-pre-commit
python run_check.py lab-student-02-pre-commit checks/02-pre-commit/01-hook.sh
```

`ssh_connections.py` emits logind SSH sessions as JSON. `container_history.py` emits the configured container user's history as JSON. `run_check.py` sends a local Bash script to the container over stdin and emits its status and bounded output.

## Adding checks

Create `checks/LAB/NN-short-label.sh`. Checks are discovered in numeric filename order and displayed using the filename suffix. They should be read-only and cheap:

- return `0` for evidence found and `1` for ordinary evidence not found;
- return `2` or higher, or write to stderr, for an error;
- use `$HOME` and `${HISTFILE:-$HOME/.bash_history}`;
- do not emit secrets or invoke installs, scans, network calls, or writes.

The shared `checks/common.bash` helper provides `require_file`, `require_command`, `history_has`, and `git_has_file`.

## Validation

```bash
python -B -m unittest discover -s tests -v
```

Tests mock Docker, logind, SSH configuration, and account discovery. They do not contact real hosts or execute real milestone checks. Follow the [security golden path workflows](https://github.com/lsy-central/lsy-security-golden-path) and docSpace deployment instructions for rollout.
