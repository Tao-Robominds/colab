# Sample tune strategy

Scope: family `sample`. Scan `data/scans/sample.txt`.

Status: a prior for the next diagnosis on this scan. It is not an accepted principle. `configs/protocol.json` still lists no accepted wisdom.

The fitted formula is [`sample_proxy.json`](sample_proxy.json). The scores are in [`dikw/data/sample_tune.md`](../data/sample_tune.md). What each trial held fixed is in [`dikw/information/sample_tune.md`](../information/sample_tune.md).

## Fitted formula

The target is 6-class mean IoU.

The features are `k_wedge`, `angle_positive`, `ab_rel_error`, and `proud_cut`.

The equation is the standardised ridge already implemented by `FrozenProxy.predict`:

```
clip(intercept + sum(weight_i * (x_i - centre_i) / scale_i), 0, 1)
```

The coefficients live in the JSON. Prose does not replace them.

The refit includes the new radius experiment. `t29` keeps `proud_cut` at 0 and scored 0.899. `t30` sets `proud_cut` to 1 and scored 0.902. A fit that stops at `t28` is the old prior.

The formula does not see denoise offset, template scale, overlap abstention, or a logit margin. Those misses stay as stops below. The proud weight comes from one replay on the t22 labels.

## Steps

### 1. Turn the K mirror on

Action: set `mirror_k_geometry` to true before any other SAM knob.

Prediction: mean IoU rises by about 0.014. K-block IoU leaves 0.78.

Rationale: `t03_mirror_k` moved mean IoU from 0.880 to 0.894 and K-block IoU from 0.784 to 0.876.

Stop: if K-block IoU stays near 0.78 after the mirror is on, stop before another SAM search.

### 2. Keep the template angle positive

Action: keep the template angle at +7.52. Do not flip the sign.

Prediction: a negative angle drops B1-block IoU and A1-block IoU to 0. Mean IoU falls below 0.3.

Rationale: `t02_angle_neg` scored 0.267. `t04_angle_neg_mirror` scored 0.286.

Stop: reject a negative angle before another full run.

### 3. Hold AB height at 3239.77

Action: leave AB height at 3239.77.

Prediction: AB height 3200 or 3300 drops mean IoU, even when K-block IoU rises.

Rationale: `t12_kh1100_ab3300` scored 0.839 with K-block IoU 0.896. `t20_ab3200` scored 0.881. A higher K-block score or a higher background score is not success.

Stop: do not take a higher K-block IoU, or a higher background IoU, as a substitute for mean IoU.

### 4. Stop the local SAM search

Action: once the mirror is on and AB height is 3239.77, stop moving angle, K height, width, padding, crop, taper, and y bounds.

Prediction: those knobs stay between mean IoU 0.892 and 0.895. Detector prompts beat ground-truth K medians.

Rationale: the local search trials after the mirror stayed in that band. `t09_kh_1120` scored 0.895. `t15_oracle_mirror_kh1120` scored 0.890.

Stop: do not spend another trial on those knobs for this scan.

### 5. Keep the mid radial mask

Action: keep the denoise mask at 2.72 to 2.78. Do not tighten it. Do not raise `smoothing_offset` to buy background IoU.

Prediction: a tight mask or a raised cutoff lowers mean IoU.

Rationale: `t21_denoise_tight` scored 0.845. `t25_denoise_offset_p005` scored 0.731. The mid mask on `t22_denoise_mid` scored 0.896.

Stop: do not trade lining classes for background IoU on this lever.

### 6. Skip the failed SAM levers

Action: do not shrink the template to 0.97, abstain on overlap, or demand a logit margin of 1.0.

Prediction: those three moves miss 0.9.

Rationale: `t26_template_scale_097` scored 0.878. `t27_overlap_abstain` scored 0.887. `t28_margin_abstain` scored 0.896. Contested pixels are mostly true lining. Spill is mostly a sole-mask claim.

Stop: consult the formula. If the four inputs match a step whose prediction already failed, do not spend the run.

### 7. Drop proud lining points

Action: after labels exist, return a predicted lining point to background when it stands more than 5 mm proud of other predicted lining points within 10 cm in `(h, θ)`.

Prediction: mean IoU crosses 0.900. Each lining class stays within 0.02 of the t22 control. The absolute 5 mm cut stays under 0.900.

Rationale: `t30_proud_5mm` scored 0.902. `t29_radius_abs_5mm` scored 0.899. Inset points are mostly true lining. Proud points are enriched for background. `drop_proud_lining` is the rule. The sample SAM config sets the cut.

Stop: do not replace the proud cut with the absolute cut on this scan.

## Limits

One scan. No repeated seed. The formula is a development fit. It is not a released proxy. The score above 0.902 is unknown.
