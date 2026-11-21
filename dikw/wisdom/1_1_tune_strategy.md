# 1-1 tune strategy

Scope: family `staggered`. Scan `data/scans/1-1.txt`.

Status: a prior for the next diagnosis on this scan. It is not an accepted principle. `configs/protocol.json` still lists no accepted wisdom.

The fitted formula is [`1_1_proxy.json`](1_1_proxy.json). The scores are in [`dikw/data/1_1_tune.md`](../data/1_1_tune.md). What each arm held fixed is in [`dikw/information/1_1_tune.md`](../information/1_1_tune.md).

The sample strategy remains the prior for `data/scans/sample.txt`. It is not the level on this scan. The sample replay scored 0.902. The best arm here scored 0.849.

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

## Limits

One scan. No repeated seed. The best score is 0.849. The score above that is unknown. The formula is a development fit. It is not a released proxy. A2-block IoU on the best arm is 0.725.
