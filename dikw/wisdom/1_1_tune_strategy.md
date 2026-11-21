# 1-1 tune strategy

Scope: family `staggered`. Scan `data/scans/1-1.txt`.

Status: a prior for the next diagnosis on this scan. It is not an accepted principle. `configs/protocol.json` still lists no accepted wisdom.

The fitted formula is [`1_1_proxy.json`](1_1_proxy.json). The scores are in [`dikw/data/1_1_tune.md`](../data/1_1_tune.md). What each arm held fixed is in [`dikw/information/1_1_tune.md`](../information/1_1_tune.md).

The sample strategy remains the prior for `data/scans/sample.txt`. It is not the level on this scan. The sample replay scored 0.902. The best arm here scored 0.891 on `a43_ring2_shift_proud_r10_6mm`. The 0.9 target was not reached. Config chase is closed.

## Fitted formula

The target is 6-class mean IoU.

The features are `k_wedge`, `angle_positive`, `ab_rel_error`, and `proud_cut`.

The equation is the standardised ridge already implemented by `FrozenProxy.predict`:

```
clip(intercept + sum(weight_i * (x_i - centre_i) / scale_i), 0, 1)
```

The coefficients live in the JSON. Prose does not replace them.

The formula does not see the radial mask, template scale, K height, the proud neighbourhood, or the denoise offset. Those results stay as stops below.

## Steps

### 1. Turn the K mirror on

Action: set `mirror_k_geometry` to true before any other SAM knob.

Prediction: mean IoU rises from 0.785. K-block IoU leaves 0.72.

Rationale: `a01_mirror_k` scored 0.796. K-block IoU rose from 0.716 to 0.797.

Stop: if K-block IoU stays near 0.72 after the mirror is on, stop before another SAM search.

### 2. Drop proud lining points at 5 mm and 10 cm

Action: after labels exist, return a predicted lining point to background when it stands more than 5 mm proud of other predicted lining points within 10 cm in `(h, θ)`.

Prediction: on the mirrored cloud, mean IoU rises and the lining guard holds. A 3 mm residual does not.

Rationale: `a02_proud_on_a01` scored 0.810 and cut spill from 89,898 to 59,628. `a05_proud3_on_a01` scored 0.778 and failed the guard.

Stop: do not tighten the residual below 5 mm on this scan.

### 3. Leave the template scale at 1

Action: do not set `template_scale` to 0.97 or to 1.03.

Prediction: neither scale raises mean IoU above the 5 mm replay.

Rationale: `a03_template_scale_103` scored 0.774 and failed the guard. `a04_scale097_mirror_proud` scored 0.800. The guard held. The score stayed below `a02`.

Stop: do not spend another full run on template scale.

### 4. Keep the mid radial mask

Action: set the denoise mask to 2.72–2.78 and keep the mirror and the 5 mm cut.

Prediction: mean IoU leaves the 0.81 band. A wider mask does not open a new band.

Rationale: `a06_mid_mask_mirror_proud` scored 0.846. `a10_a08_mask_wide_270_280` scored 0.848.

Stop: do not drop the mid mask to chase a wider proud neighbourhood.

### 5. Stop the local search on that stack

Action: once the mirror, the mid mask, and the 5 mm cut are on, stop moving K height, window size, outlier interpolation, smoothing offset, and the proud neighbourhood inside 7–10 cm.

Prediction: those knobs stay between mean IoU 0.846 and 0.849.

Rationale: `a07` scored 0.848. `a08` scored 0.848. `a09` scored 0.848. `a12` scored 0.847. `a13_a08_proud_radius_007` scored 0.849.

Stop: do not treat a move inside 0.003 as a new lever.

### 6. Do not replace the mid mask with a wider proud neighbourhood

Action: do not set `proud_radius_m` to 0.15 while the mask stays at the family band 2.32–2.79.

Prediction: mean IoU falls back near 0.81.

Rationale: `a11_a08_proud_radius_015` scored 0.811. Spill was 58,184. That arm did not keep the a08 mask.

Stop: a wider neighbourhood is not a substitute for the mid mask.

### 7. Keep AB height at 3239.77

Action: do not set AB height to 3100 or to 3400 on this stack.

Prediction: mean IoU falls and A2-block IoU falls.

Rationale: `a14_ab3100` scored 0.804 with A2-block IoU 0.598. `a15_ab3400` scored 0.748 with A2-block IoU 0.371. Both sealed calls failed. Both lining guards versus a13 failed.

Stop: AB height off 3239.77 is closed on this scan.

### 8. Stop further angle search around 7.52

Action: once angle is near +7.52, stop spending runs on ±1° steps.

Prediction: mean IoU stays inside 0.003 of the current best.

Rationale: `a16_angle_850` scored 0.848. `a17_angle_650` scored 0.850. Both sealed calls for mean IoU ≥ 0.860 failed. The lining guard held.

Stop: do not treat a move inside 0.003 as a new angle lever. Angle 6.5 is the current hold. It is not a confirmed step that opens a new band.

### 9. Keep segment width at 1200

Action: do not set segment width to 1100 or to 1300 on this stack.

Prediction: mean IoU stays at or below the current best.

Rationale: `a18_width_1100` scored 0.848. `a19_width_1300` scored 0.847. Both sealed calls failed. Both lining guards held.

Stop: segment width off 1200 is closed on this scan.

### 10. Apply ring-2 cyclic label shift +1

Action: after proud, set `ring_label_shifts` to `{"2": 1}` (cycle lining labels 1→2→…→6→1 on pred_ring 2 only).

Prediction: mean IoU leaves the 0.85 band and A2-block IoU leaves 0.73.

Rationale: `a34_ring2_label_shift` scored 0.890 with A2 0.805. Sealed call ≥ 0.870 held. Guard held. Full runs `a36` and `a37` scored 0.888.

Stop: do not reverse the ring-2 shift on this scan without a new sealed diagnosis.

### 11. Stop the config chase short of 0.9

Action: do not spend another SAM, assignment, or proud-parameter run on this scan to chase mean IoU 0.9.

Prediction: further config moves stay under 0.9.

Rationale: five proud retunes on a34 (`a38`–`a42`) scored 0.882–0.890. Full lock with the best proud (`a43`) scored 0.891. Every sealed call for 0.9 failed.

Stop: remaining lift needs detect/placement change, not another config knob.

## Limits

One scan. No repeated seed. The best score is 0.891. The 0.9 target was not reached. Config chase is closed. The formula is a development fit. It is not a released proxy. A2-block IoU on the best arm is 0.802.
