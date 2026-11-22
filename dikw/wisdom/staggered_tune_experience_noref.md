# Staggered tune experience (noref)

Scope: family `sample` and family `staggered`. This is a development prior. It is not accepted wisdom.

This page states Evidence, Diagnosis, Proposal, Prediction, Rationale, and Stop only. It does not name tune arms. The traced companion with arm names is [`staggered_tune_experience.md`](staggered_tune_experience.md).

Evidence is the difference between prediction artifacts: which points changed label, on which ring, across which radius, theta, or intensity. Stop is where the same kind of artifact change ceases to raise mean IoU.

Code order: proud drop, then ring label shift, then theta split, then dark lining drop.

## Sample scan

### 1. Keep a positive template angle with the K mirror on

Evidence: Against a positive-angle mirrored cloud, a negative angle moves about 585,000 predicted labels. Almost all of those points go to background (about 579,000), concentrated on pred_ring 1. Restoring a positive angle with the mirror on moves a similar count back from background onto the lining rings.

Diagnosis: a negative template angle empties the lining into background on the aligned cloud. The mirror alone does not protect against that empty.

Proposal: keep the template angle positive. Set the K mirror on.

Prediction: a negative angle returns hundreds of thousands of lining points to background.

Rationale: the aligned label change is lining→background under a negative angle, and background→lining when the angle is positive again.

Stop: with the mirror on and the angle negative, the emptying repeats. K-block can rise while the lining empties. A higher K-block count is not success.

### 2. Keep the mid radial mask

Evidence: Against the tight mask, the mid mask changes class counts without a shared point order: background falls by about 12,500; A2 rises by about 4,600; A1, B1, K, and A3 rise. The tight mask against the previous cloud raises background by about 17,400 and cuts A2 by about 7,000.

Diagnosis: the tight radial mask removes lining mass into background. The mid mask restores lining mass.

Proposal: keep the denoise mask at 2.72–2.78.

Prediction: tightening the mask raises background count and lowers lining counts.

Rationale: the class deltas point the same way as the sealed mean-IoU rise.

Stop: raising the denoise smoothing offset to +0.005 raises background by about 145,000. Every lining class falls. Do not raise the denoise cutoff to buy background.

### 3. Drop proud lining at 5 mm within 10 cm

Evidence: Points that stand proud of the local predicted lining are enriched for background relative to inset points of the same residual. Dropping only the proud side returns those points to background. The absolute 5 mm residual also drops 4,021 true lining points that sit inset.

Diagnosis: proud predicted lining is spill. Inset residual is mostly true lining.

Proposal: after labels exist, apply the relative 5 mm proud cut at 10 cm.

Prediction: spill falls and mean IoU crosses 0.900. The absolute cut does not.

Rationale: the enrichment of background among proud points, and the true-lining loss under the absolute cut, select the relative rule.

Stop: the absolute residual stays under 0.900. Shrinking the template moves about 28,700 labels, mostly lining→background on pred_ring 1. Overlap abstention sends 13,051 contested pixels to background; contested pixels are mostly true lining. A logit margin changes 86 points. Those moves do not beat the proud cut.

## 1-1 scan

### 1. Turn the K mirror on

Evidence: On the first finished cloud, predicted lining is present across rings 0–9.

Diagnosis: later kept edits keep this mirror setting.

Proposal: set the K mirror on before other SAM knobs on this scan.

Prediction: later stacks that keep the mirror on remain the base for proud, mask, and label rules.

Rationale: every later kept experience starts from a mirrored stack.

Stop: no later kept change turns the mirror off.

### 2. Drop proud lining at 5 mm and 10 cm

Evidence: Against the mirrored cloud, 40,735 predicted lining points return to background. Every change is lining→background. The changed points sit across rings; r p50 is 2.763.

Diagnosis: those proud predicted lining points are spill on this cloud.

Proposal: after labels exist, apply the 5 mm proud cut at 10 cm.

Prediction: tens of thousands of lining points return to background and mean IoU rises.

Rationale: the aligned change is only lining→background.

Stop: a 3 mm residual returns 100,524 lining points to background. Mean IoU falls. B1 and A1 fail the lining guard. Do not tighten below 5 mm.

### 3. Keep the mid radial mask

Evidence: Against the 3 mm proud cloud, the mid-mask full run is an unaligned cloud. Background falls by about 48,000. B1, K, B2, and A3 rise. Against the mid-mask stack, widening the proud neighbourhood to 15 cm while leaving the mask wide moves mass among lining classes and mean IoU falls.

Diagnosis: the mid mask restores lining mass that the tight residual and wide family mask do not.

Proposal: keep the denoise mask at 2.72–2.78 with the mirror and the 5 mm cut.

Prediction: leaving the mid mask, or replacing it with a wider proud neighbourhood alone, returns mean IoU toward the 0.81 band.

Rationale: the class-count shift toward lining under the mid mask, and the failure of the wide neighbourhood, bound the mask.

Stop: local knobs on the mid-mask stack change a few hundred to a few thousand class counts and do not open the next band. AB height 3100 or 3400 moves A2 by tens of thousands and mean IoU falls; at 3400, K rises while mean IoU falls.

### 4. Cycle lining labels on pred_ring 2

Evidence: 44,506 predicted labels change. Every changed point sits on pred_ring 2. Transitions are the +1 lining cycle: B1→A1 14,386; B2→K 11,226; A1→A2 7,372; K→B1 4,968; A3→B2 4,895; A2→A3 1,659. No other ring moves. A full run reproduces a class-count shift of the same shape. On pred_ring 2 the predicted lining is one step behind the ground-truth cycle.

Diagnosis: pred_ring 2 carries a one-block circumferential offset. A label cycle on that ring alone corrects it.

Proposal: on this scan, shift lining labels +1 on pred_ring 2 after the proud drop.

Prediction: removing the shift returns the ring-2 labels and mean IoU to the mid-mask band.

Rationale: the aligned change is confined to pred_ring 2 and matches the cycle map.

Stop: filling the theta border changes 853,675 labels. Dominant transitions are B2→A3, A3→A2, B1→B2 across many rings. Mean IoU falls to 0.382. That fill is not a retainable treatment. Proud retunes on the shifted labels return 1,176–19,026 points to background and stay in the 0.89 band.

### 5. Split original B2 on pred_ring 2 by theta

Evidence: Same-order comparison changes 64,867 labels; 44,944 of them sit on pred_ring 2. Ring-2 transitions include the cycle plus B2→B1 7,565 and B2→K 3,550. Original B2 rows on that ring have theta 10.15–13.46, and ground truth on them changes from B1 to K near 12.4. The full run shifts about 46,600 points and splits about 11,250.

Diagnosis: after the cycle, original B2 on that ring still covers two classes that separate along theta.

Proposal: keep the split of source label 6 on pred_ring 2 at theta 12.4 (below → B1, at or above → K). Do not publish 12.4 as a released gate.

Prediction: a repeat full run scores near 0.898. Cuts at 12.3 and 12.5 do not separate from 12.4 on the frozen labels.

Rationale: the ring-2 transitions and the recorded theta span name the same place.

Stop: 12.4 is not a detector for an unseen tunnel.

### 6. Return dark predicted lining below −1400 to background

Evidence: Same-order comparison changes 40,738 labels. Lining→background is 26,071. Of those, 22,914 have intensity below −1400 on the parent cloud. Intensity p50 of lining→background is −1480. The full run drops about 23,400 dark lining points. Background class count rises by about 22,000.

Diagnosis: after the cycle and the split, dark predicted lining still harms the labels. Returning those points to background fixes that mass.

Proposal: on this stack, return predicted lining below −1400 to background, and keep the ring-2 shift and the theta split.

Prediction: a repeat full run stays near 0.917.

Rationale: the lining→background points concentrate below −1400 on the parent cloud.

Stop: do not treat −1400 as a released gate. The class mix of the dropped points is not recorded.

## Limits

One seed per scan. Best stage-6 mean IoU on 1-1 is 0.917. Best sample replay is 0.902. Those are observed scores. They are not proved bounds.

The ring, the cycle direction, the theta cut, and the intensity cut were chosen with labels on 1-1. Deployment that cannot read ground truth can keep a pack that was already chosen. It cannot use those three label rules as a detector.
