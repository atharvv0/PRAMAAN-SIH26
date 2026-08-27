# services/governance — Policy Engine, RBAC, Audit, Sovereignty Control Plane

**Owner:** Role 4 — Security/Governance (per `docs/team-structure.md`) — status as
of this pass: the project lead reports this module's real implementation already
exists with a teammate (Arpit), not yet merged into this repo. To keep the executor
genuinely wired end-to-end in the meantime, `policy_engine/base.py` and
`audit/log.py` below contain a **real, working default implementation** — not
scaffolding-only like the other unowned services. Replace `DefaultPolicyEngine`
with the team's real RBAC/permission logic behind the same `PolicyEngine.check()`
interface; `services/orchestrator/state_graph/executor.py` doesn't need to change
when you do.

## What's actually implemented here right now

- `policy_engine/base.py` — `PolicyEngine` interface + `DefaultPolicyEngine`, which
  denies any tool declaring network access and allows everything else. No RBAC, no
  per-document permissions. This is intentionally minimal — enough to make the
  "outbound request blocked, live" sovereignty demo real today.
- `audit/log.py` — `AuditLog`, in-memory only. Records every policy decision
  (allow AND deny) the executor makes. TODO: persist to Postgres or
  `audit/*.jsonl` instead of process memory.

## What belongs here (beyond the above)

- `policy_engine/` — the ALLOW/DENY gate every tool call must pass through
  (`Agent -> Tool Request -> Policy Engine -> ALLOW/DENY -> Tool`, never
  `Agent -> Tool` directly — see `docs/architecture.md` "Core Principle")
- `rbac/` — document-level and role-based access enforcement
- `network_monitor/` — deny-by-default egress enforcement + the live sovereignty proof
  (blocked outbound request, visibly logged, for the demo)
- `audit/` — `AuditEvent` log (`docs/agent-contract.md`): actor, action, target,
  allow/deny, policy reason, timestamp
- `evidence_layer/` — provenance/approval tracking that backs `EvidenceRecord`

## What does NOT belong here

- Agent/tool execution itself → `services/orchestrator` and tool-owning services
  (this module only decides allow/deny, it doesn't execute anything)

## Contract to implement

See `docs/agent-contract.md` → "AuditEvent". `services/orchestrator` will call into
this module before every tool execution — the interface it expects should be defined
here and documented back into `docs/agent-contract.md` once frozen.

## Definition of Done (Phase 7, see docs/roadmap.md)

- [x] Default deny-by-default network-egress policy live and gated into the executor
- [x] Every policy decision (allow + deny) recorded to the audit log
- [ ] Real RBAC / per-document permission logic (replace `DefaultPolicyEngine`)
- [ ] Audit log persisted (Postgres or `audit/*.jsonl`) instead of in-memory only
- [ ] Unauthorized tool call denied before execution, with an audit entry — done for
      the network-access case; extend for other permission types as RBAC lands
