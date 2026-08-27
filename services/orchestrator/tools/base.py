"""
ToolAdapter — see docs/agent-contract.md "ToolAdapter".

This is the interface every tool must implement to be callable by the agent. Concrete
tools (document reader, spreadsheet engine, OCR, code sandbox, etc.) are implemented by
their owning service (services/knowledge, services/sandbox, ...) and registered here.
Agents call tools ONLY through this interface, and only after a Policy Engine check —
never Agent -> Tool directly. See docs/architecture.md "Core Principle".
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class ToolAdapter(ABC):
    id: str
    required_permissions: list[str] = []
    declares_network_access: bool = False

    @abstractmethod
    def invoke(self, inputs: dict) -> dict:
        """Execute the tool and return a JSON-serializable result."""
        raise NotImplementedError


class ToolRegistry:
    """In-memory registry. Tools register themselves here; the planner/executor looks
    them up by id. Does not perform permission checks itself — that's the Policy
    Engine's job (services/governance/policy_engine)."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolAdapter] = {}

    def register(self, tool: ToolAdapter) -> None:
        if tool.id in self._tools:
            raise ValueError(f"tool '{tool.id}' already registered")
        self._tools[tool.id] = tool

    def get(self, tool_id: str) -> ToolAdapter:
        if tool_id not in self._tools:
            raise KeyError(f"tool '{tool_id}' not registered")
        return self._tools[tool_id]

    def list_ids(self) -> list[str]:
        return list(self._tools.keys())
