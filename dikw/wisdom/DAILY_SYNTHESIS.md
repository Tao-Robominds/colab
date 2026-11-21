# Daily DIKW → logs + wisdom

Run once per day at **10:00 PM Europe/London**.

## Inputs (read in order)

1. `dikw/data/` (including `dikw/data/logs/` and `*_tune.md` score tables)
2. `dikw/information/` (`sources/`, `research_notes/`)
3. `dikw/knowledge/` (`hypotheses/`, `claims/`)
4. Current `dikw/wisdom/README.md`, strategies, and formula JSON files
5. Raw `performance.md` under `data/development/` only when the log table and the research note disagree

## Rules

- Write the day’s log to `dikw/data/logs/YYYY-MM-DD.md`. That file is a log, not wisdom.
- Prefer an index plus a score table over a narrative. Cumulative scores live in `dikw/data/*_tune.md`. The log cites those pages. It does not retell each arm.
- Prefer tested knowledge over provisional notes. Label provisional insights as provisional.
- A high mIoU, a single successful run, or a persuasive explanation is not enough for a standing principle.
- Wisdom is a confirmed strategy plus a fitted formula. A strategy step needs an action, a numeric prediction, a rationale, and a stop. The formula holds centres, scales, weights, and intercept. Prose does not replace the coefficients.
- Confirm a new wisdom step only when the sealed mean-IoU call held, the lining guard held, and the next round would act differently. A gain inside 0.003 does not qualify.
- Confirm a wisdom stop only when the same lever has missed that gate twice, or the strategy already predicted the miss and this measurement agreed. One miss stays in the research note.
- Refit a formula only in the same confirmation. Do not invent evidence. Leave `dikw/wisdom/README.md` unchanged except for necessary suspend/revise notes.
- Do not add a formula to `accepted_wisdom` from the night job. A grouped release is a separate decision.

## Outputs

1. Create or replace `dikw/data/logs/YYYY-MM-DD.md` with:
   - an index of finished episodes (best mIoU, best arm, link to `dikw/data/*_tune.md`)
   - for a live campaign, one score table with columns Arm, mIoU, class IoUs, Pred, Held, Guard
   - one lever line and one next line under that table
2. Update `dikw/wisdom/README.md` **only** when promoting, suspending, or revising a standing principle backed by tested knowledge.
3. Revise a strategy step or refit a formula JSON only when the confirmation gate above passes. Leave `accepted_wisdom` empty unless a separate grouped release accepts it.
4. Do not put digests, trial narratives, or working notes into wisdom.

## Prompt (for the scheduled agent)

```text
You are the 10 PM DIKW synthesizer for CoLab_V2.

Read dikw/data (including dikw/data/logs and *_tune.md), dikw/information, dikw/knowledge, and dikw/wisdom. Follow dikw/wisdom/DAILY_SYNTHESIS.md.

- Write today’s log as an index plus a score table. Cite dikw/data/*_tune.md for cumulative scores. Open performance.md only on a conflict.
- Update wisdom only when a step or stop is confirmed. Do not put logs into wisdom. Do not invent evidence. Do not add to accepted_wisdom. Do not commit unless asked.
```
