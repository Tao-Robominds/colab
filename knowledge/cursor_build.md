# Cursor build instructions

## Goal and fixed constraints

Implement this architecture around the actual SAM4Tun code. Improve final 3D semantic mIoU. Start with K-centre localisation, while running the whole pipeline for every decision-relevant experiment. Start with new evidence and newly curated expert references. Do not import historical trials or earlier learned proxy state.

Follow the supplied `SOUL.md`. Keep code free of comments and docstrings. Put descriptive instructions, prompts, assumptions, and findings in `knowledge/` or `wisdom/`. Do not convert untested notes into accepted knowledge merely because they occupy a directory named `knowledge`.

Use one replaceable LLM researcher and explicit deterministic components. Prefer existing project functions over a new orchestration framework. The researcher returns structured executable proposals; controllers own evaluation and release decisions.

## Build sequence

### 1. Connect the full runner

Map the actual repository's unfolding, denoising, enhancement, joint and K localisation, prompt, SAM, semantic assignment, and reprojection functions. Implement the real adapter in `src/rsi4tun/adapters.py`. Export every stage's artefacts and the final labels on original point identities.

Pin the source revision, executable environment, model weights, inputs, configuration, seeds, and stage outputs. An unsuccessful stage must return a failed run. Do not substitute a K-only run for a complete outcome.

Keep protected GT in a development-only store. Use separate processes or containers with deployment mounts that exclude GT. Python field validation is not an access-control boundary. The delivered skeleton does not provision that infrastructure.

### 2. Curate the initial reference pack

Obtain expert-approved artefacts covering the intended development design strata. Include depth maps with expected-support masks, independent boundary evidence, detected boundaries, K-centre results, prompts, masks, and final 3D outputs. Record expert review provenance and the scope of approval.

Implement the conversions from real artefacts to the contract in `evidence.py`. Test coordinates, units, circular seams, empty data, structural voids, and incompatible designs. Preserve raw evidence and conversion identities. Do not impose one tunnel's layout on another.

### 3. Construct and validate comparison-derived proxy inputs

Run the baseline, perform the comparison, and inspect its structured differences. Require the researcher to propose executable features with a concrete originating difference, target rationale, and known failure mode. Reject feature proposals that refer to unavailable evidence.

Fit the candidate proxy against final mIoU on development runs. Fit scaling and feature selection within the training partition. Use grouped validation and an independent final audit where feasible. Compare both predictive error and the mIoU of the configurations selected under an equal budget.

Freeze accepted feature code, reference policy, weights, applicability conditions, and evaluator identity. Start a new deployment episode when this release changes. Do not compare scores across releases as though they shared one scale.

### 4. Connect executable differential diagnosis

Give the researcher the comparison report, relevant accepted wisdom or tested knowledge, the full pipeline dependency map, permitted interventions, and the fixed budget. Include raw artefacts when a summary loses information needed for diagnosis.

Each hypothesis must specify input artefacts, assumptions, an executable response model, predicted observable intervals for the same interventions, and rejection conditions. Choose interventions expected to separate those models. Record an open possibility that neither explanation is adequate.

Before running an arm, seal the plan and its code identities in the RST record. Execute arms from the same baseline using matched inputs and planned seeds. Verify the manipulation and controlled conditions. Preserve every arm. Both arms may change; a null arm is optional, not a universal requirement.

### 5. Connect deployment retention and whole-code releases

Run every proposal from a complete source revision through `versions.py`. Include the entire code tree, not only its edited file or natural-language rationale. Keep runtime output outside the source checkout. Reject dirty or changed evaluated trees.

Keep the evaluator and release policy immutable during an episode. If candidate code changes any protected measurement or decision component, route that change to development instead of allowing self-approval.

When a treatment passes, atomically advance the accepted release pointer to the revision actually tested. Save a recoverable Git bundle, manifest, external dependency hashes, and evidence links. A failed proposal leaves the accepted release unchanged. An explicit rollback restores the prior accepted revision and compatible execution context.

### 6. Connect research memory

Write raw observations to the evidence archive. Write structured comparisons, predictions, and outcomes as information. Keep explanatory notes in `knowledge/research_notes/`, labelled as proposed or provisional where appropriate.

Require a separate reviewable gate for accepted knowledge: executable checks, supporting and contradicting evidence, scope, assumptions, uncertainty, and code paths. Require a synthesis of accepted knowledge before creating an actionable wisdom item. Retrieve only records whose scope matches the current case. Preserve superseded versions.

### 7. Run a bounded real pilot

Use a predeclared development split, one held-out deployment case, fixed budgets, and frozen acceptance criteria. Disable all synthetic records as learning input. Do not claim deployment mIoU gains before the independent evaluator opens its GT after all decisions are fixed.

If coverage is absent, request only the smallest representative labelled subset needed to address the stated gap. Move that subset into development. Keep a different case or subset for an unseen claim.

## Required validation before a research run

| Check | Required behaviour |
| --- | --- |
| Complete execution | Incomplete pipeline evidence cannot be accepted |
| Reference applicability | Wrong design or unverified registration abstains |
| Numerical validity | Empty support, non-finite values, and degenerate normalisers cannot yield a good score |
| Diagnostic registration | Changed predictions, measurements, or criteria after execution fail verification |
| Independent arms | Both arms start from the same baseline; one arm cannot inherit the other's edits |
| Proxy validity | Provisional features cannot silently replace the frozen gate |
| Version integrity | The promoted code is exactly the evaluated complete source revision |
| Rollback | Previous accepted code and its compatible identities are recoverable |
| GT isolation | The deployment process cannot read protected GT, including through artefact paths |
| Memory status | Synthetic records and unaccepted claims cannot be retrieved as tested knowledge |
| Source hygiene | No code comments or docstrings; prose lives under `knowledge/` or `wisdom/` |

## Researcher output discipline

Require structured outputs. References must resolve to existing artefacts, source revisions, or explicitly proposed new code. A literature reference may motivate a measurement, but it cannot substitute for its local implementation or validation. Searches must not expose protected project data. Record citations and their scope in `knowledge/`; pin any external implementation before using it.

The investigator may act autonomously within the campaign budget and permitted changes. It must not silently alter a criterion after seeing the current result. If no admissible experiment remains, stop and record the uncertainty.
