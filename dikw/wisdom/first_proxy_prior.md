# First proxy prior for the sample scan

Status: a prior for the first proxy. Family `sample`. Scan `data/scans/sample.txt`.

This prior guides the next diagnosis. It has no fitted weights. It is not a released proxy. `configs/protocol.json` still lists no accepted wisdom.

Linked knowledge: `dikw/knowledge/research_notes/sample_orientation_and_bg_ceiling.md`.

## Principle

I judge a change on this scan by 6-class mean IoU.

Until a proxy is fitted and checked against that target, I carry two checks forward, and I refuse two shortcuts.

The checks are K-wedge agreement with this drive orientation, and AB height held at 3239.77.

The shortcuts are a higher K-block IoU, and a higher background IoU.

## Target and measurement

The target is 6-class mean IoU on the full scan, as stage 6 writes it.

The K-wedge check is the setting `mirror_k_geometry` under this orientation. Turning it on moved mean IoU from 0.880 to 0.894 in `t03_mirror_k`.

The AB-height check is distance from 3239.77. AB height 3300 dropped mean IoU to 0.839. AB height 3200 dropped it to 0.881.

## Assumptions

I assume the next comparison uses this scan, this orientation, and the same 6-class scorer.

For t01–t20, unfolding, denoising, and enhancing stayed the copied baseline. `run_trial.py` never calls those three stages. The unwrapped cloud, the denoised cloud, the enhanced cloud, and the depth map are byte-identical across those 20 trials. I use that fact when I read a detect or SAM change.

t21 and t22 reran the early stages. The same Cartesian points receive different radius, angle, and chainage. Denoise labels differ from the copied cloud on 33,843 points in the tight run and on 5,389 points in the mid run. I do not read 0.896 as a SAM-only change on a fixed early pipeline.

I assume `θ` in the background-error count is circumferential metres. That assumption is stated with the measurement.

## Failure modes

A higher K-block IoU can arrive with a lower mean IoU. K height 1150 and AB height 3300 both did this.

A higher background IoU can arrive with a lower mean IoU. The tight full rerun scored background IoU 0.859 and mean IoU 0.845. The mid full rerun scored background IoU 0.849 and mean IoU 0.896. Stages 1 to 3 also changed in both runs, so I do not yet assign that gap to the cylinder alone.

Ground-truth prompts can score below the detector. At K height 1120 with the mirror on, they scored 0.890 against the detector's 0.895.

A negative template angle breaks the wedge check. Angle −7.52 scored mean IoU 0.267, and 0.286 with the mirror on. B1-block and A1-block IoU fell to 0. I reject that angle before another full run.

## Checked rule

On the t22 labels, returning a predicted lining point to background when it stands more than 5 mm proud of other predicted lining points within 10 cm raised mean IoU from 0.896 to 0.902. Spill fell from 35,856 to 28,702. The lining classes stayed within 0.02 of t22. The same cut with both signs scored 0.899 and did not clear 0.9.

The sample SAM config now sets that cut. Other families do not. This is one replay of one scan. It is not an accepted principle, and it is not a ceiling.

## Next experiment

I stop retuning the levers that missed: template scale 0.97, overlap abstention, a logit margin of 1.0, and the stage-2 and stage-3 arms.

A further comparison on this scan should be a fresh stage-6 score with the proud cut on, not another replay of the same labels. I will state the predicted mean IoU before that run.

## Scope

This prior applies to family `sample` on this scan. I do not use these levels on another family. One scan, and no repeated seed, bounds the uncertainty.
