# Sample orientation, K recovery, and background ceiling

Status: provisional. Scope: development family `sample` on `data/scans/sample.txt`. Not an accepted claim.

## What was tested

Retune of detecting/SAM parameters under a budget of about 20 trials, aiming for development mIoU > 0.9 under the canonical drive orientation used by CoLab_V2.

## Observations

1. Relative to historical CoLab SAM templates, correct drive alignment flips K-wedge handedness. Enabling `mirror_k_geometry` recovers K IoU (about 0.784 → 0.88) and lifts overall mIoU from about 0.880 to about 0.895.
2. Best retained SAM knobs for this family: `mirror_k_geometry: true`, `K_height: 1120`. Negative `angle` alone or with mirror collapses mIoU. Swapping detecting oblique signs hurts. GT oracle prompts without mirror do not close the gap.
3. Plateau under SAM/detect knobs is about 0.895. Mid denoise mask `2.72–2.78` with the same SAM settings reaches about 0.896. Offline post-hoc radial clamp ceilings near 0.897. Tight radial mask `2.735–2.76` raises Bg IoU but drops overall mIoU to about 0.845 by damaging lining.
4. Residual background errors are mostly GT-background points with lining-like radius that denoise keeps and SAM labels as adjacent lining classes. Median distance to lining in `(h, θ)` is small (~0.04), so cylinder radial gating alone does not separate them cleanly.

## Working implication

Clearing 0.9 on this family likely needs template or geometry changes that shrink lining spill into neighbouring background, not further radial gating of the same kind. Treat this as a provisional experiment note until registered as a claim with pinned revisions and evidence digests.

## Artefacts

Trial log and summaries under `data/development/sample/tune/` (local development archive; not knowledge acceptance).
