# Synthetic executable example

Status: software fixture. Synthetic: true. Learning eligible: false.

This example exercises the architecture without running SAM or using research data. Its predefined relationships make the expected software behaviour inspectable. They are not observations of a real tunnel. Do not retrieve this note as tested research knowledge or wisdom.

## Registered setup

The fixture baseline has three missing columns in a twelve-column depth map, a depth-coverage difference of −0.25, a K-phase difference of +0.20 turns, and a boundary symmetric-distance difference of +0.05. Arm A repairs the missing columns. Arm B applies a direct phase correction of 0.05 turns. Every fixture run produces all required logical stage artefacts and final synthetic point labels.

The comparison is computed before the executable hypotheses are registered. The boundary feature is selected as the new candidate; it is absent from the active fixture proxy. Candidate feature records link to the comparison. The hypotheses and prediction regions are described in [the hypothesis note](../hypotheses/depth_vs_phase.md).

## Fixture outcomes

Arm A changes the depth comparison to zero, the K comparison to +0.10, and the boundary comparison to +0.025. Arm B leaves the depth comparison at −0.25 and changes the K comparison to +0.15 and the boundary comparison to +0.0375. These correspond to the registered first response model. The second model incorrectly predicts no K or boundary response to A.

The frozen arithmetic proxy scores the baseline at 0.65, A at 0.80, and B at 0.70. A is the highest-scoring eligible candidate. Acceptance promotes A's complete evaluated code revision. The diagnosis remains a supported fixture response model with an unconfirmed cause.

A subsequent failed proposal scores 0.50 and produces rollback evidence. The accepted revision remains A. An unchanged repeat of A ties and ends exploitation. The fixture also illustrates abstention for a reference design coverage gap, without assigning a spurious quality score to the uncovered case.

## Limits

The proxy coefficients are demonstration constants. They were not learned from tunnel GT. The prediction intervals are chosen fixture parameters. They are not calibrated measurement-error intervals. The boundary response is proportional to K response in the fixture and may add no predictive information. It still needs development validation. The simulated full stage sequence does not execute real SAM4Tun.

Private synthetic mIoU may be computed only after deployment decisions have been fixed. It illustrates evaluation separation, not a reported segmentation result. The fixture does not establish causal validity, transfer to a new tunnel, a generalisation bound, or a performance ceiling.

The generated machine records contain the actual code commits, hashes, measurements, and event links. This note explains their intended interpretation. It does not replace them.
