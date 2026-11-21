# 1-1 tune: what the measurements support

Status: provisional. One scan. Family `staggered`. File `data/scans/1-1.txt`.

This note is not an accepted claim. It separates observations, associations, and the open gap.

Measurements: `dikw/data/1_1_tune.md`.

Design of the arms: `dikw/information/1_1_tune.md`.

The fitted formula is `dikw/wisdom/1_1_proxy.json`. The ordered prior is `dikw/wisdom/1_1_tune_strategy.md`. Neither is accepted wisdom.

## Observations

Turning the K mirror on raised mean IoU from 0.785 to 0.796. K-block IoU rose from 0.716 to 0.797. Arm `a01_mirror_k`. The lining guard held.

The 5 mm proud cut at 10 cm on that cloud raised mean IoU to 0.810 and cut spill from 89,898 to 59,628. Arm `a02_proud_on_a01`. The guard held. The same cloud with a 3 mm residual scored 0.778. B1-block and A1-block failed the guard. Arm `a05_proud3_on_a01`.

Template scale 1.03 scored 0.774. A1-block and A2-block failed the guard. Arm `a03_template_scale_103`. Template scale 0.97 with the mirror and the 5 mm cut scored 0.800. The guard held. Arm `a04_scale097_mirror_proud`.

The mid mask 2.72–2.78, with the mirror and the 5 mm cut, scored 0.846. Spill was 37,536. Every lining class rose. Arm `a06_mid_mask_mirror_proud`.

K height 1120 on that stack scored 0.848. Arm `a07_mid_mask_proud5_kh1120`. Window size 7, outlier interpolation, the wider mask 2.70–2.80, smoothing offset −0.005, and a 7 cm proud neighbourhood then scored 0.848, 0.848, 0.848, 0.847, and 0.849. Arms `a08` through `a10`, `a12`, and `a13`.

The 15 cm proud neighbourhood, with the family mask left at 2.32–2.79, scored 0.811. Spill was 58,184. Arm `a11_a08_proud_radius_015`. The guard held. The score left the 0.846–0.849 band.

On a13, true A2 points that are wrong go 89.3% to other blocks (mostly A1) and 10.7% to background. True A1 wrong points go 84.1% to other blocks (mostly B1). True B1 wrong points go 59.7% to other blocks and 40.3% to background.

AB height 3100 (`a14_ab3100`) scored 0.804 and A2-block IoU 0.598. AB height 3400 (`a15_ab3400`) scored 0.748 and A2-block IoU 0.371. Both sealed calls failed. Both guards versus a13 failed.

Angle 8.5 (`a16_angle_850`) scored 0.848. Angle 6.5 (`a17_angle_650`) scored 0.850. Both sealed calls for mean IoU ≥ 0.860 failed. Both guards held. `a17` is the best arm.

Segment width 1100 (`a18_width_1100`) scored 0.848. Width 1300 (`a19_width_1300`) scored 0.847. Both sealed calls failed. Both guards versus a17 held.

B1 template height 1519.89 (`a20_b1_height_1519`) scored 0.849. The sealed call failed. The guard held. One miss. Not a confirmed wisdom stop.

The highest mean IoU is 0.850 on `a17_angle_650`. A2-block IoU there is 0.727. The target 0.9 was not reached.

## Associations

These are associations on this scan. I do not state a physical cause.

The mirror accounts for the K-block move from 0.716 to 0.797. It does not account for the later move from 0.810 to 0.846.

The mid mask, together with the mirror and the 5 mm cut, accounts for that later move. Arms that kept the mid mask and moved one other knob stayed inside 0.846–0.849.

Template scale 0.97 and 1.03 did not raise mean IoU. A 3 mm proud residual broke the lining guard. A 15 cm neighbourhood without the mid mask gave back the gain from `a06`.

Moving AB height off 3239.77 to 3100 or 3400 lowered mean IoU and lowered A2-block IoU. That miss happened twice. It is a confirmed wisdom stop.

Angle steps of about 1° stayed inside 0.003 of the best score. That miss happened twice on the sealed mean-IoU call. Further angle search is a confirmed wisdom stop. Angle 6.5 is the current hold. It did not open a new band.

Segment width 1100 and 1300 stayed at or below the best score. That miss happened twice. It is a confirmed wisdom stop.

B1 template height 1519.89 stayed inside 0.003 of the best score. That is one miss.

On a17, about 7.1k true A2 points are predicted A1. They sit in A1's theta band and are concentrated on gt_ring 17. About 6.9k of them are outside A2's SAM mask, so assignment priority cannot reclaim them. Flipping A1→A2 on A1∩A2 (`a23`) fixed 269 true A2 and broke 256 true A1.

`reverse_circumferential`, multimask, padding 250, and an extra ring segment stayed inside 0.003 of 0.850. Shrinking A1 or expanding A2 hurt. Swapping the A1/A2 walk destroyed both classes. Dropping the template mask prior and adding A1 wrap negatives both dropped mean IoU below 0.79.

A2-block remains the class farthest from the sample 0.902 profile.

## Predictions checked

A prediction held when the sealed mean IoU was within 0.02 of the score, except where a later sealed call stated a higher floor.

`a01` predicted 0.797 and scored 0.796. The guard held. The prediction held.

`a02` predicted 0.799 and scored 0.810. The guard held. The prediction held.

`a03` predicted 0.800 and scored 0.774. The guard failed. The prediction failed.

`a04` predicted 0.825 and scored 0.800. The guard held. The prediction failed.

`a05` predicted 0.812 and scored 0.778. The guard failed. The prediction failed.

`a06` predicted 0.815 and scored 0.846. The guard held. The prediction failed because the gain was larger than the sealed call.

`a07` predicted 0.852 and scored 0.848. `a08` predicted 0.860 and scored 0.848. `a09` predicted 0.853 and scored 0.848. `a10` predicted 0.852 and scored 0.848. `a12` predicted 0.846 and scored 0.847. `a13` predicted 0.853 and scored 0.849. Each guard held. Each prediction held.

`a11` predicted 0.852 and scored 0.811. The guard held. The prediction failed.

`a14` predicted mean IoU ≥ 0.87 and A2 ≥ 0.80. It scored 0.804 and 0.598. The guard failed. The prediction failed.

`a15` made the same call. It scored 0.748 and 0.371. The guard failed. The prediction failed.

`a16` predicted mean IoU ≥ 0.860 and A2 ≥ 0.76. It scored 0.848 and 0.720. The guard held. The prediction failed.

`a17` made the same call. It scored 0.850 and 0.727. The guard held. The prediction failed. The score is the new best.

`a18` predicted mean IoU ≥ 0.870 and A2 ≥ 0.76. It scored 0.848 and 0.724. The guard held. The prediction failed.

`a19` made the same call. It scored 0.847 and 0.718. The guard held. The prediction failed.

`a20` predicted mean IoU ≥ 0.870 and B1 ≥ 0.890. It scored 0.849 and 0.867. The guard held. The prediction failed.

`a23` through `a33` each sealed mean IoU ≥ 0.870 and A2 ≥ 0.80 (or A1 ≥ 0.88 for `a29`). None held. `a25`, `a26`, `a27`, `a31`, and `a33` also failed the lining guard or destroyed A2.

`a34` cyclic-shifted pred_ring 2 labels +1. Mean IoU 0.890. A2 0.805. Sealed call ≥ 0.870 held. Guard held.

`a35` min_forward_blocks 4 scored 0.805 with A2 0.448. Guard failed.

`a36` and `a37` full runs with `ring_label_shifts={"2":1}` scored 0.888. Guard held. Call for 0.9 failed.

`a38`–`a42` proud replays on a34 scored 0.882–0.890. None reached 0.9. Best tie `a41` at 0.10 m / 6 mm.

`a43` full run with ring-2 shift and that proud scored 0.891 with A2 0.802. Call for 0.9 failed. Guard held. Config chase stopped.

## Open gap

Best mean IoU is 0.891 on `a43`. The sample prior's 0.902 was fit on `data/scans/sample.txt`. It did not appear on this scan.

Ring-2 cyclic shift opened the 0.89 band. Further SAM knobs and proud retunes did not open 0.9. Remaining lift needs detect/placement change, not another config knob.

## Limits

One scan. No repeated seed. Movements inside 0.003 mean IoU are inside the observed band. That band is not a proved bound. The 0.9 target was not reached. Config chase on this scan is closed.
