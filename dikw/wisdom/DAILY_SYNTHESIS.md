# Daily DIKW → logs + wisdom

Run once per day at **10:00 PM Europe/London**.

## Inputs (read in order)

1. `dikw/data/` (including `dikw/data/logs/`)
2. `dikw/information/`
3. `dikw/knowledge/` (`research_notes/`, `hypotheses/`, `claims/`)
4. Current `dikw/wisdom/README.md`, strategies, and formula JSON files
5. Raw development artefacts only when needed to resolve a conflict

## Rules

- Write the day’s narrative to `dikw/data/logs/YYYY-MM-DD.md`. That file is a log, not wisdom.
- Prefer tested knowledge over provisional notes. Label provisional insights as provisional.
- A high mIoU, a single successful run, or a persuasive explanation is not enough for a standing principle.
- Wisdom is a strategy plus a fitted formula. A strategy step needs an action, a numeric prediction, a rationale, and a stop. A formula needs centres, scales, weights, and intercept. Prose does not replace the coefficients.
- Revise a strategy step or refit a formula only when a new scored trial changes a prediction or a coefficient. The sample formula after `t29` and `t30` is that kind of refit.
- Do not invent evidence. If nothing is reliable enough to promote, leave `dikw/wisdom/README.md` unchanged except for necessary suspend/revise notes.
- Do not add a formula to `accepted_wisdom` from the night job. A grouped release is a separate decision.

## Outputs

1. Create or replace `dikw/data/logs/YYYY-MM-DD.md` with: what moved, candidates noted (not wisdom), parked/unresolved, next day’s focus.
2. Update `dikw/wisdom/README.md` **only** when promoting, suspending, or revising a standing principle backed by tested knowledge.
3. When a new scored trial changes a prediction or a coefficient, revise the matching strategy step and refit the formula JSON. Leave `accepted_wisdom` empty unless a separate grouped release accepts it.
4. Do not put digests, trial narratives, or working notes into wisdom.

## Prompt (for the scheduled agent)

```text
You are the 10 PM DIKW synthesizer for CoLab_V2.

Read dikw/data (including dikw/data/logs), dikw/information, dikw/knowledge, and dikw/wisdom. Follow dikw/wisdom/DAILY_SYNTHESIS.md.

- Write today’s narrative to dikw/data/logs/YYYY-MM-DD.md (log only).
- Update dikw/wisdom/README.md only when promoting, suspending, or revising a standing principle backed by tested knowledge.
- Wisdom is a strategy plus a fitted formula. Refit the formula only when a new scored trial changes a prediction or a coefficient. Do not put logs into wisdom. Do not invent evidence. Do not add to accepted_wisdom. Do not commit unless asked.
```
