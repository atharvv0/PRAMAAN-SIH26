"""
select_model — see services/model_control/README.md and docs/architecture.md
"Core Principle: Separation of Concerns" ("Model Router decides *which* model
handles a capability").

Capability-driven selection only — this function must never branch on a specific
model id or name (e.g. `if capability == "coding": return get("qwen-coder")`).
Adding a model is done entirely by registering a new ModelAdapter with the right
`capabilities`/`modalities` (services/model_control/registry) — this file does not
change.

Selection order for a capability's candidate list:
  1. filter by modality (if requested) and, when given, security_classification
     (an adapter can opt out of restricted-data use via `metadata()["allow_restricted"]`
     — absent/True means it's allowed, since most local/self-hosted adapters are).
  2. prefer the first candidate whose health_check() passes, in registration order
  3. if none are healthy, fall back to the last candidate in the list (by
     registry_instance.py convention, the offline DemoModelAdapter is registered
     last for every capability precisely so it's the final fallback here)
  4. if there are no candidates at all for the capability -> ModelUnavailableError
"""
from __future__ import annotations

from services.model_control.adapters.base import ModelAdapter
from services.model_control.errors import ModelUnavailableError
from services.model_control.registry.registry import ModelRegistry


def select_model(
    registry: ModelRegistry,
    capability: str,
    modality: str = "text",
    security_classification: str | None = None,
    latency_budget_ms: int | None = None,  # noqa: ARG001 — reserved, see NOTE below
) -> ModelAdapter:
    # NOTE: latency_budget_ms is accepted now (per the ModelAdapter/router contract
    # in services/model_control/README.md) but not yet used to filter/re-rank
    # candidates — no adapter reports expected latency yet. TODO(Phase 2
    # continuation): once benchmarks/ produces real p50/p95 numbers per model,
    # rank healthy candidates by fit to latency_budget_ms instead of pure
    # registration order.
    candidates = registry.list_by_capability(capability, modality=modality)

    if security_classification == "restricted":
        candidates = [c for c in candidates if c.metadata().get("allow_restricted", True)]

    if not candidates:
        raise ModelUnavailableError(
            f"no model registered for capability='{capability}' modality='{modality}'"
        )

    for candidate in candidates:
        if candidate.health_check():
            return candidate

    # Nothing passed health_check — degrade to the last-registered candidate
    # (the offline fallback, by registry_instance.py convention) rather than fail
    # the whole task outright.
    return candidates[-1]
