# services/sandbox — Isolated Code Execution

**Owner:** Role 4 — Security/Governance (per `docs/team-structure.md`)

## What belongs here

- `runner/` — executes generated code in isolation: no network access, resource/time
  limits, ephemeral state, no secrets ever passed in
- `policies/` — resource limits, timeout config, allowed-operations list for the
  sandbox itself (separate from `services/governance/policy_engine`, which decides
  *whether* the agent may call the sandbox at all)

## What does NOT belong here

- The allow/deny decision to *use* the sandbox → `services/governance/policy_engine`
- Registering the sandbox as an agent-callable tool → `services/orchestrator/tools`
  (this package exposes a `ToolAdapter`-shaped interface; the registry entry itself
  lives with the orchestrator)

## Definition of Done (Phase 4, see docs/roadmap.md)

- [ ] Generated code executes with network access verifiably blocked
- [ ] Resource/time limits enforced and tested (a runaway script gets killed)
- [ ] No secrets or credentials ever reachable from inside the sandbox
