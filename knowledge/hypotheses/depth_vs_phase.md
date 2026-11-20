# Depth support versus phase assignment

Status: executable demonstration hypotheses. Synthetic: true. Learning eligible: false.

## Shared evidence and interventions

Both hypotheses consume the same baseline comparison and predict responses to the same intervention vectors. Their functions live in `src/rsi4tun/hypotheses.py`. The experiment plan pins that source file's hash before execution.

The observables are changes in `depth_valid_coverage__delta`, `k_phase_rms_turns__delta`, and `boundary_symmetric_distance_fraction__delta`. The boundary feature is the newly selected candidate and is absent from the active fixture proxy. These responses are changes relative to the common baseline, even though each input feature is already a difference from an expert reference. Keep the two subtraction levels explicit.

Arm A declares `depth_repair_fraction = 0.25`. Arm B declares `phase_correction_turns = 0.05`. The fixture uses additive deterministic effects. This assumption describes the fixture only.

## H1: depth support contributes to K error

Entrypoint: `rsi4tun.hypotheses:depth_limits_k`.

Parameters: `depth_to_k = 0.4`, `direct_phase_effect = 1.0`, and `interval_half_width = 0.005`.

For depth repair `r` and phase correction `c`, the model predicts:

\[
\Delta d_{\mathrm{depth}} = r, \qquad
\Delta d_{\mathrm{K}} = -0.4r-c.
\]

Both programs additionally predict:

\[
\Delta d_{\mathrm{boundary}} = \Delta d_{\mathrm{K}}/4.
\]

This proportionality is part of the synthetic response model, not a physical law.

H1 predicts that A improves depth coverage by 0.25, reduces K discrepancy by 0.10 turns, and reduces boundary discrepancy by 0.025. It predicts that B leaves coverage unchanged and reduces K discrepancy by 0.05 turns and boundary discrepancy by 0.0125.

## H2: phase assignment explains the K response

Entrypoint: `rsi4tun.hypotheses:phase_limits_k`.

Parameters: `incidental_depth_effect = 0.0`, `phase_to_k = 1.0`, and `interval_half_width = 0.005`.

The model predicts:

\[
\Delta d_{\mathrm{depth}} = r, \qquad
\Delta d_{\mathrm{K}} = -c.
\]

H2 predicts A's depth coverage change but no K or boundary response. It agrees with H1 about B's K and boundary responses. The discriminating observations are therefore A's K and boundary responses. B is an active intervention under both models; it is not forced into a null band.

## Prediction checks

The registered interval is the predicted centre ±0.005 for every listed observable in this fixture. A hypothesis matches only if all its specified arm responses fall within their registered intervals and the manipulation checks pass. The plan also requires a predeclared separation greater than its metric-specific response threshold. Manipulation checks use the configuration differences actually applied and bound to the input-stage digest, not the predicted outcome; an unexpected null result can therefore reject a response model without invalidating an applied intervention.

A result outside H1's intervals rejects H1's registered prediction. The equivalent rule applies to H2. Both matching or neither matching remains inconclusive. Predictions are not revised after observing an arm and then counted as the original experiment.

## Interpretation limits

These functions encode competing response patterns; they do not prove causal mechanisms. The synthetic outcome supports H1's registered pattern, while H2's pattern fails. Other models could produce the same pattern. A real causal interpretation would require defensible measurement, intervention specificity, registration, control of alternative explanations, and evidence beyond this fixture.

The candidate signals remain subject to separate development validation against final mIoU. The boundary signal is proportional to K discrepancy in this fixture and may be redundant. Agreement with a response model does not validate the proxy target relation or establish incremental predictive value.
