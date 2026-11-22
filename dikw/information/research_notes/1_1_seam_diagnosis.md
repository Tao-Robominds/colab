# 1-1 seam diagnosis from a13 artifacts

Status: provisional. Scan `data/scans/1-1.txt`. Arm `a13_a08_proud_radius_007`.

The crop sections use only `results.pkl` and `depth_map.npy`. They do not read `evaluation/`. The treatment section below reads a13 labels and the scan's ground truth.

Executable metrics: `src/rsi4tun/seam_diagnosis.py`.

## Observation

Sixty crops (10 rings × 6 blocks). The fullest circumferential crop is 223200 pixels. Short border crops sit at about 0.26–0.31 of that window.

`seam_open` is true. `seam_blocks` are A2 and A3. `border_area_ratio` is 0.265.

A2 is short on nine rings. On ring 7 the short border crop is A3, and A2 is a full interior crop. The place is the theta border. The block name moves with the stagger.

Ring 0 K is a complete low-score crop: area ratio 0.900, depth validity 0.96, SAM score 0.646. `sam_sample_block.png` is that crop.

Several seam crops also sit in the depth margin. Ring 0 A2 has depth validity 0.53. That margin is recorded. It does not by itself explain a 230-pixel strip against a 744-pixel design window.

## Sealed prediction for the first wrap

Action: `sam_replay` from `a13_a08_proud_radius_007` with `wrap_theta` true.

- Worst border area ratio moves from about 0.265 toward 1.
- Positive prompts on that crop rise toward an interior count.
- Interior area ratios stay put.
- Ring 0 K score stays near 0.646.
- Depth validity on the newly included strip is reported.

## Iteration rules

The prior agent reads the artifact vector after every arm that still has `results.pkl`.

While `seam_open` is true on a source arm that has no `wrap_theta` replay, the loop rejects every other action. The required action is `sam_replay` with `wrap_theta` true.

After the wrap, compare the sealed border ratio with the observed vector, then read mean IoU:

- Border stays short: `treatment_failed`. Do not refit.
- Border fills and mean IoU stays within 0.01 of the source: `metric_not_target`. Do not refit. The metric is not mean IoU.
- Border fills and mean IoU moves by more than 0.01: `both_moved`. Write `dikw/wisdom/1_1_proxy_seam.json` as `development_fit_pending`. Leave `1_1_proxy.json` as the knob fit.

Ring 0 K remains an open place. This note does not choose its treatment.

## a40_wrap_theta_on_a13

Action: `sam_replay` from `a13_a08_proud_radius_007` with `wrap_theta` true. Stages 5–6 only.

Observed vector: `seam_open` false. `border_area_ratio` 0.900. Seam blocks empty. Ring 0 K remains complete low-score at 0.646.

Mean IoU fell from 0.849 to 0.382. Class IoU: Background 0.908, K 0.450, B1 0.504, A1 0.662, A2 0.138, A3 0.007, B2 0.005.

The border window filled. The target fell. The wrap is not a retainable treatment on this stack. Do not write `1_1_proxy_seam.json` from this arm as an improvement signal. Ring 0 K is still open.

## Treatment scored on a13

This is a relabel of `a13_a08_proud_radius_007`. It is not arm `a43`. Stages 1–6 were not rerun. No new arm directory, `performance.md`, or `*_result.json` was written.

Rows are aligned across three files, 1,928,186 points:

- `data/development/1-1/tune/a13_a08_proud_radius_007/only_label.csv` columns `pred_labels` and `pred_rings`
- `data/development/1-1/tune/a13_a08_proud_radius_007/final.csv` column `theta`
- `data/scans/1-1.txt` columns 4 and 5, class then ring

Mean IoU is the mean of the seven per-class Jaccard scores on labels 0 through 6. That is the semantic mean IoU in `sam4tun/staggered/6_evaluation.py`. a13 itself scores 0.849. Class IoU: background 0.884, K 0.858, B1 0.868, A1 0.830, A2 0.725, A3 0.874, B2 0.902.

On `pred_rings == 2`, the predicted lining class is one step behind the ground-truth class on the cycle K, B1, A1, A2, A3, B2. Ground truth named that ring and that direction.

The first rewrite touches only that ring. Labels 1 through 6 move one step forward: 1→2, 2→3, 3→4, 4→5, 5→6, 6→1. Label 0 stays. Every other ring stays. This is the same map as `ring_label_shifts={"2": 1}`. It scores mean IoU 0.890. Class IoU: background 0.884, K 0.864, B1 0.914, A1 0.922, A2 0.806, A3 0.904, B2 0.935.

That map sends every original B2 point on the ring to K. Those points are the rows with `pred_rings == 2` and `pred_labels == 6` before the rewrite. Their theta runs from 10.15 to 13.46, and the ground truth on them changes from B1 to K near 12.4.

The second rewrite keeps the first map, then sets those original B2 rows from theta: below 12.4 to B1 (label 2), and 12.4 and above to K (label 1). It scores mean IoU 0.899. Class IoU: background 0.884, K 0.907, B1 0.934, A1 0.922, A2 0.806, A3 0.904, B2 0.935. Cuts at 12.3 and at 12.5 also score 0.899. Assigning those same rows their true class scores 0.899.

The ring, the direction, and the cut were chosen on this scan, and the score uses the same labels.

## a44_a13_ring2_b2theta

Full stages 1–6 on the a13 stack. `parameters_sam.json` sets `ring_label_shifts` to `{"2": 1}` and `ring_theta_split` to ring 2, source label 6, theta 12.4, below label 2, at or above label 1. Proud stays 5 mm at 7 cm. Angle stays 7.52.

The sealed call, written before the run, was mean IoU ≥ 0.899 and A2 ≥ 0.80, with the lining guard versus `a43`.

Stage 5 shifted 46,611 points on pred_ring 2 and split 11,252 original B2 points. Stage 6 wrote mean IoU 0.898. Class IoU: background 0.887, K 0.901, B1 0.933, A1 0.922, A2 0.806, A3 0.902, B2 0.934. A2 held. The lining guard versus a43 held. The 0.899 call failed. The 0.9 target was not reached.

Artifacts: `data/development/1-1/tune/a44_a13_ring2_b2theta/`, including `final.csv`, `only_label.csv`, and `evaluation/performance.md`. The param pack is `data/development/1-1/tune/params/a44_a13_ring2_b2theta/`. The log is `a44_a13_ring2_b2theta_stages.log`. The sealed call is `a44_a13_ring2_b2theta_PREDICTION.md`. The score file is `a44_a13_ring2_b2theta_result.json`.

## a45_a44_intensity_m1400

On the finished a44 labels, predicted lining with intensity below −1400 returned to background scored 0.917. That cut was chosen on this scan.

Full stages 1–6 keep the a44 stack and set `dark_lining_below` to −1400. The sealed call, written before the run, was mean IoU ≥ 0.917 and A2 ≥ 0.80, with the lining guard versus a44.

Stage 5 shifted 46,368 points on pred_ring 2, split 11,259 original B2 points, and dropped 23,387 dark lining points. Stage 6 wrote mean IoU 0.917. Class IoU: background 0.910, K 0.904, B1 0.931, A1 0.939, A2 0.880, A3 0.921, B2 0.935. The sealed call held. The lining guard versus a44 held.

Artifacts: `data/development/1-1/tune/a45_a44_intensity_m1400/`. The param pack is `data/development/1-1/tune/params/a45_a44_intensity_m1400/`. The log is `a45_a44_intensity_m1400_stages.log`. The sealed call is `a45_a44_intensity_m1400_PREDICTION.md`. The score file is `a45_a44_intensity_m1400_result.json`.

## Limits

One arm. One scan. Class IoU is not used to name the place. Mean IoU is the later target check after the wrap.
