# PRAMAAN `services/` — Engineering Report

Scope: the `services/` directory supplied in `services.zip` (102 Python files,
~6,300 lines, plus the `frontend/` React app). This report covers a full
static + dynamic audit, the bugs found, the fixes applied, and what was and
was not possible to verify in this environment.

**Sandbox constraint, stated up front:** this environment has no live
PostgreSQL, Qdrant, or Ollama server, and no network access to reach any
(the bash tool's egress is limited to package registries — pypi/npm/github —
not arbitrary hosts). Every fix was verified either by direct code
inspection, by running the real test suite, or by exercising the real
FastAPI app through `TestClient` against a throwaway SQLite database with
the documented offline fallbacks (`DemoModelAdapter`, in-memory vector
store, hashing embeddings). That is **not** the same as verifying against
real Postgres/Qdrant/Ollama — see Section G for exactly what that leaves
unverified, and Section I for the commands to close that gap on a machine
that has those services.

---

## A. Current State (before this pass)

| Subsystem | State |
|---|---|
| Backend API (FastAPI, routes, request/response schemas) | **PARTIALLY WORKING** — routes existed and were individually reasonable, but the test suite for this service could not even be *collected* (import error), and the app's own database-backed user lookup crashed on any UUID-based lookup outside Postgres. |
| Orchestrator (Planner, Executor, ToolRegistry) | **WORKING**, well-designed — deterministic + model-backed planners, dependency-ordered executor, policy-gated tool calls, evidence propagation. Its own test suite was stale relative to the current planner output shape (six failures). |
| Model Control (Registry, Router, Adapters) | **WORKING** — capability-driven routing, real Ollama adapter, safe demo/offline fallback, auto-discovery of local models. Its test suite passed outright. |
| Knowledge / RAG (chunker, embeddings, Qdrant store, retriever) | **WORKING**, with one real inefficiency (double query embedding) and a non-hermetic default (defaults to live Ollama embeddings even for "offline" tests). |
| Knowledge / OCR-VLM | **WORKING**, correctly fails (not fakes) when no local Ollama vision model is reachable. |
| Governance — network-deny policy gate + audit log | **WORKING** and is what the executor actually calls. |
| Governance — RBAC/access-request module (`security/`) | **IMPLEMENTED, NOT WIRED** (by design — see README, owner's real implementation not yet merged) but its three demo entry points (`agent.py`, `gateway.py`, `main.py`) were **BROKEN** (unresolvable imports) even standalone. |
| Sandbox (`code.execute`) | **WORKING** — AST-based import/call blocklist, subprocess isolation, timeout. |
| Frontend contract (`app/models/*`, camelCase API fields) | Not modified in this pass — out of scope for a Python services/ audit, and no backend contract break was found against it. Not independently verified (would need the actual `frontend/` build). |
| Test infrastructure (whole repo) | **BROKEN by default** — required either a live Ollama+Qdrant+Postgres, or undocumented manual env vars, to pass; several tests referenced tool IDs/step-counts from an earlier planner architecture; a fixture file referenced by 4+ tests was missing from the supplied zip. |

Before any fix: **10 failed / 27 passed** (`model_control`, `orchestrator`,
`knowledge`), and **3 collection errors, 0 tests run** in `backend`.

---

## B. Bugs Found

### B1. Planner routing ignored auto-discovered real models
- **Bug:** `services/backend/app/api/runs.py::_load()` decided between the
  model-backed planner and the deterministic one by checking
  `os.environ.get("REASONING_MODEL_NAME", "").strip()`.
- **Root cause:** `services/model_control/registry/registry_instance.py`
  auto-discovers local Ollama models via `AUTO_DISCOVER_OLLAMA_MODELS` even
  when `REASONING_MODEL_NAME` is never set. So a real, healthy, already-
  registered reasoning model would still be silently skipped in favor of
  the weaker deterministic planner, contradicting
  `services/orchestrator/README.md`'s documented production path
  ("Task → Model-backed Planner … Production/demo planning uses the
  configured local reasoning model").
- **Affected component:** backend API / orchestrator integration.
- **Why it happened:** the backend layer re-implemented an availability
  check with its own (incomplete) heuristic instead of asking
  `model_control`'s own Router — the single source of truth every other
  model-backed tool in the codebase already uses.
- **Fix applied:** added `_build_plan()`, which calls
  `select_model(model_registry, capability="reasoning", modality="text")`
  and checks `metadata()["runtime"] != "demo-offline"` — i.e. asks the
  Router what it would *actually* select — before choosing model-backed
  planning, with a safe fallback to the deterministic planner if
  model-backed planning itself fails (malformed JSON, invocation error)
  rather than 500ing the task.
- **Validation:** `services/backend/tests/test_planner_routing.py` (new) —
  proves (a) demo-only registry → deterministic plan, (b) a real healthy
  fake model → the model is actually invoked to plan, (c) a real model that
  fails to plan → falls back cleanly. All verified passing.
- **Bug found in my own fix, then corrected:** the first version of
  `_build_plan()` checked availability against `model_registry` but called
  `create_model_backed_plan()` without passing that registry through —
  `create_model_backed_plan`'s default `registry` parameter is bound to
  `model_control`'s own singleton at *def* time, a different object in
  tests. The regression test above caught this immediately (test (b)
  failed: `invoked_with` was empty); fixed by passing `registry=model_registry`
  explicitly.

### B2. `Repository.get_user()` crashed on UUID lookup outside PostgreSQL
- **Bug:** `sqlalchemy.exc.StatementError: 'UUID' object has no attribute
  'replace'` on every user lookup by ID.
- **Root cause:** `users.user_id` is `Uuid(as_uuid=False)` — its Python-side
  representation is `str`, not `uuid.UUID`. `get_user()` parsed the input
  with `UUID(str(value))` and passed that **UUID object** straight to
  `Session.get(User, user_id)`. On PostgreSQL (native UUID column support
  in the dialect) this happens to work; on any dialect without native UUID
  support (SQLite, and potentially other backends), SQLAlchemy's generic
  `Uuid` type's bind processor assumes a string and calls `.replace("-",
  "")` on it directly, crashing on a `UUID` object.
- **Affected component:** `services/backend/app/db/repository.py`.
- **Why it happened:** classic "works against the one database the author
  tested against, breaks elsewhere" — exactly the failure mode this audit
  was asked to hunt for. It was invisible in a Postgres-only dev loop.
- **Fix applied:** `user_id = str(UUID(str(value)))` — validate it's a
  well-formed UUID, then query with the string form that matches the
  column's declared Python-side type everywhere else in the codebase.
- **Validation:** exercised directly by `services/backend/tests/test_health.py`
  (task creation/lookup goes through this path) and the full E2E smoke run
  below — was the single failure blocking every DB-touching backend test
  after the collection/lifespan bugs were fixed.

### B3. `services/backend/__init__.py` was missing
- **Bug:** `pytest services/backend/tests` failed to even *collect* —
  `ImportError: attempted relative import beyond top-level package` on
  `from ..main import app` (see B4) in every test file.
- **Root cause:** every other service (`orchestrator`, `knowledge`,
  `model_control`, `governance`, `sandbox`) has a `services/<name>/__init__.py`
  package marker; `services/backend/__init__.py` did not exist. Python 3's
  implicit namespace packages make direct `services.backend.app.X` imports
  work anyway (which is why the app itself ran fine standalone), but
  pytest's package-boundary detection for *relative* imports stops
  climbing at the first directory lacking `__init__.py` — so
  `services/backend/tests` was treated as a top-level package named `tests`,
  with no parent to resolve `..app.main` against.
- **Affected component:** `services/backend/` package structure.
- **Fix applied:** added the missing (empty) `services/backend/__init__.py`.

### B4. Backend test files imported a module path that no longer exists
- **Bug:** `test_health.py`, `test_api_surface.py`, `test_error_handling.py`
  all did `from ..main import app`.
- **Root cause:** the app was restructured into `services/backend/app/main.py`
  at some point; these three test files were never updated.
- **Fix applied:** `from ..app.main import app` in all three.

### B5. A monkeypatch target that patched a different module than the one actually running
- **Bug:** `test_error_handling.py::test_agent_loop_limit_error_maps_to_documented_error_shape`
  did `import app.api.runs as runs_module` (bare top-level `app`), then
  monkeypatched `runs_module.run_plan`.
- **Root cause:** the running app is loaded via `services.backend.app.api.runs`
  (fully-qualified, per every other import in this codebase). `import
  app.api.runs` creates a **second, disconnected copy** of that module
  under a different name — patching it has no effect on the code path the
  live `TestClient` actually calls.
- **Fix applied:** `import services.backend.app.api.runs as runs_module`.

### B6. `demo_file_path` request field was accepted but silently dropped
- **Bug:** `TaskCreateRequest.demo_file_path` existed on the schema and was
  used by the backend's own test suite, but `create_task()` never read it —
  tasks created this way had no file attached, so the planner never saw a
  `file_path` and OCR/read/summarize branches never triggered.
- **Affected component:** `services/backend/app/api/tasks.py`.
- **Fix applied:** when `demo_file_path` is set, the handler now validates
  the path exists, registers it through the same `repo.save_upload()` path
  a real multipart upload uses (so it gets a `FileRecord`, gets indexed into
  the RAG retriever, and is properly associated with the task), and appends
  the resulting file id to `file_ids`.
- **Validation:** `test_health.py::test_run_multimodal_intent_surfaces_evidence`
  depends on this and now passes; confirmed again in the E2E smoke run.

### B7. Governance demo entry points were unimportable
- **Bug:** `services/governance/{agent,gateway,main}.py` did
  `from security.models import ...` (and similarly for `.policy`, `.rbac`,
  `.tools`, `.network`, `.audit`) — a bare top-level `security` package that
  does not exist anywhere on the Python path used by the rest of this
  codebase.
- **Root cause:** written as if `services/governance` itself were on
  `sys.path` (e.g. run via `cd services/governance && python main.py`),
  inconsistent with the fully-qualified `services.X.Y` convention used
  everywhere else.
- **Fix applied:** `from services.governance.security.X import ...` in all
  three files.
- **Validation:** ran all three directly (`python services/governance/agent.py`
  etc.) — all now execute and print correct ALLOW/DENY decisions. Added
  `services/governance/tests/test_security_module_importable.py` as a
  standing regression check.
- **Note — not a bug, by design:** this `security/` RBAC module is **not**
  wired into the orchestrator's executor. `services/governance/README.md`
  explicitly documents this: the module's real implementation exists with
  a teammate ("Arpit") and is not yet merged; `policy_engine/base.py` +
  `audit/log.py` are the intentional, working, minimal stand-in ("deny any
  tool declaring network access, allow everything else") wired into
  `executor.py` today. I left this as-is rather than force-merging a
  539-line, differently-scoped RBAC model (generic `Tool`/`Permission`
  enums, team/workspace access grants) into the executor without the
  team/workspace context the executor doesn't currently thread through —
  see Section G.

### B8. RAG vector search embedded the query twice
- **Bug:** `VectorStore.search()` called `embed_text(query)` once to size
  `_ensure_collection()` (whose size argument is only ever used the *first*
  time a collection is created — every later call ignores it) and then
  called `embed_text(query)` **again** for the actual search vector.
- **Impact:** doubled embedding latency/cost on every `knowledge.search`
  call, and — when `USE_OLLAMA_EMBEDDINGS=1` (the production default) —
  doubled the number of live network calls to the local Ollama embedding
  endpoint per query.
- **Fix applied:** compute the query embedding once, reuse it for both.
- **Validation:** `services/knowledge/tests/test_rag.py` still passes
  (behavior-preserving); confirmed real retrieval still works correctly in
  the E2E smoke run (relevant chunks retrieved with sane confidence scores).

### B9. Missing test fixture referenced by 4+ tests
- **Bug:** `data/samples/demo/sample_note.txt` is referenced by
  `services/knowledge/tests/test_rag.py`,
  `services/orchestrator/tests/test_executor.py`,
  `services/orchestrator/tests/test_model_backed_tool.py`, and
  `services/backend/tests/test_health.py`, but `data/` was not part of the
  supplied `services.zip` (only `services/` was zipped).
- **Fix applied:** recreated a synthetic, clearly-labeled sample industrial
  inspection note at that exact path (content: corrosion inspection
  findings, SOP references, pressure readings — matching what the tests
  search for). Explicitly marked in the file itself as synthetic test data,
  not a real facility record.

### B10. Test suite was not hermetic by default
- **Bug:** running `pytest` on a machine with no local Ollama/Qdrant
  produced raw connection errors (`httpx.ConnectError: Connection refused`)
  instead of exercising the code under test — `USE_OLLAMA_EMBEDDINGS`
  defaults to `"1"` (real Ollama) despite `embeddings.py`'s own docstring
  saying the hashing fallback is "for unit tests/offline development only",
  and nothing set `AUTO_DISCOVER_OLLAMA_MODELS=0` / `USE_QDRANT_SERVER=0`
  for tests either.
- **Fix applied:** `services/conftest.py` (new) sets
  `USE_OLLAMA_EMBEDDINGS=0`, `USE_QDRANT_SERVER=0`,
  `AUTO_DISCOVER_OLLAMA_MODELS=0` via `os.environ.setdefault(...)` — applies
  to the whole test session, never overrides an explicit value a developer
  sets to intentionally run against real local services.
- **Did NOT change:** the production defaults in `embeddings.py` /
  `registry_instance.py` / `runtime.py` themselves — those correctly default
  to *preferring real services*, which is the right call for production and
  is exactly what this whole audit was asked to protect.

### B11. Backend test suite never triggered the database schema to be created
- **Bug:** every DB-touching backend test failed with `sqlite3.OperationalError:
  no such table: workspaces` (or `tasks`, etc.) even after B2–B5 were fixed.
- **Root cause:** all three test files build `client = TestClient(app)` at
  module level and call it directly. Starlette's `TestClient` only sends
  the ASGI lifespan **startup** event (which is what triggers
  `app/main.py`'s `init_db()` → `Base.metadata.create_all(engine)`) when
  used as a context manager (`with TestClient(app) as client:`) — a bare
  `TestClient(app)` never runs it, so the schema was simply never created.
- **Fix applied:** `services/backend/tests/conftest.py` (new) adds a
  session-scoped, autouse fixture that enters `TestClient(app)` as a context
  manager once for the whole test session. This is sufficient because
  `init_db()` acts on the shared SQLite file behind the module-level engine
  singleton — every other bare `TestClient(app)` instance created inside
  individual test files can use the resulting schema even though its own
  lifespan was never entered.
- **Also in this file:** overrides `DATABASE_URL` to a throwaway file-based
  SQLite database (see Section G for what this does and doesn't verify).

### B12–B17. Stale tests from an earlier planner architecture
Six tests in `services/orchestrator/tests/` and two in
`services/knowledge/tests/test_rag.py` asserted step-counts, tool IDs, or
step indices from a planner architecture that predates two real
improvements already present in `create_plan()`:
1. File-backed "summarize" and "visual document" plans now always finish
   with a real `model.reason` answer step (per the explicit requirement:
   "the plan should not terminate prematurely after simple summarization…
   finish with a final reasoning/answer step") — so these plans are 3 steps,
   not 2.
2. The deterministic planner emits the *real* production tool ids
   (`text.summarize_model`, `model.reason`) directly — not the older
   `text.summarize_naive` demo placeholder.

Each was individually diagnosed (not just assertion-patched) and fixed to
match current, correct planner behavior — full detail in the diff
(`pramaan_fixes.diff`). One (`test_ingest_and_retrieve_relevant_chunk`) was
a simple return-type mismatch: `VectorStore.add_chunks()` returns the list
of point ids it wrote, not a count — the test asserted `== 3` where
`len(...) == 3` was meant. One
(`test_multimodal_loop_populates_evidence`) had a plain missing import
(`SummarizeTextModelTool` used but never imported — `NameError`).

---

## C. Architecture Map (as verified, not aspirational)

```
User
 ↓
POST /api/v1/tasks  (FastAPI, services/backend/app/api/tasks.py)
 ↓                    — creates Task + TaskRun rows (Postgres/SQLite via SQLAlchemy)
 ↓                    — demo_file_path / file_ids → FileRecord + RAG ingestion
POST /api/v1/tasks/{id}/run
 ↓
_build_plan()  →  Model Router asks: is a real (non-demo) reasoning model
 │                 healthy? → services/model_control/router/router.py
 ├─ yes → create_model_backed_plan()  (real local LLM plans, JSON-validated,
 │         tool ids checked against PLANNER_SAFE_TOOLS before the executor
 │         ever sees them)
 └─ no  → create_plan()  (deterministic, keyword-routed, same tool ids)
 ↓
run_plan()  (services/orchestrator/state_graph/executor.py)
 │  for each ready step, in dependency order:
 ├── PolicyEngine.check()  → deny any tool with declares_network_access=True
 │                            (services/governance/policy_engine/base.py)
 ├── AuditLog.record()     → every allow/deny decision recorded
 ├── ToolRegistry.get(tool_id).invoke(inputs)
 │     file.read            → services/orchestrator/tools/examples.py
 │     ocr.process           → services/knowledge/ocr_vlm (real Ollama VLM)
 │     knowledge.search       → services/knowledge/rag (real chunk→embed→
 │                              Qdrant/in-memory→cosine search→evidence)
 │     text.summarize_model,
 │     model.reason,
 │     code.generate_model    → services/model_control Router → real Ollama
 │                              adapter, or DemoModelAdapter fallback
 │     code.execute           → services/sandbox (AST-blocklisted subprocess)
 ├── evidence[] populated from each tool's "evidence" output (real claim +
 │   source + confidence + validation_state, never fabricated)
 ├── data-flow: this step's output injected into dependent steps' inputs
 │   as upstream_<step_id>
 └── on requires_approval=true → pauses (approval_status="pending"),
     state persisted, resumes via POST /tasks/{id}/approve
 ↓
final_output = { response (from the last model.reason/summary output),
                  tool_outputs[], evidence[], model_calls[], approval_status }
 ↓
persist_state_artifacts()  → TaskStep / ToolCall / ModelCall / Evidence rows
 ↓
generate_approval_note()  → real python-docx deliverable, persisted as a
                              FileRecord + Deliverable row, downloadable via
                              GET /api/v1/files/{id}/download
```

---

## D. Files Changed

| Path | Change |
|---|---|
| `services/backend/app/api/runs.py` | Added `_build_plan()`: route to model-backed vs. deterministic planner via the Model Router instead of a raw env var; graceful fallback on planning failure. |
| `services/backend/app/api/tasks.py` | Wire `demo_file_path` into task creation (was silently ignored); index it into the RAG retriever. |
| `services/backend/app/db/repository.py` | `get_user()`: fix UUID-object-vs-string bug in `Session.get()` lookup. |
| `services/backend/__init__.py` | **New.** Missing package marker, present in every other service. |
| `services/backend/README.md` | Fixed the documented run command (dual-import-path hazard: `app.main:app --app-dir services/backend` vs. every internal import using `services.backend.app.*`). |
| `services/backend/tests/conftest.py` | **New.** Throwaway SQLite `DATABASE_URL` + session-scoped lifespan fixture so the suite doesn't need a live Postgres and the DB schema actually gets created. |
| `services/backend/tests/test_planner_routing.py` | **New.** Regression test for the B1 fix. |
| `services/backend/tests/test_health.py` | Fixed import path (B4); fixed stale `ocr.process_naive` tool-id assertion → `ocr.process` with the VLM adapter mocked for offline testing; fixed stale `completed_steps == 2` → `1`. |
| `services/backend/tests/test_api_surface.py` | Fixed import path (B4). |
| `services/backend/tests/test_error_handling.py` | Fixed import path (B4); fixed disconnected-module monkeypatch target (B5). |
| `services/governance/agent.py`, `gateway.py`, `main.py` | Fixed unresolvable `security.X` imports → `services.governance.security.X`. |
| `services/governance/tests/test_security_module_importable.py` | **New.** Regression test for the above. |
| `services/knowledge/rag/store.py` | `VectorStore.search()`: compute the query embedding once instead of twice. |
| `services/knowledge/tests/test_rag.py` | Fixed `add_chunks()` return-type assertion (list of ids, not a count). |
| `services/orchestrator/tests/test_agent_state.py` | Fixed stale step-count assertion for the current 3-step file+summarize plan. |
| `services/orchestrator/tests/test_executor.py` | Fixed stale step-counts/tool-ids across 5 tests (see B12–B17); added missing import. |
| `services/orchestrator/tests/test_model_backed_tool.py` | Registered the now-required `model.reason` tool (plan grew from 2 to 3 steps). |
| `services/conftest.py` | **New.** Repo-wide hermetic test defaults (offline embeddings/vector-store/model-discovery). |
| `data/samples/demo/sample_note.txt` | **New.** Missing fixture, recreated (synthetic content). |

Full line-by-line diff: `pramaan_fixes.diff` (attached).

---

## E. Integration Status

| Component | Status | Notes |
|---|---|---|
| Backend API surface | ✅ | All documented routes reachable, JSON-compatible, verified via `TestClient` + a manual E2E run (below). |
| Database (SQLAlchemy models, repository) | ✅ (SQLite-verified) / ⚠️ (Postgres not exercised here) | Schema creates cleanly, full CRUD path exercised. UUID-type bug (B2) fixed — was masked by Postgres's native UUID handling in the original dev loop. |
| Model Router / Registry | ✅ | Capability-driven selection, health-check ordering, demo fallback all verified via existing + new tests. |
| Ollama integration | ⚠️ Not verified live | No Ollama server reachable in this sandbox. Adapter code correct (real HTTP calls, real error propagation on failure — confirmed via a real `ConnectionRefused` in the E2E run, not a fake success). |
| Qdrant integration | ⚠️ Not verified live | Same constraint. In-memory fallback verified real (real cosine search, real evidence). |
| Planner (deterministic + model-backed) | ✅ | Both paths exercised; routing bug (B1) fixed and regression-tested. |
| Executor | ✅ | Dependency ordering, policy gating, retries, approval-pause/resume, evidence population, final-output selection all exercised live. |
| Tool Registry | ✅ | All 8 production tool ids verified registered and reachable; `code.execute` verified to actually run code and actually block a disallowed import. |
| Evidence / Provenance | ✅ | Verified real (not fabricated) — evidence claims in the E2E run are literal chunks from the uploaded file with real cosine-similarity confidence scores. |
| Governance — network policy gate | ✅ | Verified: `network.fetch_demo` denied, audited, never invoked. |
| Governance — RBAC module | ⚪ Implemented, not wired (by design, see B7) | Demo entry points fixed and now run correctly standalone. |
| Deliverables (docx generation) | ✅ | Verified: real `.docx` generated via python-docx, persisted, downloadable — confirmed non-empty valid Office XML content-type and byte count. |
| Frontend contract | ⚪ Not independently re-verified | No backend contract break found; frontend build/run itself was out of scope for this pass. |

---

## F. E2E Flow — What Was Actually Run

This is a real, captured run through the live FastAPI app (`TestClient`
against SQLite + in-memory vector store + `DemoModelAdapter`, no mocking of
orchestrator/executor/policy/RAG logic itself):

1. **Health check** → `200 {"status": "ok", ...}`
2. **Upload** `sample_note.txt` via `POST /files/upload` → real file
   persisted, real RAG ingestion (chunked, embedded, indexed).
3. **Create + run** a task ("search the knowledge base for the SOP pressure
   limit") → plan: `knowledge.search → model.reason` → **status: completed,
   errors: []**. Evidence returned contains the *actual* matching sentences
   from the uploaded file ("Pipeline pressure must not exceed 150 psi under
   the safety SOP…") with real similarity confidence scores (~0.46), not
   placeholders.
4. **Create + run** a task with `demo_file_path` pointing at the same file,
   intent "review this scanned p&id drawing" → plan routes through
   `ocr.process` → **status: failed**, error `TOOL_EXECUTION_ERROR:
   Ollama VLM (gemma3:4b) failed: Connection refused`. This is the *correct*
   behavior in this sandbox: no live vision model is reachable, and the
   system fails honestly rather than fabricating OCR output.
5. **Create + run** a task ("prepare an approval note…") → pauses at
   **awaiting_approval** → `POST /approve` → **status: completed**, 1
   completed step, and a real `.docx` deliverable generated.
6. **Deliverables list** → the generated approval note is present, approved,
   with a real download URL.
7. **Download** the deliverable → `200`, content-type
   `application/vnd.openxmlformats-officedocument.wordprocessingml.document`,
   37KB, a genuine valid Word document.
8. **Network sovereignty test** ("test network access") → plan routes to
   `network.fetch_demo` → **status: failed**, error `PERMISSION_DENIED:
   Network access is denied by the default sovereignty policy`, and the
   tool's `invoke()` — which would raise if it were ever actually reached —
   never ran.
9. **Overview/sovereignty endpoint** → correctly reflects 1 blocked
   network event, 100% local processing.
10. **Audit trail** → real, timestamped, correctly attributed entries for
    every decision above.

---

## G. Remaining Limitations

**Required for genuine production functioning (not yet done — outside what
was safely achievable without live services in this sandbox):**
- **Real Postgres integration was not exercised.** Only SQLite was verified.
  The schema and repository code are dialect-generic SQLAlchemy and the
  UUID bug that *would* have broken this (B2) is now fixed, but true
  Postgres-specific behavior (NUMERIC precision on `vram_required_gb`,
  concurrent-session semantics, actual `psycopg` driver behavior) has not
  been run against a real Postgres instance. **Action:** run
  `pytest services/backend/tests` with `DATABASE_URL` pointed at a real
  `docker compose up` Postgres before considering this fully closed.
- **Real Ollama integration was not exercised.** The adapter code is
  correct and fails cleanly without a server (verified), but no actual
  model inference, real planning JSON output, real OCR/vision output, or
  real embeddings were ever produced by an actual model in this session.
  **Action:** run the same E2E flow with `ollama serve` + the models named
  in `.env.example` actually pulled, and confirm `create_model_backed_plan()`
  produces a valid plan from real model output (this codebase already
  handles malformed JSON from a real model via `PlannerError`, but that
  path itself was only exercised with a scripted fake model here).
- **Real Qdrant integration was not exercised.** In-memory fallback is
  verified real (genuine cosine search over genuine embeddings), but the
  actual `QdrantClient` HTTP path (`collection_exists`, `upsert`,
  `query_points`) against a live server was not run.

**Recommended for production (not required for the system to function):**
- The `services/governance/security/*` RBAC module (team/workspace-scoped
  access control) is real but unwired, by explicit design documented in
  `services/governance/README.md`. When that teammate's implementation is
  ready to merge, it should replace `PolicyEngine`/`default_policy_engine`
  behind the same `.check()` interface — `executor.py` does not need to
  change (this was designed correctly for exactly this kind of swap).
- `services/backend/db/database.py`'s `@app.on_event("startup")` is
  deprecated by FastAPI/Starlette in favor of lifespan context managers
  (shows a `DeprecationWarning` on every test run) — not broken, but worth
  migrating before it's actually removed upstream.
- No automated tests exist yet for `services/sandbox/` or
  `services/governance/security/` beyond the one new regression test added
  here — I verified `code.execute` manually (real execution + real import
  blocking), but did not write a full test module for it, to keep this
  pass focused on fixing what was broken rather than expanding scope
  further.
- `Repository.progress()` computes task progress from `TaskStep` rows, but
  `persist_state_artifacts()` never sets `output_ref` on those rows (always
  `None`) — harmless today (nothing reads it) but worth closing if the
  frontend ever wants per-step output in the progress view.

**Future enhancements (explicitly out of scope):**
- Multimodal spreadsheet engine (`services/knowledge/spreadsheet_engine/`)
  is an empty stub — consistent with docs describing it as future work, not
  a bug.
- PaddleOCR adapter (`paddle_adapter.py`) is implemented but explicitly
  documented as blocked on model-weight download in an offline sandbox —
  not touched, matches its own status note.

---

## H. Test Results

**Before this pass:**
- `services/model_control`, `services/orchestrator`, `services/knowledge`:
  **10 failed, 27 passed**
- `services/backend`: **3 collection errors, 0 tests run**

**After this pass (verified — full suite, this session):**

```
$ pytest services/ -q
49 passed  (initial full pass, before the 3 new regression tests below)
...
$ pytest services/ -q   (final, with all new tests added)
52 passed in 3.02s
```

Breakdown:
- `services/model_control` — all passing (no changes needed; was already
  correct and hermetic).
- `services/orchestrator` — all passing (6 stale-test fixes).
- `services/knowledge` — all passing (2 fixes: hermetic env + return-type
  assertion).
- `services/governance` — all passing (1 new regression test).
- `services/backend` — all passing (10 tests: the original 6 + fixed
  imports/lifespan/UUID bug, + 3 new planner-routing regression tests +
  1 new `__init__.py`).
- `services/sandbox` — no automated tests exist; manually verified
  (real code execution, real import blocking — see Section E).

Plus the manual E2E run described in Section F, which is not part of the
automated suite but was executed live in this session against the real
FastAPI app.

---

## I. How to Run

**1. Install dependencies** (from repo root, with `data/` and the fixed
`services/` in place):
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r services/backend/requirements.txt \
            -r services/orchestrator/requirements.txt \
            -r services/knowledge/requirements.txt \
            -r services/model_control/requirements.txt \
            -r services/governance/requirements.txt \
            -r services/sandbox/requirements.txt
```

**2. Start dependencies** (for full production verification — optional for
just running the test suite, which is now hermetic by default):
```bash
docker compose up -d postgres qdrant ollama   # if docker-compose.yml is present
ollama pull qwen3:4b && ollama pull gemma3:4b && ollama pull nomic-embed-text
```

**3. Run the test suite** (works with or without step 2, thanks to
`services/conftest.py` / `services/backend/tests/conftest.py`):
```bash
PYTHONPATH=. pytest services/ -q
```
To instead force real integration testing against live services from step
2, override the hermetic defaults:
```bash
PYTHONPATH=. USE_OLLAMA_EMBEDDINGS=1 USE_QDRANT_SERVER=1 \
  AUTO_DISCOVER_OLLAMA_MODELS=1 DATABASE_URL=postgresql+psycopg://pramaan:changeme@localhost:5433/pramaan \
  pytest services/ -q
```

**4. Start the backend:**
```bash
PYTHONPATH=. uvicorn services.backend.app.main:app --reload --port 8000
```

**5. Run an actual PRAMAAN task** (against the running server):
```bash
curl -s -X POST localhost:8000/api/v1/files/upload \
  -F "file=@data/samples/demo/sample_note.txt"
# → note the returned "id"

curl -s -X POST localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"intent":"search the knowledge base for the SOP pressure limit","file_ids":["<id from above>"]}'
# → note the returned "task_id"

curl -s -X POST localhost:8000/api/v1/tasks/<task_id>/run
```

**6. Verify final output:** the `/run` response's `final_output.response`
field should contain a real model-generated (or, without Ollama pulled,
demo-adapter-extractive) answer, `evidence[]` should contain real retrieved
chunks with `source` pointing at the uploaded file, and `status` should be
`"completed"`.

**7. Troubleshooting:**
- `status: "failed"` with `ModelUnavailableError` / `Connection refused` on
  an OCR or reasoning step → no Ollama server reachable at
  `MODEL_RUNTIME_HOST:MODEL_RUNTIME_PORT` (default `localhost:11434`) with
  the named model actually pulled. This is expected, honest behavior, not a
  bug — see Section G.
- `no such table` errors → `DATABASE_URL` points somewhere `init_db()`
  never ran against (e.g. a fresh Postgres with the app started via a path
  that skips the FastAPI startup event) — use the fully-qualified uvicorn
  invocation in step 4, which does trigger it correctly (this only affected
  the test client, per B11, not a real ASGI server run).
- `knowledge.search` returns no evidence → confirm the file was actually
  ingested (`POST /files/upload` response, or check for exceptions
  swallowed by the `try/except` in `files.py`'s upload handler — currently
  silent by design for unsupported file types, but worth checking manually
  if a specific file unexpectedly indexes nothing).
