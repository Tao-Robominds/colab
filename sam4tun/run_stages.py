#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

STAGES = [
    "1_unfolding.py",
    "2_denoising.py",
    "3_enhancing.py",
    "4_detection.py",
    "5_sam.py",
    "6_evaluation.py",
]
SAM4TUN_ROOT = Path(__file__).resolve().parent


def run_stages(
    tunnel_id: str,
    *,
    through_stage: int = 6,
    out_root: Path | None = None,
    input_txt: Path | None = None,
) -> Path:
    if not 1 <= through_stage <= 6:
        raise ValueError("through_stage must be between 1 and 6")
    env = os.environ.copy()
    if out_root is not None:
        env["PROXY4TUN_OUT_ROOT"] = str(Path(out_root).resolve())
    if input_txt is not None:
        env["PROXY4TUN_INPUT_TXT"] = str(Path(input_txt).resolve())
    env["PYTHONPATH"] = os.pathsep.join(
        [
            str(SAM4TUN_ROOT),
            str(SAM4TUN_ROOT / "segment-anything"),
            env.get("PYTHONPATH", ""),
        ]
    ).rstrip(os.pathsep)
    env["MPLBACKEND"] = env.get("MPLBACKEND", "Agg")
    for stage in STAGES[:through_stage]:
        script = SAM4TUN_ROOT / stage
        print(f"\n=== {stage} ===", flush=True)
        subprocess.run(
            [sys.executable, "-u", str(script), tunnel_id],
            cwd=str(SAM4TUN_ROOT.parent),
            env=env,
            check=True,
        )
    root = Path(env.get("PROXY4TUN_OUT_ROOT", SAM4TUN_ROOT / "data"))
    return root / tunnel_id


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("tunnel_id")
    parser.add_argument("--through-stage", type=int, default=6, choices=range(1, 7))
    parser.add_argument("--out-root", type=Path, default=None)
    parser.add_argument("--input", type=Path, default=None)
    args = parser.parse_args(argv)
    path = run_stages(
        args.tunnel_id,
        through_stage=args.through_stage,
        out_root=args.out_root,
        input_txt=args.input,
    )
    print(path)


if __name__ == "__main__":
    main()
