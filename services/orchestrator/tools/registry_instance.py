"""
The shared ToolRegistry instance backend/app wires up at startup.

Phase 4+: real tools from services/knowledge, services/sandbox, etc. get imported
and registered here alongside (or instead of) the demo tools, once those modules
exist. Backend should only ever import `default_registry` from this module — never
construct its own ToolRegistry.

text.summarize_model (tools/model_backed.py) closes the Phase 5 TODO on
SummarizeTextTool: it's a real call through services/model_control now that the
Model Router exists, rather than a demo placeholder. It's registered here
alongside — not instead of — text.summarize_naive: the planner (planner/planner.py)
still selects the naive tool by default for demo determinism (no dependency on an
Ollama runtime being up during rehearsal — see docs/roadmap.md "Demo fragility"
risk), but text.summarize_model is available for any plan/capability wiring that
wants a real model call, and callers can register a plan step with
tool="text.summarize_model" today.
"""
from __future__ import annotations

from services.orchestrator.tools.base import ToolRegistry
from services.orchestrator.tools.examples import (
    OcrProcessNaiveTool,
    ReadFileTool,
    SummarizeTextTool,
)
from services.orchestrator.tools.model_backed import SummarizeTextModelTool

default_registry = ToolRegistry()
default_registry.register(ReadFileTool())
default_registry.register(SummarizeTextTool())
default_registry.register(OcrProcessNaiveTool())
default_registry.register(SummarizeTextModelTool())
