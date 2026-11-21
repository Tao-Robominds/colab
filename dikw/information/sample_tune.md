# What the sample tune was

The measurements are in `dikw/data/sample_tune.md`. This page says what those trials held fixed, and which comparisons are valid.

## Question

The tune tried to raise 6-class mean IoU above 0.9 on `data/scans/sample.txt`.

`data/development/sample/tune/SUMMARY.md` states that goal. It states a budget of about 20 trials. The folder contains the original 22 trial directories plus three full-pipeline arms, t23–t25.

## What the first 20 trials held fixed

`run_trial.py` copies the pre-SAM baseline into each trial. The copy includes depth, the unwrapped cloud, the denoised cloud, the enhanced cloud, and the detected-line image.

A `detect` trial then runs detection, SAM, and evaluation.

An `oracle_gt` trial replaces each prompt's ring position with the median of the ground-truth K points on that ring. It then runs SAM and evaluation. It does not run detection again.

Stages 1, 2, and 3 stay at the copied baseline for these 20 trials. `run_trial.py` does not call `1_unfolding.py`, `2_denoising.py`, or `3_enhancing.py`. The unwrapped cloud, the denoised cloud, the enhanced cloud, and `depth_map.npy` have one hash each across t01–t20. A score change in that set is a change in detection, in SAM, or in the prompt file.

The SAM settings at the start were angle 7.52, AB height 3239.77, segment width 1200, and K height 1079.92.

## How to read the trials

The literal overrides are in `results.jsonl` and in `tune/params/`. The groups below are the comparisons.

**Handedness.** `t03_mirror_k` sets `mirror_k_geometry` to true. K height stays 1079.92.

**Reversed template angle.** `t02_angle_neg` sets angle to −7.52. `t04_angle_neg_mirror` sets that angle and turns the mirror on.

**Detector signs.** `t08_mirror_detect_swap` swaps the two oblique ranges in `parameters_detecting.json`. The mirror is on.

**Prompts.** `t01_oracle_gt` uses ground-truth prompts and leaves the mirror off. `t15_oracle_mirror_kh1120` uses ground-truth prompts with the mirror on and K height 1120. `t09_kh_1120` is the detector at that same SAM geometry.

**Block height.** `t12_kh1100_ab3300` sets AB height to 3300. `t20_ab3200` sets AB height to 3200.

**Local SAM search.** These trials keep the mirror on and move one SAM control: K height 1080, 1100, 1120, or 1150; angle 7.0, 7.8, or 8.0; segment width 1250; padding 200; crop margin 30; taper 500 mm; y bounds from 4000 to 13500.

**Denoise.** `t21_denoise_tight` and `t22_denoise_mid` are outside that runner. Each directory holds a full pipeline under `baseline/`. They have no `params/` copy and no line in `results.jsonl`. `SUMMARY.md` says the tight mask is radius 2.735 to 2.76, and the mid mask is radius 2.72 to 2.78. It says both use the mirror and K height 1120. I cannot recover those mask numbers from a saved parameter file.

Aligned on `x, y, z`, both clouds still contain the t01 points. Derived `r`, `θ`, and `h` differ. Denoise `pred` differs on 33,843 points in the tight run and on 5,389 points in the mid run. Stages 1 to 3 did not stay fixed for these two trials.

`SUMMARY.md` also says an offline radial clamp reached about 0.897. I did not recompute that clamp. I leave it out of the measurements.

**Stage 1–3 unlock, t23–t25.** Predictions were sealed in `STAGE13_PREDICTIONS.md` before the runs. `run_full_arm.py` clones `configs/families/sample` into `tune/params/<name>`, then runs stages 1 through 6 into `tune/<name>/baseline`. SAM stays at the retained settings. The denoise band stays 2.72–2.78. Unfolding parameters stay unchanged. The living `data/development/sample/baseline` is not overwritten.

Arm A (`t23_enhance_no_outlier`) sets `enable_outlier_interpolation` to false.

Arm B (`t24_enhance_window3`) sets `window_size` to 3 and leaves interpolation on.

Arm C (`t25_denoise_offset_p005`) sets `smoothing_offset` to +0.005.

**Template inset, t26.** The prediction is in `TEMPLATE_PREDICTION.md`, written before the run. Stages 1–4 are the `t22_denoise_mid/baseline` copies. `template_scale` 0.97 moves each SAM template vertex 3% of the way toward the prompt centre. `5_sam.py` reads that scale. The default, when the key is absent, is 1. The family file in `configs/families/sample` is unchanged.

**Assignment abstention, t27–t28.** The prediction is in `ASSIGNMENT_PREDICTION.md`, written before the score. `replay_assignment.py` reads `t22_denoise_mid/baseline/results.pkl` and rebuilds the label map. Arm D (`t27_overlap_abstain`) sets a pixel to background when two masks cover it. Arm E (`t28_margin_abstain`) sets a pixel to background when the top two logits differ by less than 1.0. Stages 1–5 are not rerun. `5_sam.py` stays on the highest-logit rule.

**Radius residual, t29–t30.** The prediction is in `RADIUS_PREDICTION.md`, written before each score. Both arms start from the t22 point labels. The neighbourhood is 10 cm in `(h, θ)`, with `θ` wrapped by `2π` times the median radius. Arm F (`t29_radius_abs_5mm`) returns a point to background when the absolute residual exceeds 5 mm. That arm takes the median of the 64 nearest lining points inside the neighbourhood. Arm G (`t30_proud_5mm`) returns a point to background only when the radius exceeds the median of every other predicted lining point in the neighbourhood by more than 5 mm. `drop_proud_lining` implements Arm G. `5_sam.py` calls it when `proud_residual_mm` is set. The sample family sets 5 mm and a 10 cm neighbourhood. Other families leave the key unset, so the call does not run.

## Which baseline to cite

`configs/families/sample` now sets the mirror on, K height to 1120, and the denoise mask to 2.72–2.78.

`data/development/sample/baseline` currently scores 0.896. Those class scores match `t22_denoise_mid`.

I use `baseline_before_tune_performance.md` when I compare a trial with the start of the tune.
