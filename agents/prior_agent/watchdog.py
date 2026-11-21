from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path


def write_status(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n")


def trim_log(path: Path, max_bytes: int = 2_000_000, keep_lines: int = 200) -> None:
    if not path.is_file() or path.stat().st_size <= max_bytes:
        return
    lines = path.read_text(errors="replace").splitlines()
    path.write_text("\n".join(lines[-keep_lines:]) + "\n")


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    tunnel_id = os.environ.get("PRIOR_TUNNEL_ID", "1-1")
    target = os.environ.get("PRIOR_TARGET", "0.9")
    max_full_runs = os.environ.get("PRIOR_MAX_FULL_RUNS", "12")
    tune_root = root / "data/development" / tunnel_id / "tune"
    tune_root.mkdir(parents=True, exist_ok=True)
    summary_path = tune_root / "episode_summary.json"
    status_path = tune_root / "watchdog_status.json"
    log_path = tune_root / "agent.log"
    pid_path = tune_root / "watchdog.pid"
    pid_path.write_text(str(os.getpid()) + "\n")

    restarts = 0
    python = root / "venv/bin/python"
    exe = str(python) if python.is_file() else sys.executable
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [str(root / "agents"), str(root / "src"), env.get("PYTHONPATH", "")]
    )
    env["MPLBACKEND"] = "Agg"

    while not summary_path.is_file():
        trim_log(log_path)
        restarts += 1
        started = time.time()
        write_status(
            status_path,
            {
                "state": "running",
                "restarts": restarts,
                "started_at": started,
                "pid": os.getpid(),
                "tunnel_id": tunnel_id,
            },
        )
        with log_path.open("a") as log_fp:
            log_fp.write(f"\n--- watchdog start #{restarts} at {time.ctime()} ---\n")
            log_fp.flush()
            proc = subprocess.Popen(
                [
                    exe,
                    "-u",
                    "-m",
                    "prior_agent",
                    "--root",
                    str(root),
                    "--tunnel-id",
                    tunnel_id,
                    "--target",
                    str(target),
                    "--max-full-runs",
                    str(max_full_runs),
                ],
                cwd=str(root),
                env=env,
                stdout=log_fp,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
            (tune_root / "agent.pid").write_text(str(proc.pid) + "\n")
            code = proc.wait()
        write_status(
            status_path,
            {
                "state": "restarting" if not summary_path.is_file() else "done",
                "restarts": restarts,
                "last_exit_code": code,
                "last_elapsed_s": round(time.time() - started, 1),
                "pid": os.getpid(),
                "tunnel_id": tunnel_id,
            },
        )
        if summary_path.is_file():
            break
        time.sleep(min(15 + restarts * 5, 120))

    write_status(
        status_path,
        {
            "state": "done",
            "restarts": restarts,
            "pid": os.getpid(),
            "tunnel_id": tunnel_id,
            "summary": str(summary_path),
        },
    )
    return 0


if __name__ == "__main__":
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    raise SystemExit(main())
