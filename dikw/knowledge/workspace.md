# Workspace map

All substantive prose is stored under `dikw/`. The root `README.md` is an entry link.

| Location | Contents |
| --- | --- |
| `src/rsi4tun/contracts.py` | Complete-run evidence and integrity checks |
| `src/rsi4tun/adapters.py` | Executable synthetic pipeline and real SAM4Tun adapter boundary |
| `src/rsi4tun/evidence.py` | Typed artefacts, applicability checks and programmatic reference comparisons |
| `src/rsi4tun/proxy.py` | Comparison-derived signal records, ridge fitting, validation and proxy release |
| `src/rsi4tun/hypotheses.py` and `diagnosis.py` | Executable response models, prospective plans and observed-response assessment |
| `src/rsi4tun/orchestrator.py` | Registered execution, frozen treatment decisions and coverage actions |
| `src/rsi4tun/versions.py` | Complete Git snapshots, execution receipts and accepted-release pointers |
| `src/rsi4tun/records.py` | RST integrity, GT field guards and knowledge eligibility |
| `src/rsi4tun/researcher.py` | Structured LLM context and replaceable researcher interface |
| `src/rsi4tun/evaluation.py` | Private final 3D semantic mIoU evaluation |
| `src/rsi4tun/quality.py` | Comment and docstring audit |
| `src/rsi4tun/demo.py` and `cli.py` | Reproducible synthetic demonstration and commands |
| `configs/` | Machine-readable experiment and comparison policies |
| `configs/families/` | Family parameter packs for the real stage runner |
| `sam4tun/` | Parameterized stages 1–6, helpers (family_io, geometry, IO), Segment Anything package, and ViT-H weight |
| `venv/` | Local Python environment with CUDA torch |
| `data/scans/` | Six-column labelled scans shared by stage runs |
| `data/meta/` | Shared tunnel design-blueprint metadata |
| `data/development/` | Local development run outputs |
| `data/deployment/` | Deployment run outputs |
| `environment.lock.json` | Digests and substrate pins for the local environment |
| `dikw/` | Data, information, knowledge, and wisdom layers |
| `dikw/data/` | Experiment data summaries (filled later) |
| `dikw/information/` | Organised experiment information (filled later) |
| `dikw/knowledge/` | Specifications, assumptions, hypotheses, prompts, provisional notes and verification |
| `dikw/knowledge/environment.md` | Copy list, path rewrites, and GT isolation notes |
| `dikw/wisdom/` | Acceptance rules for scoped principles; no accepted research wisdom is supplied |
| `tests/` | Meaningful evidence, validation, protocol, integrity and source-version tests |

Create run archives outside the source repository. The demo produces separate `runs/`, `evidence/`, `evaluator/`, `rst/`, `archive/` and `development_private/` directories. Real deployment must not mount the private development directory.

An accepted release identifies the complete code revision and its exact tree. The evidence archive and private data do not become source files merely because they are needed for reproducibility. Their identities and availability belong in the release manifest.
