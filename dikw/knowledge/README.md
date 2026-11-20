# RSI4Tun: executable evidence for SAM4Tun

## Purpose

Build a co-lab that improves **final 3D semantic mIoU** through executable evidence comparisons, competing hypotheses, and controlled changes to the complete SAM4Tun pipeline. K-centre localisation is the first research focus. Proxy scores guide deployment when its ground truth is unavailable; they do not replace the target.

This workspace implements contracts, artefact comparisons, standard-library ridge fitting, grouped proxy-validation gates, and a synthetic demonstration. It supplies the architecture and build instructions for connecting the real SAM4Tun repository. A synthetic pass is a software check. It is not evidence of improved segmentation, a validated research proxy, or a supported causal explanation.

The design emphasises executable representations and hypotheses, differential diagnosis, explicit proxy limits, and evidence-backed knowledge and wisdom. The documents here are **design specifications**, unless a claim record explicitly carries an accepted evidence status.

## Start here

1. Read [the architecture](architecture.md) and [the evidence contract](evidence_contract.md).
2. Follow [the Cursor build instructions](cursor_build.md).
3. Read the [RST guide](rst_guide.md) before connecting a researcher.
4. Inspect [knowledge acceptance](claims/README.md) and [wisdom acceptance](../wisdom/README.md).
5. Check the [workspace map](workspace.md), [principle mapping](principle_mapping.md), and [verification limits](verification.md).

Run from the workspace root:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m rsi4tun audit-code --root .
PYTHONPATH=src python -m rsi4tun demo --output /tmp/rsi4tun-example-001
```

Use a new output directory for each demonstration. The demo must label its records as synthetic. The real runner must fail explicitly until its adapter and execution controls are connected.

## Execution order

1. Run the full baseline and preserve its stage artefacts.
2. Compare those artefacts programmatically with applicable expert references.
3. Derive candidate measurement functions and proxy inputs from the comparisons. Validate and freeze a new proxy in development before using it for acceptance. Unvalidated signals may still guide diagnosis.
4. Retrieve scoped wisdom or tested knowledge. Form competing executable explanations of the observed differences.
5. Register predictions, interventions, thresholds, budgets, and code revisions. Execute complete pipeline runs from the same baseline.
6. Evaluate the predictions. Independently decide whether to retain the treatment under the frozen acceptance policy.
7. Preserve the entire accepted source revision, environment identity, artefact identities, and decision evidence. Update knowledge only when its separate evidence gate passes.

## Scope of this rebuild

Start a new empirical campaign. Do not ingest previous trials, learned coefficients, or earlier success narratives. Newly curated expert-reference artefacts are an explicit input to this architecture. Their provenance and applicability must be recorded; their existence does not establish deployment accuracy.

All code files contain executable content without comments or docstrings. Put descriptive material, prompts, assumptions, and research notes in `dikw/knowledge/`. Put accepted decision principles in `dikw/wisdom/`. Machine-readable records link to those documents and to immutable evidence.

Novelty remains the research purpose. For this task, final segmentation accuracy is the primary performance criterion. An observed plateau is a stopping event for an episode, not proof of an attainable ceiling.
