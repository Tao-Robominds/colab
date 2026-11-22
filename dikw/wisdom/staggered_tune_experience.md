# Staggered tune experience

Scope: scans `data/scans/sample.txt` (family `sample`) and `data/scans/1-1.txt` (family `staggered`). Two scans in one page. This is a development prior. It is not accepted wisdom. `configs/protocol.json` lists no accepted wisdom.

Arm traces stay in this file for later ablation. The noref Evidence / Diagnosis / Stop page without arm names is [`staggered_tune_experience_noref.md`](staggered_tune_experience_noref.md).

Artifact measurements: [`dikw/information/research_notes/tune_artifact_diffs.md`](../information/research_notes/tune_artifact_diffs.md). Seam facts: [`1_1_seam_diagnosis.md`](../information/research_notes/1_1_seam_diagnosis.md). Sample proud facts: [`sample_orientation_and_bg_ceiling.md`](../information/research_notes/sample_orientation_and_bg_ceiling.md). Scores: [`dikw/data/sample_tune.md`](../data/sample_tune.md), [`dikw/data/1_1_tune.md`](../data/1_1_tune.md). Formulas: [`sample_proxy.json`](sample_proxy.json), [`1_1_proxy.json`](1_1_proxy.json).

## How to read this page

Evidence is the difference between prediction artifacts: which points changed label, on which ring, across which radius, theta, or intensity. A class-IoU table is not Evidence. Arm names appear once as a trace.

Selection is the ground-truth check that kept or rejected that artifact change. Diagnosis, Proposal, Prediction, Rationale, and Stop follow from the artifact difference. Stop is where the same kind of artifact change ceases to raise mean IoU.

Code order in `sam4tun/staggered/5_sam.py`: proud drop, then `ring_label_shifts`, then `split_ring_source_by_theta`, then `drop_dark_lining`.

## Proxy

Both formulas stay `development_fit_pending`. The coefficients live in the JSON files. This page does not restate them.

## Sample scan (`data/scans/sample.txt`)

### 1. Keep a positive template angle with the K mirror on

Evidence: Against a positive-angle mirrored cloud, a negative angle moves about 585,000 predicted labels. Almost all of those points go to background (about 579,000), concentrated on pred_ring 1. Restoring a positive angle with the mirror on moves a similar count back from background onto the lining rings. Trace: `t02` / `t03` / `t04`.

Configuration: angle +7.52 and `mirror_k_geometry` true, against angle −7.52.

Selection: ground truth keeps the positive-angle mirrored labels. Mean IoU rises when those labels return from background.

Diagnosis: a negative template angle empties the lining into background on the aligned cloud. The mirror alone does not protect against that empty.

Proposal: keep the template angle positive. Set `mirror_k_geometry` true.

Prediction: a negative angle returns hundreds of thousands of lining points to background.

Rationale: the aligned label change is lining→background under a negative angle, and background→lining when the angle is positive again.

Stop: `t04` with the mirror on and angle negative repeats the emptying. K-block can rise while the lining empties. A higher K-block count is not success.

### 2. Keep the mid radial mask

Evidence: Against the tight mask, the mid mask changes class counts without a shared point order: background falls by about 12,500; A2 rises by about 4,600; A1, B1, K, and A3 rise. The tight mask against the previous cloud raises background by about 17,400 and cuts A2 by about 7,000. Trace: `t21` / `t22`.

Configuration: denoise mask 2.72–2.78 against 2.735–2.76.

Selection: ground truth keeps the mid-mask class counts. Mean IoU rises.

Diagnosis: the tight radial mask removes lining mass into background. The mid mask restores lining mass.

Proposal: keep the denoise mask at 2.72–2.78.

Prediction: tightening the mask raises background count and lowers lining counts.

Rationale: the unaligned class deltas point the same way as the sealed scores.

Stop: `t25` raises `smoothing_offset` to +0.005. Background rises by about 145,000. Every lining class falls. Do not raise the denoise cutoff to buy background.

### 3. Drop proud lining at 5 mm within 10 cm

Evidence: Points that stand proud of the local predicted lining are enriched for background relative to inset points of the same residual. Dropping only the proud side returns those points to background. The absolute 5 mm residual also drops 4,021 true lining points that sit inset. Trace: Arm G / Arm F in `RADIUS_PREDICTION.md` and `sample_orientation_and_bg_ceiling.md`. Arm directories for `t29` / `t30` are gone.

Configuration: `drop_proud_lining` at 5 mm residual and 10 cm neighbourhood on the mid-mask labels.

Selection: ground truth keeps the proud cut. Mean IoU rises above 0.900. The absolute cut stays under 0.900.

Diagnosis: proud predicted lining is spill. Inset residual is mostly true lining.

Proposal: after labels exist, apply the relative 5 mm proud cut at 10 cm.

Prediction: spill falls and mean IoU crosses 0.900. The absolute cut does not.

Rationale: the enrichment of background among proud points, and the true-lining loss under the absolute cut, select the relative rule.

Stop: Arm F (absolute residual). `t26` moves about 28,700 labels, mostly lining→background on pred_ring 1. `t27` abstains 13,051 contested pixels to background; contested pixels are mostly true lining. `t28` changes 86 points. Those moves do not beat the proud cut.

## 1-1 scan (`data/scans/1-1.txt`)

### 1. Turn the K mirror on

Evidence: First finished cloud on this scan. Predicted lining is present across rings 0–9. Trace: `a01`.

Configuration: `mirror_k_geometry` true.

Selection: this is the starting artifact for every later kept change on this scan.

Diagnosis: later kept edits keep this mirror setting.

Proposal: set `mirror_k_geometry` true before other SAM knobs on this scan.

Prediction: later arms that keep the mirror on remain the comparison stack for proud, mask, and label rules.

Rationale: every later kept experience starts from a mirrored stack.

Stop: this page has no arm that turns the mirror off after `a01`.

### 2. Drop proud lining at 5 mm and 10 cm

Evidence: Against the mirrored cloud, 40,735 predicted lining points return to background. Every change is lining→background. The changed points sit across rings; r p50 is 2.763. Trace: `a02` on `a01`.

Configuration: `proud_replay` at 5 mm residual and 10 cm neighbourhood. Code: `drop_proud_lining`.

Selection: ground truth keeps that drop. Mean IoU rises. Spill falls.

Diagnosis: those proud predicted lining points are spill on this cloud.

Proposal: after labels exist, apply the 5 mm proud cut at 10 cm.

Prediction: tens of thousands of lining points return to background and mean IoU rises.

Rationale: the aligned change is only lining→background.

Stop: `a05` on `a01` at 3 mm returns 100,524 lining points to background. Mean IoU falls. B1 and A1 fail the lining guard. Do not tighten below 5 mm.

### 3. Keep the mid radial mask

Evidence: Against the 3 mm proud replay, the mid-mask full run is an unaligned cloud. Background falls by about 48,000. B1, K, B2, and A3 rise. Trace: `a06` versus `a05`. Against the mid-mask stack, widening the proud neighbourhood to 15 cm while leaving the mask wide (`a11` on `a08`) moves mass among lining classes and mean IoU falls.

Configuration: denoise mask 2.72–2.78, mirror on, proud 5 mm at 0.1 m.

Selection: ground truth keeps the mid-mask stack. Mean IoU rises into the 0.85 band.

Diagnosis: the mid mask restores lining mass that the tight residual and wide family mask do not.

Proposal: keep the denoise mask at 2.72–2.78 with the mirror and the 5 mm cut.

Prediction: leaving the mid mask, or replacing it with a wider proud neighbourhood alone, returns mean IoU toward the 0.81 band.

Rationale: the class-count shift toward lining under the mid mask, and the failure of `a11`, bound the mask.

Stop: local knobs on the mid-mask stack (`a07`–`a13`) change a few hundred to a few thousand class counts and do not open the next band. AB height 3100 / 3400 on `a13` (`a14`, `a15`) moves A2 by tens of thousands and mean IoU falls; on `a15` K rises while mean IoU falls.

### 4. Cycle lining labels on pred_ring 2

Evidence: Against `a17` labels, 44,506 predicted labels change. Every changed point sits on pred_ring 2. Transitions are the +1 lining cycle: B1→A1 14,386; B2→K 11,226; A1→A2 7,372; K→B1 4,968; A3→B2 4,895; A2→A3 1,659. No other ring moves. Trace: `a34`. Full run `a36` reproduces a class-count shift of the same shape. Seam note: on pred_ring 2 the predicted lining is one step behind the ground-truth cycle.

Configuration: `ring_label_shifts={"2": 1}` after the proud drop.

Selection: ground truth keeps the cycle. Mean IoU rises from the mid-mask band into the 0.89 band.

Diagnosis: pred_ring 2 carries a one-block circumferential offset. A label cycle on that ring alone corrects it.

Proposal: on this scan, set `ring_label_shifts` to `{"2": 1}` after the proud drop.

Prediction: removing the shift returns the ring-2 labels and mean IoU to the mid-mask band.

Rationale: the aligned change is confined to pred_ring 2 and matches the cycle map.

Stop: `a40_wrap_theta_on_a13` changes 853,675 labels. Dominant transitions are B2→A3, A3→A2, B1→B2 across many rings. Mean IoU falls to 0.382. Filling the theta border is not a retainable treatment. Proud retunes on the shifted labels (`a38`–`a42`) return 1,176–19,026 points to background and stay in the 0.89 band.

### 5. Split original B2 on pred_ring 2 by theta

Evidence: Against `a13`, same-order comparison changes 64,867 labels; 44,944 of them sit on pred_ring 2. Ring-2 transitions include the cycle plus B2→B1 7,565 and B2→K 3,550. The seam note: original B2 rows on that ring have theta 10.15–13.46, and ground truth on them changes from B1 to K near 12.4. Stage 5 shifts 46,611 points and splits 11,252. Trace: `a44` on `a13`.

Configuration: `ring_label_shifts={"2":1}` and `ring_theta_split` ring 2, source label 6, theta 12.4, below label 2, at or above label 1. Code: `split_ring_source_by_theta`.

Selection: ground truth keeps the cycle-plus-split. Mean IoU rises to 0.898.

Diagnosis: after the cycle, original B2 on that ring still covers two classes that separate along theta.

Proposal: keep that split on this stack. Do not publish 12.4 as a released gate.

Prediction: a repeat full run scores near 0.898. Cuts at 12.3 and 12.5 do not separate from 12.4 on the frozen labels.

Rationale: the ring-2 transitions and the recorded theta span name the same place as the seam rewrite.

Stop: 12.4 is not a detector for an unseen tunnel.

### 6. Return dark predicted lining below −1400 to background

Evidence: Against `a44`, same-order comparison changes 40,738 labels. Lining→background is 26,071. Of those, 22,914 have intensity below −1400 on the a44 cloud. Intensity p50 of lining→background is −1480. Stage 5 drops 23,387 dark lining points. Background class count rises by about 22,000. Trace: `a45` on `a44`. Code: `drop_dark_lining`.

Configuration: `dark_lining_below` −1400 on the a44 stack. Ring-2 shift and theta split stay.

Selection: ground truth keeps the dark cut. Mean IoU rises to 0.917. A2 rises with it.

Diagnosis: after the cycle and the split, dark predicted lining still harms the labels. Returning those points to background fixes that mass.

Proposal: on this stack, set `dark_lining_below` to −1400 and keep the ring-2 shift and the theta split.

Prediction: a repeat full run stays near 0.917.

Rationale: the lining→background points concentrate below −1400 on the parent cloud.

Stop: do not treat −1400 as a released gate. The class mix of the dropped points is not in the result file.

## Limits

One seed per scan. Best stage-6 mean IoU on 1-1 is 0.917. Best sample replay is 0.902. Those are observed scores. They are not proved bounds.

The ring, the cycle direction, the theta cut, and the intensity cut were chosen with labels on 1-1. Deployment that cannot read ground truth can keep a pack that was already chosen. It cannot use those three label rules as a detector.

Full per-run measurements stay in `tune_artifact_diffs.md`. This page keeps the differences ground truth raised.
