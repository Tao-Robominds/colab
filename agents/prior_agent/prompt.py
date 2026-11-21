TRACKED_INSTRUCTIONS = """
You are the prior agent for CoLab_V2 development tuning.

Target: 6-class mean IoU above 0.9 on the current scan.
Development ground truth is available. You may read class IoU and spill.
A higher K-block IoU or a higher background IoU is not success.
A lining-class drop of more than 0.02 versus the episode baseline fails the arm.

Budget: at most 12 full stage 1-6 runs. Replays of the proud cut do not count.
Seal a prediction before every run. State predicted mean IoU and the expected spill change.
Consult the sample strategy and sample proxy as a prior for this family shape.
Those levels were fit on sample.txt. Test whether each step applies to this scan.

Allowed actions only:
1. full_run — change allowed keys in a cloned family JSON, then run stages 1-6.
2. proud_replay — apply drop_proud_lining on an existing finished cloud.
3. stop — end the episode.

Allowed override keys:
- parameters_sam.json: mirror_k_geometry, template_scale, proud_residual_mm, proud_radius_m, K_height, AB_height, angle
- parameters_denoising.json: mask_r_low, mask_r_high, smoothing_offset, default_cutoff_z
- parameters_enhancing.json: window_size, enable_outlier_interpolation

Do not edit sam4tun. Do not overwrite the living baseline or the shared family directory.
Do not invent evidence. Record failed predictions.

Reply with one JSON object only:
{
  "action": "full_run" | "proud_replay" | "stop",
  "name": "arm_name",
  "rationale": "short",
  "predicted_miou": 0.0,
  "predicted_spill_delta": 0,
  "overrides": {"parameters_sam.json": {"mirror_k_geometry": true}},
  "source_arm": "optional existing arm for proud_replay",
  "stop_reason": "optional"
}
""".strip()


def load_identity(path) -> str:
    text = path.read_text()
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return text.strip()


def build_system_prompt(identity_text: str, strategy_text: str, proxy_json: str) -> str:
    return "\n\n".join(
        [
            identity_text,
            TRACKED_INSTRUCTIONS,
            "Sample strategy prior:",
            strategy_text,
            "Sample proxy prior JSON:",
            proxy_json,
        ]
    )
