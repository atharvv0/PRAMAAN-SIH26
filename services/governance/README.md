# services/governance — Policy Engine, RBAC, Audit, Sovereignty Control Plane

**Owner:** Role 4 — Security/Governance (per `docs/team-structure.md`)

## What belongs here

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

- [ ] Unauthorized tool call denied before execution, with an audit entry
- [ ] Outbound network attempt blocked and shown live (sovereignty proof)
- [ ] Every model/tool/file-access event logged
