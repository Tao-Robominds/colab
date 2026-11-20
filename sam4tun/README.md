# sam4tun

End-to-end SAM4Tun stages for CoLab_V2.

## Layout

```text
sam4tun/
  1_unfolding.py
  2_denoising.py
  3_enhancing.py
  4_detection.py
  5_sam.py
  6_evaluation.py
  run_stages.py
  helpers/
    design_blueprint.py
    family_io.py
    pipeline_io.py
    pipeline_state.py
    t12_geometry.py
    t3_geometry.py
    t45_geometry.py
  segment-anything/
    segment_anything/
    sam_vit_h_4b8939.pth
    LICENSE
```

## Run stages 1–6

From the workspace root:

```bash
export PROXY4TUN_OUT_ROOT="$PWD/data/development/1-1"
export PROXY4TUN_INPUT_TXT="$PWD/data/development/scans/1-1.txt"
export PROXY4TUN_PARAMS_DIR="$PWD/configs/families/staggered"
export PROXY4TUN_TUNNEL_META="$PWD/data/development/meta/tunnel_meta.json"
export PROXY4TUN_SUBSET="1-1"
export PYTHONPATH="$PWD/sam4tun:$PWD/sam4tun/segment-anything"
mkdir -p "$PROXY4TUN_OUT_ROOT"
./venv/bin/python sam4tun/run_stages.py baseline --out-root "$PROXY4TUN_OUT_ROOT" --input "$PROXY4TUN_INPUT_TXT"
```

Or run one stage:

```bash
./venv/bin/python sam4tun/1_unfolding.py baseline
```

`1_unfolding.py` reads design blueprint fields from `PROXY4TUN_TUNNEL_META` for the active `PROXY4TUN_SUBSET`: diameter, ring length, ring count, and orientation. Family parameter packs load through `helpers/family_io.py` from `PROXY4TUN_PARAMS_DIR`.

Evaluation writes to `<out-root>/<tunnel_id>/evaluation/performance.md`.
