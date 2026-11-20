

from __future__ import annotations

import json
import os

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_SAM4TUN_DIR = os.path.dirname(_THIS_DIR)
_REPO_ROOT = os.path.dirname(_SAM4TUN_DIR)

VALID_MODES = ("staggered", "continuous", "complex")

                                                                            
MODE_DEFAULTS: dict[str, dict[str, dict[str, object]]] = {
    "unfolding": {
        "staggered": {},
        "continuous": {},
        "complex": {
            "top_tube_radius": 3.5,
            "top_tube_top_n": 10,
        },
    },
    "denoising": {
        "staggered": {},
        "continuous": {},
        "complex": {},
    },
    "enhancing": {
        "staggered": {},
        "continuous": {},
        "complex": {},
    },
    "detecting": {
        "staggered": {
            "prompt_logic": "t12_pattern",
            "uniform_k_snap": False,
        },
        "continuous": {
            "prompt_logic": "t3_inherit",
            "uniform_k_snap": True,
        },
        "complex": {
            "prompt_logic": "t12_pattern",
            "uniform_k_snap": False,
        },
    },
    "sam": {
                                                                              
                                                                              
        "staggered": {
            "geometry_profile": "t12",
            "mirror_k_geometry": False,
            "segment_per_ring": 6,
            "segment_loop_extra": 0,
        },
        "continuous": {
            "geometry_profile": "t3",
            "mirror_k_geometry": True,
            "segment_per_ring": 6,
            "segment_loop_extra": 1,
        },
        "complex": {
            "geometry_profile": "t45",
            "segment_per_ring": 7,
            "segment_loop_extra": 1,
        },
    },
}


def _resolve_params_root(params_dir: str | None = None) -> str:

    if params_dir:
        return os.path.abspath(params_dir)
    env = (os.environ.get("PROXY4TUN_PARAMS_DIR") or "").strip()
    if env:
        return os.path.abspath(env)
    return os.path.join(_SAM4TUN_DIR, "params")


def load_family_mode(params_dir: str | None = None) -> str:

    root = _resolve_params_root(params_dir)
    path = os.path.join(root, "parameters_family.json")
    if not os.path.isfile(path):
        raise SystemExit(
            f"Missing parameters_family.json under resolved params dir: {root}. "
            "Provide it with a 'family_mode' of "
            f"{', '.join(VALID_MODES)}."
        )
    with open(path, "r") as f:
        data = json.load(f)
    mode = data.get("family_mode")
    if mode not in VALID_MODES:
        raise SystemExit(
            f"Invalid family_mode={mode!r} in {path}; "
            f"expected one of {', '.join(VALID_MODES)}"
        )
    return mode


def apply_mode_defaults(stage: str, params: dict, mode: str) -> dict:

    if mode not in VALID_MODES:
        raise SystemExit(
            f"Invalid family_mode={mode!r}; expected one of {', '.join(VALID_MODES)}"
        )
    merged = dict(params)
    defaults = MODE_DEFAULTS.get(stage, {}).get(mode, {})
    for key, value in defaults.items():
        if key not in merged:
            merged[key] = value
    return merged


def load_raw_params(stage: str, params_dir: str | None = None) -> tuple[dict, str]:

    root = _resolve_params_root(params_dir)
    path = os.path.join(root, f"parameters_{stage}.json")
    if not os.path.isfile(path):
        raise SystemExit(
            f"Missing parameters_{stage}.json under resolved params dir: {root}"
        )
    with open(path, "r") as f:
        data = json.load(f)
    return data, path


def load_stage_params(stage: str, params_dir: str | None = None) -> tuple[dict, str, str]:

    mode = load_family_mode(params_dir)
    data, path = load_raw_params(stage, params_dir)
    merged = apply_mode_defaults(stage, data, mode)
    try:
        rel = os.path.relpath(path, _REPO_ROOT)
    except ValueError:
        rel = path
    print(f"Loaded {stage} parameters from {rel} (family_mode={mode})")
    return merged, path, mode
