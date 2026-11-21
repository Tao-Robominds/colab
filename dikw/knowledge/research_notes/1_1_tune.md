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

The highest mean IoU is 0.849 on `a13_a08_proud_radius_007`. A2-block IoU there is 0.725. The target 0.9 was not reached.

## Associations

These are associations on this scan. I do not state a physical cause.

The mirror accounts for the K-block move from 0.716 to 0.797. It does not account for the later move from 0.810 to 0.846.

The mid mask, together with the mirror and the 5 mm cut, accounts for that later move. Arms that kept the mid mask and moved one other knob stayed inside 0.846–0.849.

Template scale 0.97 and 1.03 did not raise mean IoU. A 3 mm proud residual broke the lining guard. A 15 cm neighbourhood without the mid mask gave back the gain from `a06`.

A higher background IoU and a higher K-block IoU both appear on the 0.846–0.849 band. Neither one is the 0.9 target. A2-block remains the lowest lining class on the best arm.

## Predictions checked

A prediction held when the sealed mean IoU was within 0.02 of the score.

`a01` predicted 0.797 and scored 0.796. The guard held. The prediction held.

`a02` predicted 0.799 and scored 0.810. The guard held. The prediction held.

`a03` predicted 0.800 and scored 0.774. The guard failed. The prediction failed.

`a04` predicted 0.825 and scored 0.800. The guard held. The prediction failed.

`a05` predicted 0.812 and scored 0.778. The guard failed. The prediction failed.

`a06` predicted 0.815 and scored 0.846. The guard held. The prediction failed because the gain was larger than the sealed call.

`a07` predicted 0.852 and scored 0.848. `a08` predicted 0.860 and scored 0.848. `a09` predicted 0.853 and scored 0.848. `a10` predicted 0.852 and scored 0.848. `a12` predicted 0.846 and scored 0.847. `a13` predicted 0.853 and scored 0.849. Each guard held. Each prediction held.

`a11` predicted 0.852 and scored 0.811. The guard held. The prediction failed.

## Open gap

The score above 0.849 is unknown. The sample prior's 0.902 was fit on `data/scans/sample.txt`. It did not appear on this scan.

A2-block IoU on the best arm is 0.725, against 0.624 at the baseline. The arms that stayed on the mid mask did not move A2-block out of 0.716–0.725.

`window_size` other than 7 and 9, and `default_cutoff_z`, were not run.

## Limits

One scan. No repeated seed. Eleven full runs and two replays. Movements inside 0.003 mean IoU on the mid-mask stack are inside the observed band. That band is not a proved bound.
