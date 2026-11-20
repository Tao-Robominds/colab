# Local environment

This workspace holds a self-contained copy of the runnable SAM4Tun environment. The architecture and SOUL remain unchanged. Historical CoLab trials and proxy coefficients were not imported.

## Copied into this repository

| Path | Source | Role |
| --- | --- | --- |
| `venv/` | CoLab `venv/` | Python 3.12.12 with torch CUDA, OpenCV, faiss, numba, and related packages |
| `sam4tun/segment-anything/` | CoLab `sam4tun/segment-anything/` | Segment Anything package and ViT-H checkpoint |
| `sam4tun/` | CoLab `sam4tun/` | Stage scripts 1–6, helpers, Segment Anything, ViT-H weight |
| `pipeline/` | Proxy4Tun `pipeline/` | Stage executor used by CoLab experiments |
| `configs/families/` | CoLab `configs/families/` | Family parameter packs |
| `data/development/scans/` | CoLab scans and RSI4Tun `sample.txt` | Full six-column labelled scans |
| `data/development/meta/tunnel_meta.json` | CoLab `data/meta/tunnel_meta.json` | Drive orientation metadata |
| `data/deployment/scans/` | Derived here | Four-column scans with label and ring columns removed |

## Path rewrites after the virtualenv copy

The CoLab virtualenv still pointed at other projects. After the copy, these identities were rewritten to CoLab_V2 paths:

- Shebangs under `venv/bin`
- `VIRTUAL_ENV` in the activate scripts
- Editable finders for `segment_anything` and `sam4tun`
- Matching `direct_url.json` records
- `pyvenv.cfg` executable and command fields

`segment_anything.__file__` resolves under `sam4tun/segment-anything/`. Script shebangs and editable finders do not retain paths into CEEC, CoLab, Proxy4Tun, or RSI4Tun.

## Remaining machine substrate

`venv/bin/python` keeps a `RUNPATH` into `~/.pyenv/versions/3.12.12` and `~/.pyenv-deps`. Those libraries stay on the host. `environment.lock.json` records them.

## Development and deployment data

Development scans keep six fields: coordinates, intensity, semantic label, and ring index. Deployment scans keep the first four fields only. Deployment mounts must not include `data/development/`.

`tunnel_meta.json` holds design-blueprint fields only: inner diameter, ring length, ring count, and orientation. It is keyed by subset id. Stage 1 loads these through `sam4tun/helpers/design_blueprint.py` and uses them for diameter, slicing ring count, ring-length checks, and drive orientation.

## Excluded from this import

- Historical run trees under CoLab `data/development`, `data/deployment`, and `runs/`
- `sam4tun/data/monolith`
- `registry/proxies/` and CoLab `configs/defaults.yaml`
- Tracked copies of `.env` secrets

The synthetic demo copies the source tree into a temporary worktree. That copy excludes `venv/`, `sam4tun/segment-anything/`, `data/`, and other run archives so the fixture does not duplicate the local environment.

Machine-readable digests live in `environment.lock.json`.
