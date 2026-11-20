# Knowledge acceptance

Status: registry specification. This rebuild begins with no inherited empirical claims.

Keep four levels distinct:

| Level | Example | Storage role |
| --- | --- | --- |
| Data | A depth array, detected boundary coordinates, final point labels | Immutable artefact archive |
| Information | A design-conditioned comparison or registered experiment outcome | Machine-readable evidence and RST records |
| Knowledge | A relation supported by linked evidence and executable checks under stated conditions | Accepted claim record and explanatory text here |
| Wisdom | A scoped decision principle synthesised from accepted knowledge | Accepted principle in `dikw/wisdom/` |

Design documents, literature notes, candidate metrics, hypotheses, and provisional diagnoses may reside under `dikw/knowledge/` for organisation. Their explicit status remains specification, source note, proposed, or provisional. Directory location cannot promote them.

Accept a knowledge item only when its evidence and executable checks support the stated claim. Record assumptions, scope, uncertainty, counterexamples, relevant code paths, and exact source revisions. Link null and contradictory results as well as supporting ones. Software tests can establish contract behaviour; they cannot establish a segmentation claim using synthetic fixtures alone.

Keep statistical and causal claims separate. A metric associated with mIoU in development is an association under the tested distribution. A controlled intervention can support an effect under its assumptions. A unique cause requires adequate exclusion of alternatives; a supported response pattern alone does not provide that exclusion.

For a new claim, keep the initial text as proposed. Record the acceptance decision and the evidence version separately. If later evidence changes the claim's support or scope, create a new version and mark the previous version superseded or suspended. Preserve its evidence trace.
