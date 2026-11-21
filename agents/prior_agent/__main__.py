from __future__ import annotations

import argparse
import json
from pathlib import Path

from prior_agent.loop import run_episode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prior_agent")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--tunnel-id", default="1-1")
    parser.add_argument("--target", type=float, default=0.9)
    parser.add_argument("--max-full-runs", type=int, default=12)
    args = parser.parse_args(argv)
    summary = run_episode(
        args.root,
        tunnel_id=args.tunnel_id,
        target=args.target,
        max_full_runs=args.max_full_runs,
    )
    print(
        json.dumps(
            {
                "reached_target": summary["reached_target"],
                "best": summary["best"],
                "full_runs": summary["full_runs"],
                "arms": len(summary["history"]),
            }
        ),
        flush=True,
    )
    return 0 if summary["reached_target"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
