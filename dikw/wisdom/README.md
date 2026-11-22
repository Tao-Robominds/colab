# Wisdom

A wisdom item is a tune experience plus a fitted formula.

The experience names each kept rise, states Evidence, Configuration, Selection, Diagnosis, Proposal, Prediction, Rationale, and Stop. The formula holds the coefficients. A paragraph does not stand in for the weights.

Promote an item only when evidence and executable support justify it. Directory location alone does not accept a principle. An item stays out of `configs/protocol.json` `accepted_wisdom` until a later grouped release.

## What belongs here

- A tune experience whose evidence comes from arm artifacts.
- A fitted formula with centres, scales, weights, and intercept.
- A stated scope: which family, which scan, which fit rows.
- Confirmed stops from the same experience. A single miss stays in `dikw/information/research_notes/` until the stop is confirmed.

## What does not belong here

- Trial narratives and daily logs. Those stay under `dikw/data/logs/`.
- Working notes and open explanations. Those stay under `dikw/information/research_notes/`.
- Hand-picked weights described as learned.
- A released gate. A prior with receipt `development_fit_pending` is not a released proxy.

## Standing principles

_None accepted yet._

## Current prior

Scans `data/scans/sample.txt` and `data/scans/1-1.txt`.

- Experience (with arm traces): [`staggered_tune_experience.md`](staggered_tune_experience.md)
- Experience (noref Evidence / Diagnosis / Stop): [`staggered_tune_experience_noref.md`](staggered_tune_experience_noref.md)
- Formulas: [`sample_proxy.json`](sample_proxy.json), [`1_1_proxy.json`](1_1_proxy.json)

The experiences are built from prediction-artifact differences between tune arms. The traced page keeps arm names for ablation. The noref page does not. The full per-run measurements are in `dikw/information/research_notes/tune_artifact_diffs.md`. Both formulas are development fits. Neither is a released proxy. Neither is accepted wisdom.
