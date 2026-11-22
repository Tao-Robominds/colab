# 1-1 tune claims

Status: proposed. The measurements support these relations on `data/scans/1-1.txt`, family `staggered`. They are not accepted beyond that scan. They are not accepted wisdom.

Scores: [`dikw/data/1_1_tune.md`](../../data/1_1_tune.md). Arm controls: [`dikw/information/1_1_tune.md`](../../information/1_1_tune.md). The tune experience that uses these relations: [`dikw/wisdom/staggered_tune_experience.md`](../../wisdom/staggered_tune_experience.md).

Mean IoU is the mean of the seven class Jaccard scores. The lining guard fails when a lining class falls more than 0.02 below the comparison arm.

## 1. The score moved in bands

On this scan, retained arms sit in bands about 0.785, 0.796–0.810, 0.846–0.850, 0.888–0.891, 0.898, and 0.917. Knob moves inside about 0.003 did not open the next band.

The 0.85 band broke on `a34_ring2_label_shift` at 0.890. The stall under 0.9 broke on `a45_a44_intensity_m1400` at 0.917. Both are label corrections after SAM.

Scope: this scan, these arms. A plateau is not a proved bound. The ceiling above 0.917 is unknown.

## 2. The K mirror moved K-block IoU, and not the later bands

`a01_mirror_k` changed only `mirror_k_geometry`. Mean IoU went from the recorded episode start 0.785 to 0.796. K-block IoU went from 0.716 to 0.797. A2-block stayed at 0.622. The sealed call held. The guard held.

The move from 0.810 to 0.846 is not this change. One arm. The mechanism is a template-orientation correction. A physical cause is not separated.

Code: `sam4tun/staggered/5_sam.py`.

The episode-start row is in the score table. `data/development/1-1/baseline/evaluation/performance.md` now reads 0.848. That file is not the episode start.

## 3. A 5 mm proud cut raised the mirrored cloud, and 3 mm failed the guard

`a02_proud_on_a01` replayed `a01` labels at 5 mm and 10 cm. Mean IoU was 0.810. Spill fell from 89,898 to 59,628. `a05_proud3_on_a01` used 3 mm on the same cloud and neighbourhood. Mean IoU was 0.778. B1-block and A1-block failed the guard.

This is one replay pair. It does not rerun stages 1–5. Code: `drop_proud_lining` in `sam4tun/staggered/helpers/proud_lining.py`.

## 4. The 0.85 band travelled with the mid mask

`a06_mid_mask_mirror_proud` scored 0.846 with mask 2.72–2.78, the mirror, and the 5 mm cut. The sealed call 0.815 failed because the gain was larger. The guard held. `a10_a08_mask_wide_270_280` scored 0.848. `a11_a08_proud_radius_015` left the mask at 2.32–2.79, set the neighbourhood to 15 cm, and scored 0.811.

`a06` is a full run and `a02` is a replay, so the mask is not the only difference. `a11` changes mask and radius together. The association stands. The isolation does not.

## 5. Closed families missed twice or stayed in band

Template scale (`a03` 0.774, `a04` 0.800), AB height (`a14` 0.804, `a15` 0.748), angle steps of about 1° (`a16` 0.848, `a17` 0.850), and segment width (`a18` 0.848, `a19` 0.847) did not open a new band. AB height failed the guard both times. On `a15`, K-block IoU rose to 0.878 while mean IoU fell.

Local knobs on the mid-mask stack stayed at 0.846–0.849 (`a07`–`a10`, `a12`, `a13`). Proud retunes after the ring-2 cycle stayed at 0.882–0.891 (`a38`–`a43`).

B1 template height (`a20`, 0.849) is one miss. It is not in the closed set.

A higher K-block IoU is not a substitute for mean IoU.

## 6. The ring-2 cycle is a label correction, and a filled theta border is not

`a34_ring2_label_shift` cycled pred_ring 2 lining +1 on a17 labels. Mean IoU was 0.890. A2-block was 0.805. The sealed call ≥ 0.870 and A2 ≥ 0.80 held. The guard held.

`a36_ring2_shift` logged the shift and then the proud drop. Mean IoU was 0.888. A2-block was 0.797. `a37_ring2_shift_after_proud` logged the proud drop and then the shift. Mean IoU was 0.888. A2-block was 0.793. The order changed the band by nothing that leaves 0.888. The current source order is proud, then shift.

`a40_wrap_theta_on_a13` set `wrap_theta` true from the a13 stack. Mean IoU fell from 0.849 to 0.382. A3-block was 0.007. B2-block was 0.005. The border filled. The target fell. That arm has `performance.md` and no `*_result.json`.

The ring and the direction were named with ground truth. The cause of the offset is not identified. Code: the shift loop in `sam4tun/staggered/5_sam.py`. The rejected border path is `crop_image_theta` in `src/rsi4tun/theta_wrap.py`.

`a21_a2_over_a1` and `a22_a2_bias_2` scored 0.838. Their labels differ from the current `a17_angle_650` file by 34,741 and 34,046 points. `a23_a2_over_a1_on_a17` differs by 734 points and scored 0.850. Overlap priority on the current a17 labels did not move the band. `a21` and `a22` are not a clean test of that rule.

## 7. The theta split raised the full run to 0.898, and the sealed floor failed

On frozen a13 labels, the cycle scored 0.890 and the split of pre-cycle B2 rows at theta 12.4 scored 0.899. Cuts at 12.3 and 12.5, and assigning those rows their true class, also scored 0.899.

`a44_a13_ring2_b2theta` ran that rule through stages 1–6. The log split 11,252 points. Stage 6 wrote 0.898. A2-block was 0.806. The sealed call ≥ 0.899 failed. The guard versus `a43` held.

The cut is not unique at the recorded resolution. It was chosen on this scan. Code: `split_ring_source_by_theta` in `src/rsi4tun/ring_theta_split.py`.

## 8. The dark-lining cut reproduced 0.917, and it was chosen on the same labels

On finished a44 labels, intensity below −1400 returned to background scored 0.917. `a45_a44_intensity_m1400` dropped 23,387 points and stage 6 wrote 0.917. A2-block was 0.880. The sealed call held. The guard versus a44 held.

The class mix of the dropped points is not in the result file. The threshold was selected on the labels the full run then reproduced. Proud retunes did not reach this score. Code: `drop_dark_lining` in `src/rsi4tun/dark_lining.py`.

## 9. The 1-1 proxy scores the a45 pack at the observed mean IoU

`dikw/wisdom/1_1_proxy.json` is `1_1_tune_v2`, `development_fit_pending`, fit on all 46 arms under `data/development/1-1/tune`, including `a45`. The in-sample score of that pack matches the observed 0.917.

The features are proud residual, mid mask, the ring-2 shift of +1, the ring-2 source-6 split at theta 12.4, the −1400 dark cut, theta wrap, AB relative error, template-scale deviation, the swapped walk, template mask off, A1 negative wrap, `min_forward_blocks` 4, and block-scale deviation. The K mirror is on in every row. One scan. This is not a released proxy and not accepted wisdom.
