from dataclasses import asdict, dataclass
from typing import Protocol

from rsi4tun.contracts import OBJECTIVE, digest
from rsi4tun.proxy import CandidateSignal, ProxyProposal, propose_proxy
from rsi4tun.records import require_gt_free, retrieve_claims


@dataclass(frozen=True)
class ResearchContext:
    objective: str
    comparison: dict
    candidate_signals: tuple[CandidateSignal, ...]
    frozen_proxy_digest: str
    code_revision: str
    retrieved_claims: tuple[dict, ...]
    pipeline_contract_ref: str
    budget_full_runs: int
    public_source_refs: tuple[str, ...]
    candidate_proxy: ProxyProposal | None = None


def build_context(comparison: dict, signals: tuple[CandidateSignal, ...], *,
                  proxy_digest: str, code_revision: str, claim_registry: tuple[dict, ...],
                  scope_id: str, budget_full_runs: int, public_source_refs: tuple[str, ...] = ()) -> ResearchContext:
    require_gt_free(comparison)
    if type(budget_full_runs) is not int or budget_full_runs < 1 or not code_revision:
        raise ValueError("invalid_research_context")
    if any(signal.comparison_digest != digest(comparison) for signal in signals):
        raise ValueError("candidate_evidence_mismatch")
    names = [signal.feature_id for signal in signals]
    if len(set(names)) != len(names) or any(name not in comparison["features"] for name in names):
        raise ValueError("candidate_signal_not_measured")
    if any(signal.target != OBJECTIVE or signal.status != "unvalidated" for signal in signals):
        raise ValueError("invalid_candidate_signal_status")
    context = ResearchContext(OBJECTIVE, comparison, signals, proxy_digest, code_revision,
                              retrieve_claims(claim_registry, scope_id), "configs/evidence_contract.md",
                              budget_full_runs, public_source_refs, propose_proxy(signals, proxy_digest) if signals else None)
    require_gt_free(asdict(context))
    return context


class Researcher(Protocol):
    def propose_signals(self, comparison: dict, code_revision: str) -> tuple[CandidateSignal, ...]:
        ...

    def design_experiment(self, context: ResearchContext) -> dict:
        ...
