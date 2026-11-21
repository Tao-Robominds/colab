# sam4tun

Case-specific SAM4Tun stages for CoLab_V2.

## Layout

```text
sam4tun/
  run_stages.py              # dispatcher into a case
  sample/
  staggered/
  continuous/
  complex/
  segment-anything/
    segment_anything/
    sam_vit_h_4b8939.pth
```

Each case directory holds stages 1–6 and the helpers that case needs. Sample and staggered share the repeating-pattern block geometry. Continuous uses fixed-order prompts. Complex uses irregular seven-segment blocks and top-tube unfolding. The SAM weights stay once under `segment-anything/`.

## Run stages 1–6

From the workspace root:

```bash
export PROXY4TUN_OUT_ROOT="$PWD/data/development/1-1"
export PROXY4TUN_INPUT_TXT="$PWD/data/scans/1-1.txt"
export PROXY4TUN_PARAMS_DIR="$PWD/configs/families/staggered"
export PROXY4TUN_TUNNEL_META="$PWD/configs/meta/tunnel_meta.json"
export PROXY4TUN_SUBSET="1-1"
mkdir -p "$PROXY4TUN_OUT_ROOT"
./venv/bin/python sam4tun/run_stages.py baseline --case staggered --out-root "$PROXY4TUN_OUT_ROOT" --input "$PROXY4TUN_INPUT_TXT"
```

Or call a case directly:

```bash
export PYTHONPATH="$PWD/sam4tun/staggered:$PWD/sam4tun/segment-anything"
./venv/bin/python sam4tun/staggered/run_stages.py baseline --out-root "$PROXY4TUN_OUT_ROOT" --input "$PROXY4TUN_INPUT_TXT"
```

Stage 1 reads the design blueprint from `PROXY4TUN_TUNNEL_META` for `PROXY4TUN_SUBSET`: diameter, ring length, ring count, orientation, segment count, and K layout. A case refuses a tunnel whose segment count or K layout does not match.

Evaluation writes to `<out-root>/<tunnel_id>/evaluation/performance.md`.
