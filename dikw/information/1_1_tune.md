# What the 1-1 tune was

The measurements are in `dikw/data/1_1_tune.md`. This page says what those arms held fixed, and which comparisons are valid.

## Question

The tune tried to raise 6-class mean IoU above 0.9 on `data/scans/1-1.txt`.

The family is `staggered`. The budget was 12 full stage 1–6 runs. A proud replay does not spend that budget. Eleven full runs were used. The episode stopped after `a13`.

The living baseline `data/development/1-1/baseline` was not overwritten. The shared family directory was not overwritten. Each full run cloned `configs/families/staggered` and applied only the overrides below.

## What a full run holds fixed

A full run executes unfolding, denoising, enhancing, detection, SAM, and evaluation. A score change is a change in the cloned parameters, not a change in the runner.

At the start of the tune the family file sets the mirror off, K height 1079.92, AB height 3239.77, and angle 7.52. It does not set `template_scale` or `proud_residual_mm`. The denoise mask is 2.32–2.79 and `smoothing_offset` is −0.003. Enhancing `window_size` is 9.

When `proud_residual_mm` is absent, SAM does not call `drop_proud_lining`. When the residual is set and `proud_radius_m` is absent, the neighbourhood is 10 cm.

## What a replay holds fixed

`a02` and `a05` start from the `a01_mirror_k` point labels. They do not rerun stages 1–5. They apply `drop_proud_lining` and rescore.

## How to read the arms

**Mirror.** `a01_mirror_k` sets `mirror_k_geometry` to true. Nothing else changes.

**Proud replay.** `a02_proud_on_a01` uses a 5 mm residual and a 10 cm neighbourhood. `a05_proud3_on_a01` uses a 3 mm residual and the same neighbourhood.

**Template scale.** `a03_template_scale_103` keeps the mirror and sets `template_scale` to 1.03. `a04_scale097_mirror_proud` keeps the mirror, sets `template_scale` to 0.97, and turns on the 5 mm cut at 10 cm.

**Mid mask.** `a06_mid_mask_mirror_proud` sets the denoise mask to 2.72–2.78, keeps the mirror, and turns on the 5 mm cut at 10 cm.

**K height.** `a07_mid_mask_proud5_kh1120` keeps the a06 settings and sets K height to 1120.

**Local knobs on the a07 stack.** These arms keep the mirror, K height 1120, AB height 3239.77, and template scale 1.0.

`a08` also sets the mid mask, the 5 mm cut at 10 cm, `window_size` 7, and outlier interpolation on.

`a09` sets the mid mask, the 5 mm cut, and outlier interpolation on. It does not set `window_size`, so the window returns to 9. It does not set `proud_radius_m`, so the neighbourhood is 10 cm.

`a10` sets the mask to 2.70–2.80 and the 5 mm cut. It does not set the enhancing keys.

`a12` sets the mid mask, `smoothing_offset` −0.005, and the 5 mm cut.

`a13_a08_proud_radius_007` sets the mid mask and the 5 mm cut with a 7 cm neighbourhood.

**Proud radius without the mid mask.** `a11_a08_proud_radius_015` sets the mirror, K height 1120, AB height 3239.77, template scale 1.0, and a 5 mm cut at 15 cm. It does not set the denoise mask, so the mask stays 2.32–2.79. It is not a comparison that holds the a08 mask fixed.

## Which baseline to cite

I use `data/development/1-1/baseline` when I compare an arm with the start of the tune. That score is mean IoU 0.785.

The lining guard fails an arm when any lining class falls more than 0.02 below that baseline. A higher K-block IoU or a higher background IoU is not the target.
