from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Callable

from prior_agent.client import OpusClient, parse_action
from prior_agent.dikw import (
    features_from_action,
    maybe_refit_1_1_proxy,
    record_arm,
)
from prior_agent.prompt import build_system_prompt, load_identity
from prior_agent.runner import (
    clone_params,
    lining_guard,
    parse_performance,
    proud_replay,
    run_full_pipeline,
    spill_count,
)


ChatFn = Callable[[list[dict[str, str]]], str]
RunFullFn = Callable[[Path, Path, str, Path, Path, str], Path]
ProudFn = Callable[[Path, Path, Path, Path, float, float], Path]


def evidence_message(
    tunnel_id: str,
    baseline: dict,
    history: list[dict],
    full_runs_left: int,
    target: float,
    notice: dict | None = None,
) -> str:
    payload = {
        "tunnel_id": tunnel_id,
        "target_miou": target,
        "full_runs_left": full_runs_left,
        "baseline": baseline,
        "history": history,
    }
    if notice:
        payload["notice"] = notice
    return json.dumps(payload, indent=2)


def seal_prediction(path: Path, action: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    required = ("action", "predicted_miou", "rationale")
    for key in required:
        if key not in action:
            raise ValueError(f"prediction_missing:{key}")
    path.write_text(json.dumps(action, indent=2) + "\n")


def prediction_held(action: dict, miou: float, tolerance: float = 0.02) -> bool:
    predicted = float(action["predicted_miou"])
    return abs(predicted - miou) <= tolerance


DEFAULT_FEATURES = {
    "k_wedge": 0.0,
    "angle_positive": 1.0,
    "ab_rel_error": 0.0,
    "proud_cut": 0.0,
}


def load_completed(tune_root: Path) -> list[dict]:
    entries = []
    for path in sorted(tune_root.glob("*_result.json")):
        entry = json.loads(path.read_text())
        if not entry.get("name"):
            entry["name"] = path.name[: -len("_result.json")]
        entries.append(entry)
    return entries


def clear_incomplete_arm(tune_root: Path, name: str) -> None:
    if (tune_root / f"{name}_result.json").is_file():
        return
    arm_dir = tune_root / name
    if arm_dir.exists():
        shutil.rmtree(arm_dir)
    pred = tune_root / f"{name}_PREDICTION.md"
    if pred.is_file():
        pred.unlink()
    params = tune_root / "params" / name
    if params.exists():
        shutil.rmtree(params)


def run_episode(
    root: Path,
    tunnel_id: str = "1-1",
    target: float = 0.9,
    max_full_runs: int = 12,
    chat: ChatFn | None = None,
    run_full: RunFullFn | None = None,
    run_proud: ProudFn | None = None,
) -> dict:
    root = root.resolve()
    tune_root = root / "data/development" / tunnel_id / "tune"
    tune_root.mkdir(parents=True, exist_ok=True)
    family_dir = root / "configs/families/staggered"
    if tunnel_id == "sample":
        family_dir = root / "configs/families/sample"
    scan_path = root / "data/scans" / f"{tunnel_id}.txt"
    baseline_perf = parse_performance(
        root / "data/development" / tunnel_id / "baseline/evaluation/performance.md"
    )
    baseline_spill = spill_count(
        root / "data/development" / tunnel_id / "baseline",
        scan_path,
    )
    baseline = {
        "mIoU": baseline_perf["mIoU"],
        "classes": baseline_perf["classes"],
        "spill": baseline_spill,
    }
    identity = load_identity(root / ".cursor/rules/private/identity.mdc")
    strategy = (root / "dikw/wisdom/sample_tune_strategy.md").read_text()
    sample_proxy_path = root / "dikw/wisdom/sample_proxy.json"
    proxy_json = sample_proxy_path.read_text()
    system = build_system_prompt(identity, strategy, proxy_json)
    if chat is None:
        client = OpusClient(root)
        chat = client.complete
    if run_full is None:
        run_full = run_full_pipeline
    if run_proud is None:
        run_proud = proud_replay

    history = load_completed(tune_root)
    done_names = {entry["name"] for entry in history}
    for path in sorted(tune_root.glob("*_PREDICTION.md")):
        name = path.name[: -len("_PREDICTION.md")]
        if name not in done_names:
            clear_incomplete_arm(tune_root, name)
    proxy_rows: list[dict] = [
        {
            "run_id": "baseline",
            "features": dict(DEFAULT_FEATURES),
            "miou": baseline["mIoU"],
            "is_baseline": True,
        }
    ]
    full_runs = 0
    best = {"name": "baseline", "mIoU": baseline["mIoU"]}
    for entry in history:
        if entry.get("action") == "full_run":
            full_runs += 1
        if entry.get("mIoU", 0) > best["mIoU"] and entry.get("guard_ok", True):
            best = {"name": entry["name"], "mIoU": entry["mIoU"]}
        pred_path = tune_root / f"{entry['name']}_PREDICTION.md"
        action = json.loads(pred_path.read_text()) if pred_path.is_file() else entry
        feats = features_from_action(action, dict(DEFAULT_FEATURES))
        proxy_rows.append(
            {
                "run_id": entry["name"],
                "features": feats,
                "miou": entry["mIoU"],
                "is_baseline": False,
            }
        )
    system_message = {"role": "system", "content": system}
    notice = None

    while full_runs < max_full_runs and best["mIoU"] < target:
        raw = chat(
            [
                system_message,
                {
                    "role": "user",
                    "content": evidence_message(
                        tunnel_id,
                        baseline,
                        history,
                        max_full_runs - full_runs,
                        target,
                        notice,
                    ),
                },
            ]
        )
        notice = None
        action = parse_action(raw)
        name = str(action.get("name") or f"arm_{len(history) + 1}")
        if name in done_names:
            notice = {
                "error": "arm_name_already_scored",
                "name": name,
                "hint": "Choose a new name. Completed arms are in history.",
            }
            continue
        prediction_path = tune_root / f"{name}_PREDICTION.md"
        seal_prediction(prediction_path, action)
        if not prediction_path.is_file():
            raise RuntimeError("prediction_not_sealed")

        kind = action.get("action")
        if kind == "stop":
            history.append(
                {
                    "name": name,
                    "action": "stop",
                    "stop_reason": action.get("stop_reason", ""),
                    "predicted_miou": action.get("predicted_miou"),
                }
            )
            break

        if kind == "full_run":
            params_dir = clone_params(
                family_dir,
                tune_root / "params" / name,
                action.get("overrides") or {},
            )
            run_dir = run_full(
                root,
                tune_root,
                name,
                params_dir,
                scan_path,
                tunnel_id,
            )
            full_runs += 1
        elif kind == "proud_replay":
            source = action.get("source_arm") or "baseline"
            if source == "baseline":
                source_dir = root / "data/development" / tunnel_id / "baseline"
            else:
                source_dir = tune_root / source
            residual = float(
                ((action.get("overrides") or {}).get("parameters_sam.json") or {}).get(
                    "proud_residual_mm", 5
                )
            )
            radius = float(
                ((action.get("overrides") or {}).get("parameters_sam.json") or {}).get(
                    "proud_radius_m", 0.10
                )
            )
            run_dir = run_proud(
                root,
                source_dir,
                tune_root / name,
                scan_path,
                residual,
                radius,
            )
        else:
            raise ValueError(f"unknown_action:{kind}")

        metrics = parse_performance(run_dir / "evaluation" / "performance.md")
        spill = spill_count(run_dir, scan_path)
        guard_ok, guard_fails = lining_guard(metrics["classes"], baseline["classes"])
        held = prediction_held(action, metrics["mIoU"])
        record_arm(
            root / "dikw",
            name,
            action,
            metrics,
            spill,
            guard_ok,
            guard_fails,
            held,
        )
        feats = features_from_action(action, dict(DEFAULT_FEATURES))
        proxy_rows.append(
            {
                "run_id": name,
                "features": feats,
                "miou": metrics["mIoU"],
                "is_baseline": False,
            }
        )
        maybe_refit_1_1_proxy(
            root / "dikw/wisdom",
            sample_proxy_path,
            proxy_rows,
            feats,
            metrics["mIoU"],
        )
        entry = {
            "name": name,
            "action": kind,
            "predicted_miou": action.get("predicted_miou"),
            "mIoU": metrics["mIoU"],
            "spill": spill,
            "guard_ok": guard_ok,
            "guard_fails": guard_fails,
            "prediction_held": held,
            "classes": metrics["classes"],
        }
        history.append(entry)
        done_names.add(name)
        (tune_root / f"{name}_result.json").write_text(json.dumps(entry, indent=2) + "\n")
        if metrics["mIoU"] > best["mIoU"] and guard_ok:
            best = {"name": name, "mIoU": metrics["mIoU"]}
        (tune_root / "progress.json").write_text(
            json.dumps(
                {
                    "best": best,
                    "full_runs": full_runs,
                    "last": entry,
                    "completed": len(history),
                },
                indent=2,
            )
            + "\n"
        )
        if metrics["mIoU"] >= target and guard_ok:
            break

    summary = {
        "tunnel_id": tunnel_id,
        "target": target,
        "reached_target": best["mIoU"] >= target,
        "best": best,
        "full_runs": full_runs,
        "history": history,
    }
    (tune_root / "episode_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (tune_root / "progress.json").write_text(
        json.dumps({"best": best, "full_runs": full_runs, "completed": len(history), "done": True}, indent=2)
        + "\n"
    )
    return summary
