#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

CASES = ("sample", "staggered", "continuous", "complex")
SAM4TUN_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SAM4TUN_ROOT.parent


def resolve_case(tunnel_id: str, case: str | None) -> str:
    if case:
        if case not in CASES:
            raise SystemExit(f"unknown case {case!r}; expected one of {CASES}")
        return case
    if tunnel_id == "sample":
        return "sample"
    if tunnel_id.startswith("1-") or tunnel_id.startswith("2-"):
        return "staggered"
    if tunnel_id.startswith("3-"):
        return "continuous"
    if tunnel_id.startswith("4-") or tunnel_id.startswith("5-"):
        return "complex"
    raise SystemExit(
        f"cannot infer case for tunnel_id={tunnel_id!r}; pass --case "
        f"({'|'.join(CASES)})"
    )


def run_stages(
    tunnel_id: str,
    *,
    case: str | None = None,
    through_stage: int = 6,
    out_root: Path | None = None,
    input_txt: Path | None = None,
) -> Path:
    chosen = resolve_case(tunnel_id, case)
    script = SAM4TUN_ROOT / chosen / "run_stages.py"
    cmd = [sys.executable, "-u", str(script), tunnel_id, "--through-stage", str(through_stage)]
    if out_root is not None:
        cmd.extend(["--out-root", str(Path(out_root).resolve())])
    if input_txt is not None:
        cmd.extend(["--input", str(Path(input_txt).resolve())])
    env = os.environ.copy()
    env["MPLBACKEND"] = env.get("MPLBACKEND", "Agg")
    subprocess.run(cmd, cwd=str(REPO_ROOT), env=env, check=True)
    root = Path(out_root).resolve() if out_root is not None else Path(
        env.get("PROXY4TUN_OUT_ROOT", SAM4TUN_ROOT / chosen / "data")
    )
    return root / tunnel_id


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("tunnel_id")
    parser.add_argument("--case", choices=CASES, default=None)
    parser.add_argument("--through-stage", type=int, default=6, choices=range(1, 7))
    parser.add_argument("--out-root", type=Path, default=None)
    parser.add_argument("--input", type=Path, default=None)
    args = parser.parse_args(argv)
    path = run_stages(
        args.tunnel_id,
        case=args.case,
        through_stage=args.through_stage,
        out_root=args.out_root,
        input_txt=args.input,
    )
    print(path)


if __name__ == "__main__":
    main()
