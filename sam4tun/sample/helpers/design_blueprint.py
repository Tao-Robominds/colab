from __future__ import annotations

import json
import os
from pathlib import Path

_HELPERS = Path(__file__).resolve().parent
_CASE_ROOT = _HELPERS.parent
_SAM4TUN_ROOT = _CASE_ROOT.parent
_REPO_ROOT = _SAM4TUN_ROOT.parent

CASE = "sample"
EXPECTED_SEGMENT_COUNT = 6
EXPECTED_K_LAYOUT = "repeating_pattern"
ALLOWED_K_LAYOUTS = ("repeating_pattern", "fixed_order", "irregular")
_REQUIRED = (
    "inner_diameter_m",
    "ring_length_m",
    "ring_count",
    "orientation_xy",
    "segment_count",
    "k_layout",
)


def _default_meta_path() -> str:
    return str(_REPO_ROOT / "configs" / "meta" / "tunnel_meta.json")


def load_design_blueprint(subset_id: str | None = None) -> dict:
    meta_path = (os.environ.get("PROXY4TUN_TUNNEL_META") or "").strip() or _default_meta_path()
    subset = (os.environ.get("PROXY4TUN_SUBSET") or "").strip() or (subset_id or "")
    if not subset:
        raise SystemExit("PROXY4TUN_SUBSET or subset_id is required for the design blueprint")
    with open(meta_path, "r", encoding="utf-8") as handle:
        meta = json.load(handle)
    entry = meta.get(subset)
    if entry is None:
        raise SystemExit(f"No design blueprint for subset {subset} in {meta_path}")
    missing = [key for key in _REQUIRED if key not in entry]
    if missing:
        raise SystemExit(f"Design blueprint for {subset} missing fields: {missing}")
    diameter = float(entry["inner_diameter_m"])
    ring_length = float(entry["ring_length_m"])
    ring_count = int(entry["ring_count"])
    segment_count = int(entry["segment_count"])
    k_layout = str(entry["k_layout"])
    orientation = entry["orientation_xy"]
    if ring_count < 1:
        raise SystemExit("ring_count must be >= 1")
    if diameter <= 0 or ring_length <= 0:
        raise SystemExit("inner_diameter_m and ring_length_m must be positive")
    if segment_count not in (6, 7):
        raise SystemExit("segment_count must be 6 or 7")
    if k_layout not in ALLOWED_K_LAYOUTS:
        raise SystemExit(f"k_layout must be one of {ALLOWED_K_LAYOUTS}")
    if segment_count != EXPECTED_SEGMENT_COUNT or k_layout != EXPECTED_K_LAYOUT:
        raise SystemExit(
            f"Tunnel {subset} has segment_count={segment_count} k_layout={k_layout}; "
            f"case {CASE} expects {EXPECTED_SEGMENT_COUNT} and {EXPECTED_K_LAYOUT}"
        )
    if not isinstance(orientation, (list, tuple)) or len(orientation) != 2:
        raise SystemExit("orientation_xy must have two components")
    ox = float(orientation[0])
    oy = float(orientation[1])
    norm = (ox * ox + oy * oy) ** 0.5
    if norm == 0.0 or not norm == norm:
        raise SystemExit("orientation_xy must be a finite non-zero vector")
    return {
        "subset_id": subset,
        "inner_diameter_m": diameter,
        "ring_length_m": ring_length,
        "ring_count": ring_count,
        "segment_count": segment_count,
        "k_layout": k_layout,
        "orientation_xy": (ox / norm, oy / norm),
    }
