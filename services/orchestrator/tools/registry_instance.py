"""
The shared ToolRegistry instance backend/app wires up at startup.

Phase 4+: real tools from services/knowledge, services/sandbox, etc. get imported
and registered here alongside (or instead of) the demo tools, once those modules
exist. Backend should only ever import `default_registry` from this module — never
construct its own ToolRegistry.
"""
from __future__ import annotations

from services.orchestrator.tools.base import ToolRegistry
from services.orchestrator.tools.examples import (
    OcrProcessNaiveTool,
    ReadFileTool,
    SummarizeTextTool,
)

default_registry = ToolRegistry()
default_registry.register(ReadFileTool())
default_registry.register(SummarizeTextTool())
default_registry.register(OcrProcessNaiveTool())
