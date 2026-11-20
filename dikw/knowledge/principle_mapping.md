# Mapping from research principles to the implementation

This table describes design choices rather than experimental findings.

| Principle | Implemented representation | Remaining real-system obligation |
| --- | --- | --- |
| Represent observations through code | Typed artefact bundles; complete stage files; executable measurements; stage and bundle integrity checks | Map the real point cloud and SAM outputs into the contract without losing necessary information |
| Make explanations executable | Versioned hypothesis functions, registered response intervals and deterministic assessment | Develop and test meaningful response models; fixture coefficients have no scientific standing |
| Use differential diagnosis | Compare artefacts first; derive candidate signals; predict the same interventions; preserve inconclusive outcomes | Supply scoped knowledge and select useful experiments within the research budget |
| Separate causation from correlation | Response support, treatment retention and development validation have distinct records; causal status remains unconfirmed | State mechanisms and identifying assumptions for any later causal study |
| Identify method limits | Explicit missing-evidence statuses; incompatible reference abstention; plateau rather than ceiling | Test alternative representations and estimate performance limits using appropriate evidence |
| Adapt exploration | Diagnostic branches can gather evidence without changing the accepted operational release | Implement the bounded live episode scheduler and cost policy around the provided controller |
| Limit proxy claims | Comparison-derived inputs, training-bound fits, grouped validation and selected-configuration mIoU checks | Use independent acquisitions, equal search budgets, a final audit and a verified development-release loader |
| Convert experience to knowledge and wisdom | Immutable RST files; separate claim eligibility checks; scoped retrieval; synthetic records excluded | Review claim scope and supporting tests; version accepted knowledge and its synthesis into wisdom |
| Preserve research continuity | Full Git source snapshots, execution receipts, recoverable bundles and accepted-release references | Provision and verify external model/data dependencies and the real execution environment |
| Keep criteria fixed | Protected evaluator source, immutable preregistration and score-release identity checks | Separate trusted evaluator permissions from the code under investigation |

Raw data belong in the experiment archive. Structured comparisons and RST records are information. A file under `dikw/knowledge/` is not automatically tested knowledge. Accepted knowledge needs evidence and executable support. Wisdom needs an explicit synthesis of accepted knowledge. This rebuild contains no accepted scientific knowledge or wisdom from its synthetic demonstrations.
