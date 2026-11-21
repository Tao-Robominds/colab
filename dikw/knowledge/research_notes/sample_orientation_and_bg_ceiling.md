# Sample tune: what the measurements support

Status: provisional. One scan. Family `sample`. File `data/scans/sample.txt`.

This note is not an accepted claim. It separates observations, associations, and open explanations.

Measurements: `dikw/data/sample_tune.md`.

Design of the trials: `dikw/information/sample_tune.md`.

Code path for t01–t20: `data/development/sample/tune/run_trial.py`.

Code path for t23–t25: `data/development/sample/tune/run_full_arm.py`.

Predictions before those arms: `data/development/sample/tune/STAGE13_PREDICTIONS.md`.

## Observations

Turning the K mirror on, with the other SAM settings left as they were, raised mean IoU from 0.880 to 0.894. K-block IoU rose from 0.784 to 0.876. Trial `t03_mirror_k`.

Ground-truth prompts without that mirror left K-block IoU at 0.781 and mean IoU at 0.876. Trial `t01_oracle_gt`.

A template angle of −7.52 dropped mean IoU to 0.267. B1-block IoU and A1-block IoU fell to 0. The same angle with the mirror on scored mean IoU 0.286, while K-block IoU was 0.907. Trials `t02_angle_neg` and `t04_angle_neg_mirror`.

Swapping the detecting oblique signs, with the mirror on, dropped mean IoU to 0.859 and K-block IoU to 0.811. Trial `t08_mirror_detect_swap`.

With the mirror on, the local SAM search stayed between mean IoU 0.892 and 0.895. K height 1150 raised K-block IoU to 0.893 and scored mean IoU 0.893. Trial `t10_kh_1150`.

AB height 3300 scored K-block IoU 0.896, A2-block IoU 0.638, and mean IoU 0.839. AB height 3200 scored A2-block IoU 0.830 and mean IoU 0.881. Trials `t12_kh1100_ab3300` and `t20_ab3200`.

With the mirror on and K height 1120, the detector scored mean IoU 0.895. Ground-truth prompts at that geometry scored 0.890. Trials `t09_kh_1120` and `t15_oracle_mirror_kh1120`.

The tight run scored background IoU 0.859 and mean IoU 0.845. A2-block IoU was 0.730. The mid run scored background IoU 0.849 and mean IoU 0.896. That 0.896 is the highest mean IoU in the archive. Trials `t21_denoise_tight` and `t22_denoise_mid`. These two reran unfolding, denoising, and enhancing. I cannot assign the score gap to the radial mask alone.

On the mid-mask output, 35,856 ground-truth background points received a lining label. All of them lie at radius 2.72 to 2.78. Their median distance to a ground-truth lining point is 0.014 m in `(h, θ)`. Most of those labels are B2-block (11,312) or B1-block (9,377).

With outlier interpolation off, mean IoU was 0.897 and spill was 35,874. Trial `t23_enhance_no_outlier`. The lining guard held. Spill did not fall by 30%.

With depth window size 3, mean IoU was 0.892 and spill was 35,087. Trial `t24_enhance_window3`. The lining guard held. Spill fell by 2.1%.

With denoise `smoothing_offset` +0.005, mean IoU was 0.731 and spill was 29,751. Trial `t25_denoise_offset_p005`. Spill fell by 17%. Every lining class fell by more than 0.02.

With the SAM template scaled to 0.97, and stages 1–4 held at t22, mean IoU was 0.878. Total spill was 31,534. B1 spill was 7,752 and B2 spill was 9,473, so B1+B2 spill was 17,225. A1-block IoU was 0.904. A2-block IoU was 0.837. Trial `t26_template_scale_097`.

With overlap abstention on the t22 masks, mean IoU was 0.887 and spill was 35,155. K-block IoU was 0.860. Trial `t27_overlap_abstain`. Contested pixels were 138,052.

With a logit margin of 1.0 on the same masks, mean IoU was 0.896 and spill was 35,851. Trial `t28_margin_abstain`.

On the t22 labels, an absolute radius residual above 5 mm gave mean IoU 0.899 and spill 28,193. Trial `t29_radius_abs_5mm`. The lining guard held.

Returning a point to background only when it stood more than 5 mm proud of other predicted lining points within 10 cm gave mean IoU 0.902 and spill 28,702. Trial `t30_proud_5mm`. A2-block IoU was 0.887. Every other lining class rose. This replay did not rerun stages 1 to 5.

## Associations

These are associations on this scan. I do not state a physical cause.

The K mirror accounts for the only detect or SAM change that moved mean IoU by more than 0.01 while the lining classes stayed intact.

K-block IoU and mean IoU moved apart when AB height changed, and again at K height 1150. A higher K-block score did not mean a higher mean IoU.

Background IoU and mean IoU moved apart between the two full reruns. The tight run has the higher background IoU and the lower mean IoU. The recorded intent is the radial mask. Unfolding coordinates and denoise labels also changed.

Ground-truth prompts did not raise mean IoU above the detector once the mirror was on.

Turning off outlier fill did not cut the spill. Narrowing the depth window cut 2.1% of the spill and lowered mean IoU. Raising the denoise cutoff cut 17% of the spill and broke the lining classes. These three stage-2 and stage-3 levers did not open mean IoU above 0.9.

## Predictions checked

Arm A predicted a spill cut of at least 30% and a mean IoU rise with the lining guard held. The lining guard held. Spill did not fall. The prediction failed.

Arm B made the same prediction. Spill fell by 2.1%. Mean IoU fell to 0.892. The prediction failed.

Arm C predicted that spill would not fall by 30% and that mean IoU would stay at or below 0.900. Both parts held. The arm damaged lining.

The template arm predicted mean IoU above 0.900, B1+B2 spill at or below 14,482, total spill at or below 28,685, and the lining guard. Mean IoU was 0.878. B1+B2 spill was 17,225, a 17% cut. A1 and A2 failed the lining guard. The prediction failed.

Arm D predicted mean IoU above 0.900, a spill cut of at least 3,000, and the lining guard. Mean IoU was 0.887. Spill fell by 701. K failed the lining guard. The prediction failed.

Arm E made the same prediction with a logit margin of 1.0. Mean IoU was 0.896. Spill fell by 5. The prediction failed.

Arm F predicted spill near 28,200, mean IoU near 0.904, and the lining guard, for an absolute residual above 5 mm. Spill was 28,193. Mean IoU was 0.899. The guard held. The mean IoU call failed.

Arm G predicted spill near 29,600, mean IoU near 0.902, and the lining guard, for a proud residual above 5 mm. Spill was 28,702. Mean IoU was 0.902. The guard held. The mean IoU call held. The spill call was high by about 900 points.

## Open explanations

The errors that remain sit on a lining radius, next to lining points.

A 3% template shrink cut B1+B2 spill by 17% and damaged A2. That one scale did not show that the template cover is the lever that clears 0.9.

Overlap abstention and a logit margin of 1.0 did not select the spill. Contested pixels are mostly true lining. The spill that remains is mostly a sole-mask claim. The highest-logit rule stays.

Denoising may keep points that the radial mask cannot separate from lining. The stage-2 arms did not clear 0.9 without lining damage.

Points that stand proud of the local predicted lining are enriched for background, relative to points that sit inset by the same amount. Dropping the proud points on the t22 labels raised mean IoU above 0.9. Dropping both signs did not. I do not state what those proud points are on the wall.

The ceiling above 0.902 stays unknown.

## Limits

The detect and SAM search, after the mirror was on, produced an observed plateau from 0.892 to 0.895. The best full-pipeline score in the archive is 0.897 on `t23_enhance_no_outlier`. The best replay score is 0.902 on `t30_proud_5mm`.

That plateau is not a proved bound. The score 0.902 is one replay of one scan. It is not a ceiling.

The radial mask did not close the gap from 0.896 to 0.9. Outlier fill, the depth window, and a raised denoise cutoff also failed that gap. These are failed interventions. They do not prove that no other representation can pass 0.9.

t21 and t22 have no saved parameter file. Movements inside 0.003 mean IoU are inside the plateau. I ran one scan, with no repeat.
