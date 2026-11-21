# Daily DIKW → logs + wisdom

Run once per day at **10:00 PM Europe/London**.

## Inputs (read in order)

1. `dikw/data/` (including `dikw/data/logs/`)
2. `dikw/information/`
3. `dikw/knowledge/` (`research_notes/`, `hypotheses/`, `claims/`)
4. Current `dikw/wisdom/README.md`
5. Raw development artefacts only when needed to resolve a conflict

## Rules

- Write the day’s narrative to `dikw/data/logs/YYYY-MM-DD.md`. That file is a log, not wisdom.
- Prefer tested knowledge over provisional notes. Label provisional insights as provisional.
- A high mIoU, a single successful run, or a persuasive explanation is not enough for a standing principle.
- Standing principles need applicable conditions, linked knowledge, uncertainty, and known counterexamples.
- Do not invent evidence. If nothing is reliable enough to promote, leave `dikw/wisdom/README.md` unchanged except for necessary suspend/revise notes.

## Outputs

1. Create or replace `dikw/data/logs/YYYY-MM-DD.md` with: what moved, candidates noted (not wisdom), parked/unresolved, next day’s focus.
2. Update `dikw/wisdom/README.md` **only** when synthesising a standing principle from tested knowledge — or when suspending/revising an existing one.
3. Do not put digests, trial narratives, or working notes into wisdom.

## Prompt (for the scheduled agent)

```text
You are the 10 PM DIKW synthesizer for CoLab_V2.

Read dikw/data (including dikw/data/logs), dikw/information, dikw/knowledge, and dikw/wisdom/README.md. Follow dikw/wisdom/DAILY_SYNTHESIS.md.

- Write today’s narrative to dikw/data/logs/YYYY-MM-DD.md (log only).
- Update dikw/wisdom/README.md only when promoting, suspending, or revising a standing principle backed by tested knowledge.
- Do not put logs into wisdom. Do not invent evidence. Do not commit unless asked.
```
