# Executable evidence contract

Status: specification. Thresholds and example values are not calibrated research results.

## What a reference contributes

An expert reference is a versioned collection of artefacts judged suitable for a defined tunnel design and processing condition. It contributes examples of measurable stage behaviour. It does not supply ground truth for another tunnel.

Record who curated the pack, the source scan identity, pipeline and measurement revisions, coordinate conventions, sensor and sampling context, lining design, and the conditions of expert approval. Keep private GT and annotations outside the deployment-visible pack. A newly curated pack is permitted in the fresh campaign; historical trial outcomes and fitted coefficients are not silently imported with it.

Use several references when available. Store their spread and support counts rather than treating one number as an exact ideal. The delivered comparator evaluates one declared reference–observation pair. Selecting from a bank of design strata, population envelopes, and uncertainty estimates remains an integration task. Freeze the selection rule before evaluating the current proposal; do not select whichever reference makes its result look best.

## Required artefacts

| Artefact | Minimum representation | What it preserves | What it does not establish |
| --- | --- | --- | --- |
| Depth map | Depth values, validity mask, expected-support mask, physical grid scale, angular periodicity | Sampled surface and missing-data structure | Correct segmentation or semantic identity |
| Independent boundary evidence | Edge locations extracted independently of the proposed boundary detector, with method identity | Available geometric support for a boundary | That every observed edge is a lining joint |
| Detected boundaries | Locations per ring, coordinate convention, detector revision | The proposed partition geometry | Correct boundary class or segment name |
| K-centre result | Coordinates, ring association, registration and semantic identity status | Estimated K placement and consistency | True K position without suitable evidence |
| Prompts and SAM masks | Prompt coordinates/types, mask identities, confidence where available | The actual input and output of SAM | Correct semantic assignment |
| Final 3D output | Original point identities and predicted class identities | The complete decoded segmentation | Accuracy without permitted GT evaluation |

Export all stages even when only depth, boundaries, and K-centre enter the initial comparator. Keep the raw representation so a later measurement can be computed without inventing an earlier observation.

## Comparability gate

Before computing a quality-relevant deviation, check design family and layout, units and scale, coordinate/unwrap conventions, expected support, and registration requirements. Distinguish these outcomes:

- **Comparable:** the declared comparison is supported by metadata and the representation.
- **Partial:** only a valid subset is available, for example when K semantic identity is unresolved. Preserve the limitation and omit unavailable features.
- **Coverage gap:** the reference pack does not cover the current design or condition.
- **Insufficient reference:** the pack lacks the required expert-review identity.
- **Invalid evidence:** required data are missing, non-finite, inconsistent, or empty.

Only valid, applicable features may enter a frozen reference-based gate. A partial comparison can be scored only when every feature required by the active validated proxy is available; it cannot impute the missing feature as a favourable value. Coverage gaps, insufficient references, and invalid evidence do not produce a score. A coverage gap does not mean the new tunnel is defective. For example, a complex lining layout must not be judged against the expected segment count or K arrangement of a simple layout.

Do not compare raw cross-tunnel pixels unless correspondence is established. Use physical or design-normalised coordinates when correspondence is unnecessary. Record every transform, resampling operation, and masked region. State which information each transformation removes.

## Initial executable measurements

### Depth readiness

Measure valid coverage only over the mask of locations where observations are expected:

\[
C_{\mathrm{depth}} = \frac{|V \cap S|}{|S|}.
\]

Here, `V` is valid measured support and `S` is expected support. Structural voids excluded from `S` are not failed measurements. An empty `S` is invalid evidence.

Also measure the largest connected missing region as a fraction of expected support. Respect the periodic seam when the representation wraps azimuthally. Two maps with identical coverage can have very different missing-region structure.

These measures inspect support coverage and hole structure. They do not measure noise, retained detail, depth accuracy, useful contrast, or the correctness of inpainting. The real adapter must preserve which samples were observed and which were imputed, along with their transformation provenance. Filling an empty pixel must not be treated as proof that its depth became accurate. Add further readiness measurements only when their definitions and target relevance are supported.

### Boundary detections

Use independently extracted geometric evidence. Calculate both the fraction of detected boundary locations supported by that evidence and the fraction of available evidence explained by detections. Keeping both prevents a detector from appearing good merely by returning very few boundaries or an excessive number of boundaries.

Calculate symmetric location discrepancy with an explicit matching rule and normalisation. Use circular distance for azimuthal positions. Keep unmatched detections and unmatched support in the record. Do not hide them through favourable nearest-neighbour matching.

Expected counts and spacing must come from applicable design metadata. A count difference without an applicable design is a coverage question, not an error score. If independent support is empty, return invalid evidence rather than a perfect similarity score.

### K-centre evidence

Measure registered consistency across comparable rings in design-normalised units. Preserve any unresolved K semantic identity. Low positional spread can be achieved by repeatedly choosing the wrong location; consistency alone does not show correctness.

Before using cross-ring spread, confirm that registration preserves meaningful K variation. Do not independently align every ring to its estimated K position and then report the resulting zero spread as evidence. That would remove the phenomenon being measured.

### Full-output safeguards

Retain the final semantic labels and original point correspondence even when no deployment GT is available. Check completeness and class-schema consistency. In development, score mIoU on the declared class set and all eligible original points. Do not improve evaluation by dropping unassigned or difficult points, or by choosing a label permutation after seeing GT.

## From differences to a candidate proxy

For each proposed feature, preserve its originating comparison, executable function identity, units, applicability scope, direction convention, missing-data behaviour, and anticipated failure modes. The feature can depend on several comparisons when that dependency is explicit.

A possible candidate vector contains depth support, missing-region extent, boundary support, independent-edge coverage, boundary discrepancy, and K-centre consistency. Its weights must not be hand-selected and described as learned. The synthetic demonstration uses fixtures only; real coefficients require development fitting.

The development target is final mIoU from complete runs. Compare the candidate release against the incumbent using fixed data grouping, budgets, and acceptance criteria. Freeze the feature code, transformations, reference selection, weights, and scope together.

If evidence reveals an unmodelled condition, preserve the diagnostic signal without granting it acceptance authority. Revise and validate a proxy in development. Never fit a new feature or its threshold to the observed diagnostic outcome and present the resulting match as a preregistered prediction.

## Evidence trace

Each comparison must be recoverable through:

**Reference identity → observed artefact identity → executable measurement revision → comparison result → candidate feature revision → registered diagnosis → full-run outcome → acceptance decision.**

Use content hashes and immutable record identities. The machine record carries measurements and links. Explain the representation, assumptions, and conclusions in `dikw/information/research_notes/`, `dikw/knowledge/`, or `dikw/wisdom/`, not in code comments.
