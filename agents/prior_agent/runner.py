from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ALLOWED_SAM = {
    "mirror_k_geometry",
    "template_scale",
    "proud_residual_mm",
    "proud_radius_m",
    "K_height",
    "AB_height",
    "angle",
}
ALLOWED_DENOISE = {
    "mask_r_low",
    "mask_r_high",
    "smoothing_offset",
    "default_cutoff_z",
}
ALLOWED_ENHANCE = {
    "window_size",
    "enable_outlier_interpolation",
}
ALLOWED_FILES = {
    "parameters_sam.json": ALLOWED_SAM,
    "parameters_denoising.json": ALLOWED_DENOISE,
    "parameters_enhancing.json": ALLOWED_ENHANCE,
}
LINING_NAMES = (
    "K-block",
    "B1-block",
    "A1-block",
    "A2-block",
    "A3-block",
    "B2-block",
)


def deep_set(data: dict, patch: dict) -> None:
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(data.get(key), dict):
            deep_set(data[key], value)
        else:
            data[key] = value


def filter_overrides(overrides: dict) -> dict:
    clean: dict = {}
    for fname, patch in (overrides or {}).items():
        if fname not in ALLOWED_FILES:
            raise ValueError(f"disallowed_param_file:{fname}")
        allowed = ALLOWED_FILES[fname]
        kept = {}
        for key, value in patch.items():
            if key not in allowed:
                raise ValueError(f"disallowed_param_key:{fname}:{key}")
            kept[key] = value
        if kept:
            clean[fname] = kept
    return clean


def clone_params(family_dir: Path, dest: Path, overrides: dict) -> Path:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(family_dir, dest)
    for fname, patch in filter_overrides(overrides).items():
        path = dest / fname
        data = json.loads(path.read_text())
        deep_set(data, patch)
        path.write_text(json.dumps(data, indent=2) + "\n")
    return dest


def parse_performance(perf_path: Path) -> dict:
    text = perf_path.read_text()
    out: dict = {"classes": {}}
    in_cls = False
    for line in text.splitlines():
        if "Mean IoU (mIoU):" in line:
            out["mIoU"] = float(line.split(":")[-1].strip())
        elif line.startswith("## Per-class"):
            in_cls = True
        elif in_cls and line.startswith("##"):
            break
        elif in_cls and line.startswith("- "):
            name, val = line[2:].split(":")
            out["classes"][name.strip()] = float(val.strip())
    if "mIoU" not in out:
        raise ValueError(f"miou_missing:{perf_path}")
    return out


def load_gt_labels(scan_path: Path) -> np.ndarray:
    frame = pd.read_csv(
        scan_path,
        sep=r"\s+",
        header=None,
        usecols=[4],
        dtype=np.int32,
        engine="c",
    )
    return frame.iloc[:, 0].to_numpy()


def spill_count(run_dir: Path, scan_path: Path) -> int:
    pred = pd.read_csv(run_dir / "only_label.csv", usecols=["pred_labels"])["pred_labels"].to_numpy().astype(int)
    gt = load_gt_labels(scan_path)
    return int(((gt == 0) & (pred >= 1) & (pred <= 6)).sum())


STAGE_LOG_BYTES = 64 * 1024


def relay_output(stream, dest, max_bytes: int = STAGE_LOG_BYTES) -> None:
    kept = bytearray()
    dropped = False
    while True:
        block = stream.read(8192)
        if not block:
            break
        kept.extend(block)
        if len(kept) > max_bytes:
            dropped = True
            del kept[:-max_bytes]
    if dropped:
        dest.write(b"... earlier log dropped ...\n")
    dest.write(kept)


def lining_guard(classes: dict, baseline_classes: dict, margin: float = 0.02) -> tuple[bool, list[str]]:
    fails = []
    for name in LINING_NAMES:
        base = baseline_classes.get(name)
        got = classes.get(name)
        if base is None or got is None:
            fails.append(f"{name}: missing")
            continue
        if got < base - margin:
            fails.append(f"{name}: {got:.3f} < {base - margin:.3f}")
    return (len(fails) == 0), fails


def run_full_pipeline(
    root: Path,
    tune_root: Path,
    arm_name: str,
    params_dir: Path,
    scan_path: Path,
    subset_id: str,
) -> Path:
    dest = tune_root / arm_name
    if dest.exists():
        shutil.rmtree(dest)
    tune_root.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["MPLBACKEND"] = "Agg"
    env["PROXY4TUN_OUT_ROOT"] = str(tune_root)
    env["PROXY4TUN_INPUT_TXT"] = str(scan_path)
    env["PROXY4TUN_PARAMS_DIR"] = str(params_dir)
    env["PROXY4TUN_TUNNEL_META"] = str(root / "configs/meta/tunnel_meta.json")
    env["PROXY4TUN_SUBSET"] = subset_id
    case = "sample" if subset_id == "sample" else "staggered"
    case_root = root / "sam4tun" / case
    env["PYTHONPATH"] = os.pathsep.join(
        [str(case_root), str(root / "sam4tun/segment-anything"), env.get("PYTHONPATH", "")]
    )
    python = root / "venv/bin/python"
    exe = str(python) if python.is_file() else sys.executable
    stage_log = tune_root / f"{arm_name}_stages.log"
    command = [
        exe,
        "-u",
        str(case_root / "run_stages.py"),
        arm_name,
        "--out-root",
        str(tune_root),
        "--input",
        str(scan_path),
    ]
    proc = subprocess.Popen(
        command,
        cwd=str(root),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    assert proc.stdout is not None
    with stage_log.open("wb") as log_fp:
        relay_output(proc.stdout, log_fp)
    code = proc.wait()
    if code != 0:
        raise subprocess.CalledProcessError(code, command)
    return dest


def proud_replay(
    root: Path,
    source_dir: Path,
    dest_dir: Path,
    scan_path: Path,
    residual_mm: float = 5.0,
    radius_m: float = 0.10,
) -> Path:
    sys.path[:0] = [str(root / "sam4tun" / "staggered")]
    from helpers.proud_lining import drop_proud_lining

    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True)
    final_src = source_dir / "final.csv"
    header = pd.read_csv(final_src, nrows=0).columns.tolist()
    columns = [name for name in ("h", "theta", "r", "pred", "pred_ring") if name in header]
    df = pd.read_csv(final_src, usecols=columns)
    labels = drop_proud_lining(
        df["h"].to_numpy(),
        df["theta"].to_numpy(),
        df["r"].to_numpy(),
        df["pred"].to_numpy(),
        radius_m,
        residual_mm / 1000.0,
    )
    df["pred"] = labels
    df.to_csv(dest_dir / "final.csv", index=False)
    if "pred_ring" in df.columns:
        rings = df["pred_ring"].to_numpy()
    else:
        rings = np.full(len(df), -1, dtype=int)
    only = pd.DataFrame({"pred_labels": labels, "pred_rings": rings})
    only.to_csv(dest_dir / "only_label.csv", index=False)
    eval_dir = dest_dir / "evaluation"
    eval_dir.mkdir(parents=True)
    gt = load_gt_labels(scan_path)
    from sklearn.metrics import jaccard_score

    names = ["Background", "K-block", "B1-block", "A1-block", "A2-block", "A3-block", "B2-block"]
    ious = jaccard_score(gt, labels.astype(int), average=None, labels=list(range(7)), zero_division=0)
    miou = float(np.mean(ious))
    lines = [
        f"# Performance Metrics for Tunnel {dest_dir.name}",
        "",
        "- Segment schema: **6-class** (6-class (B2 at index 6))",
        "",
        "## Overall Metrics",
        f"- Mean IoU (mIoU): {miou:.3f}",
        "",
        "## Per-class IoU",
    ]
    for name, value in zip(names, ious):
        lines.append(f"- {name}: {float(value):.3f}")
    (eval_dir / "performance.md").write_text("\n".join(lines) + "\n")
    return dest_dir
