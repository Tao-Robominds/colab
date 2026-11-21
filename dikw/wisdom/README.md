# Wisdom

A wisdom item is an ordered strategy plus a fitted formula.

The strategy names each step, states a numeric prediction, states the rationale, and states the stop. The formula holds the coefficients. A paragraph does not stand in for the weights.

Promote an item only when evidence and executable support justify it. Directory location alone does not accept a principle. An item stays out of `configs/protocol.json` `accepted_wisdom` until a later grouped release.

## What belongs here

- An ordered strategy with a prediction and a rationale on every step.
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

Family `sample`, scan `data/scans/sample.txt`.

- Strategy: [`sample_tune_strategy.md`](sample_tune_strategy.md)
- Formula: [`sample_proxy.json`](sample_proxy.json)

The formula was refit after the radius experiment. `t29` and `t30` are the new rows. It is a development fit. It is not accepted wisdom.

Family `staggered`, scan `data/scans/1-1.txt`.

- Strategy: [`1_1_tune_strategy.md`](1_1_tune_strategy.md)
- Formula: [`1_1_proxy.json`](1_1_proxy.json)

The formula was fit on the 1-1 arms. It is a development fit. It is not accepted wisdom. It does not replace the sample prior.
