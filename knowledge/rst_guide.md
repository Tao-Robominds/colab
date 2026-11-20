# RST records

## Meaning and scope

This workspace uses **Research State Transition (RST)** as a working name for the record connecting a registered research state to its observed outcome and next action. This expansion defines the local schema; it does not assert that an attached article uses the same acronym.

An RST record preserves evidence and decisions. It is not a transcript of internal reasoning, a natural-language substitute for code, or an automatic knowledge claim. Keep explanatory text in `knowledge/` and link it through `knowledge_ref`. Keep full code in the immutable source revisions that the record names.

`records.py` implements an immutable before record and a separate after record. `preregister_and_execute` in `orchestrator.py` seals the plan before starting the actual versioned arm runs, binds the registration receipt, and rejects pre-existing output directories and protected-evaluator changes. `verify_preregistration` checks both record and plan digests. `append_outcome` links the result to that before record, checks the planned arm commits, and creates a new file without overwriting the previous one.

## Record fields

| Record | Machine-readable content | Purpose |
| --- | --- | --- |
| Before | Campaign and protocol identity; synthetic status; comparison and candidate-signal paths; complete plan; plan digest; retrieved claim identities | Establish what existed and was predicted before execution |
| Plan | Baseline run and commit; comparison, signal, proxy, and evidence-contract digests; arm commits and trees; executable hypothesis entrypoints and source hashes; parameters; prediction intervals; units; manipulation checks | Bind the scientific comparison to exact executable versions |
| After | Before digest; plan digest; diagnosis; run identities; arm commits; treatment decisions; next action code; knowledge reference | Preserve what occurred and the ensuing action |
| Warning | Rejected operator identity, condition and evaluator identities, failed run and decision links | Prevent an identical failed retry under the same condition and frozen evaluator |
| Coverage event | Reference and observed design identities; comparison status; available development coverage; selected next action | Explain abstention without fabricating a quality score |

Deployment records reject protected GT fields. This is a record-level guard. Production deployments still require process and storage isolation. Private development evaluation records stay outside the deployment archive.

## Example 1: a discriminative experiment

**Synthetic fixture only.** This example tests implementation plumbing. It does not establish a tunnel mechanism, a proxy–mIoU relation, or segmentation improvement.

The baseline comparison has three relevant features. The boundary feature is selected as a new candidate before hypothesis design. It is absent from the active fixture proxy:

| Comparison feature | Baseline |
| --- | ---: |
| `depth_valid_coverage__delta` | −0.25 |
| `k_phase_rms_turns__delta` | +0.20 |
| `boundary_symmetric_distance_fraction__delta` | +0.05 |

Arm A repairs the fixture's three missing depth columns. Arm B applies a phase correction of 0.05 turns. Both run from the same baseline. The two programs predict **both arms**; the arms are not themselves the hypotheses.

| Program | Arm | Predicted depth response | Predicted K response | Predicted boundary response |
| --- | --- | ---: | ---: | ---: |
| `hypotheses.depth_limits_k` | A | +0.25 | −0.10 | −0.025 |
| `hypotheses.depth_limits_k` | B | 0 | −0.05 | −0.0125 |
| `hypotheses.phase_limits_k` | A | +0.25 | 0 | 0 |
| `hypotheses.phase_limits_k` | B | 0 | −0.05 | −0.0125 |

Each centre has a registered interval half-width of 0.005 in the corresponding units. These widths are demonstration parameters, not measured uncertainty. The model definitions and scope are in [the hypothesis note](hypotheses/depth_vs_phase.md).

The observed synthetic responses, in the table's metric order, are A: `(+0.25, −0.10, −0.025)` and B: `(0, −0.05, −0.0125)`. Their resulting boundary differences are +0.025 and +0.0375. The first prediction matches and the second fails. The recorded diagnosis is `h1_supported`; `causal_status` remains `unconfirmed`. The agreement of both models on B does not invalidate the discrimination supplied by A. Other explanations remain possible.

Manipulation validity comes from the configuration actually executed: A applies depth repair +0.25 and B applies phase correction +0.05. It is checked independently of the outcome. If a correctly applied intervention produces an unexpected null response, the hypotheses may fail; the experiment is not automatically labelled an invalid manipulation.

The boundary signal remains unvalidated. In this fixture it is proportional to K discrepancy, so it may be redundant. A discriminative response does not establish incremental predictive value for final mIoU.

The frozen fixture score is:

\[
P = 0.9 + 0.2\,d_{\mathrm{depth}} - d_{\mathrm{K}}.
\]

| Full run | Depth comparison | K comparison | Fixture score | Treatment result |
| --- | ---: | ---: | ---: | --- |
| Baseline | −0.25 | +0.20 | 0.65 | Starting release |
| A | 0 | +0.10 | 0.80 | Eligible and selected |
| B | −0.25 | +0.15 | 0.70 | Eligible, lower fixed score than A |

Selection uses the frozen rule, independently of which hypothesis matched. The accepted pointer advances to A's complete tested code revision. The arithmetic fixture is not a learned or validated research proxy. Any private synthetic mIoU calculation occurs only after deployment decisions have been fixed.

## Example 2: a failed treatment

**Synthetic fixture only.** Starting from accepted A, a follow-up proposal leaves six depth columns missing. Its comparison is `depth_valid_coverage__delta = −0.50` and `k_phase_rms_turns__delta = +0.30`. The frozen score is 0.50, below A's 0.80.

The treatment decision is `rollback`. The accepted release remains A. Preserve the failed run and its complete source revision. Save a warning keyed by the input condition, accepted baseline commit, frozen proxy, evidence contract, and operator. Do not reinterpret this result as evidence that every similar operator fails on every tunnel.

Repeating A's unchanged state gives an equal score and a `plateau` decision. That stops this exploitation episode. It does not prove a performance ceiling.

The warning and the failed arm are evidence. They are not automatically accepted knowledge or wisdom. A diagnosis may use them later only with their actual status and scope.

## Example 3: uncovered complex design

Suppose the available expert reference is scoped to a simple `1-1` lining design and the new tunnel is marked `5-1`. The comparison produces a `coverage_gap` before interpreting differences as defects. Do not fill in invented depth, boundary, K, or proxy values for that case.

Record the reference identity, the new design identity, the applicability decision, and the next action. If matching labelled development cases already exist, inspect that coverage. Otherwise, a justified and budgeted request can acquire one representative labelled subset. If the request cannot be satisfied, record `defer_unsupported_scope`.

New labels used to refit the method become development evidence. They do not preserve the same subset's status as an unseen evaluation case.

## Reading the generated records

Run the demo into a new output directory. The following paths are relative to that directory. The demonstration has been executed with the scores and decisions shown above; each new execution supplies its own actual identities.

| Generated path | Contents |
| --- | --- |
| `report.json` | Run summary, decisions, and generated evidence identities |
| `evidence/reference.json` | Synthetic expert-reference artefact bundle |
| `evidence/baseline_comparison.json` | Measurements and comparison-derived features before diagnosis |
| `evidence/candidate_signals.json` | Candidate signals linked to the baseline comparison |
| `evidence/candidate_proxy.json` | Comparison-derived proxy specification created before hypothesis design |
| `evaluator/proxy.json` and `evaluator/policy.json` | Frozen fixture evaluator and policy |
| `rst/synthetic_depth_vs_phase.before.json` | Sealed experiment registration |
| `rst/synthetic_depth_vs_phase.after.json` | Observed response checks and treatment decisions |
| `rst/warning.json` and `rst/plateau.json` | Failed follow-up and stopping evidence |
| `runs/reference/`, `runs/baseline/`, `runs/arm_a/`, and `runs/arm_b/` | Complete synthetic stage outputs |
| `runs/rejected_followup/` and `runs/plateau_repeat/` | Preserved rejected and tied runs |
| `archive/bundles/` and `archive/executions/` | Recoverable complete source revisions and execution receipts |
| `development_private/posthoc_fixture_audit.json` | Private synthetic GT evaluation after deployment decisions |

Use these generated files for their real hashes and commits. The documentation never supplies fabricated hash strings as verified evidence. The deployment process must not use the private post-hoc audit file to choose a treatment.

The RST and demonstration summary records carry `synthetic: true` and `learning_eligible: false`. Stage artefacts identify the `synthetic` backend. The knowledge gate rejects fixture evidence. The synthetic explanatory note is [here](research_notes/synthetic_example.md).

## What remains to connect

Production RST needs verified artefact storage, protected execution identities, real experiment budgets, and a retrieval index that respects claim status and scope. The supplied code implements record integrity and validation boundaries; it does not by itself establish an operating-system security boundary or validate a scientific claim.
