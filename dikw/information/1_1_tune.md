# What the 1-1 tune was

The measurements are in `dikw/data/1_1_tune.md`. This page says what those arms held fixed, and which comparisons are valid.

## Question

The tune tried to raise 6-class mean IoU above 0.9 on `data/scans/1-1.txt`.

The family is `staggered`. The first episode used eleven full runs and two proud replays and stopped after `a13` at mean IoU 0.849. The live campaign reached 0.891 on `a43` and stopped the config chase short of 0.9.

The living baseline `data/development/1-1/baseline` is not overwritten. The shared family directory is not overwritten. Each full run clones a param pack and applies only the overrides below.

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

**AB height on the a13 stack.** `a14_ab3100` and `a15_ab3400` keep the a13 stack and change only AB height to 3100 or 3400. The hold is AB height 3239.77 on a13.

**Angle on the a13 stack.** `a16_angle_850` sets angle to 8.5. `a17_angle_650` sets angle to 6.5. Sign stays positive. One knob each.

**Segment width on the a17 stack.** `a18_width_1100` and `a19_width_1300` keep angle 6.5 and change only segment width to 1100 or 1300. The hold is width 1200.

**B1 template height on the a17 stack.** `a20_b1_height_1519` sets `prompt_points.template_mask.b1_block.height_top` to 1519.89. The hold is 1619.89.

**Assignment replays on a17 masks.** `a23_a2_over_a1_on_a17` flips A1→A2 only where both masks cover. `a29_a1_over_b1_on_a17` flips B1→A1 on B1∩A1. Stages 1–5 are not rerun.

**Circumferential / SAM exploratories on a17.** `a24_reverse_circ` sets `reverse_circumferential` true. `a25_a1_scale_090` / `a26_a2_scale_110` set `block_template_scale` for one block. `a27_swap_a1_a2_walk` sets `circumferential_block_order` to [K,B1,A2,A1,A3,B2]. `a28_multimask` sets `multimask_output` true. `a30_padding_250` sets padding 250. `a31_no_template_mask` sets `use_template_mask_input` false. `a32_extra_ring_1` sets `extra_ring_segments` 1. `a33_a1_wrap_negatives` sets `a1_wrap_negative_prompts` true.

**Ring-2 label shift.** `a34_ring2_label_shift` is an assignment replay: on pred_ring 2 only, cycle lining labels +1 (1→2→…→6→1). Stages 1–5 are not rerun. `a36_ring2_shift` and `a37_ring2_shift_after_proud` are full runs with `ring_label_shifts={"2":1}` (shift after proud). `a35_min_forward_4` sets `min_forward_blocks` to 4 on the a17 stack.

**Proud retune on a34.** `a38`–`a42` start from a34 labels, apply `drop_proud_lining` only, and rescore. Radii/residuals: 0.10/5, 0.15/5, 0.20/5, 0.10/6, 0.07/4. `a43_ring2_shift_proud_r10_6mm` is a full run with `ring_label_shifts={"2":1}`, proud 0.10 m / 6 mm.

The lining guard for campaign arms is versus the current best arm, not versus the 0.785 episode baseline.

## Which baseline to cite

I use `data/development/1-1/baseline` when I compare an arm with the start of the first episode. That score is mean IoU 0.785.

For the live campaign, the lining guard fails an arm when any lining class falls more than 0.02 below the current best arm (a13). A higher K-block IoU or a higher background IoU is not the target.
