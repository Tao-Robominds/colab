from __future__ import annotations

import json
import os
from pathlib import Path

_HELPERS = Path(__file__).resolve().parent
_CASE_ROOT = _HELPERS.parent
_SAM4TUN_ROOT = _CASE_ROOT.parent
_REPO_ROOT = _SAM4TUN_ROOT.parent

CASE = "complex"
CASE_DEFAULTS = {'unfolding': {'top_tube_radius': 3.5, 'top_tube_top_n': 10}, 'denoising': {}, 'enhancing': {}, 'detecting': {}, 'sam': {'mirror_k_geometry': False, 'segment_per_ring': 7, 'extra_ring_segments': 1}}


def _resolve_params_root(params_dir: str | None = None) -> str:
    if params_dir:
        return os.path.abspath(params_dir)
    env = (os.environ.get("PROXY4TUN_PARAMS_DIR") or "").strip()
    if env:
        return os.path.abspath(env)
    return str(_REPO_ROOT / "configs" / "families" / "complex")


def load_family_mode(params_dir: str | None = None) -> str:
    root = _resolve_params_root(params_dir)
    path = os.path.join(root, "parameters_family.json")
    if not os.path.isfile(path):
        raise SystemExit(f"Missing parameters_family.json under {root}")
    with open(path, "r") as handle:
        data = json.load(handle)
    mode = data.get("family_mode")
    if mode not in ("staggered", "continuous", "complex"):
        raise SystemExit(f"Invalid family_mode={mode!r} in {path}")
    if CASE == "sample":
        if mode != "staggered":
            raise SystemExit(f"sample case expects family_mode staggered, got {mode!r}")
    elif mode != CASE:
        raise SystemExit(f"case {CASE} expects family_mode {CASE}, got {mode!r}")
    return CASE


def apply_case_defaults(stage: str, params: dict) -> dict:
    merged = dict(params)
    for key, value in CASE_DEFAULTS.get(stage, {}).items():
        if key not in merged:
            merged[key] = value
    if "segment_loop_extra" in merged and "extra_ring_segments" not in merged:
        merged["extra_ring_segments"] = merged["segment_loop_extra"]
    return merged


def load_raw_params(stage: str, params_dir: str | None = None) -> tuple[dict, str]:
    root = _resolve_params_root(params_dir)
    path = os.path.join(root, f"parameters_{stage}.json")
    if not os.path.isfile(path):
        raise SystemExit(f"Missing parameters_{stage}.json under {root}")
    with open(path, "r") as handle:
        data = json.load(handle)
    return data, path


def load_stage_params(stage: str, params_dir: str | None = None) -> tuple[dict, str, str]:
    mode = load_family_mode(params_dir)
    data, path = load_raw_params(stage, params_dir)
    merged = apply_case_defaults(stage, data)
    try:
        rel = os.path.relpath(path, _REPO_ROOT)
    except ValueError:
        rel = path
    print(f"Loaded {stage} parameters from {rel} (case={mode})")
    return merged, path, mode
