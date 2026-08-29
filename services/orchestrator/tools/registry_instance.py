from __future__ import annotations

from services.knowledge.ocr_vlm.ocr_tool import OcrProcessTool
from services.knowledge.rag.runtime import get_retriever
from services.knowledge.rag.tool import KnowledgeSearchTool
from services.orchestrator.tools.base import ToolRegistry
from services.orchestrator.tools.examples import NetworkFetchDemoTool, ReadFileTool
from services.orchestrator.tools.model_backed import CodingModelTool, ReasoningModelTool, SummarizeTextModelTool
from services.sandbox.code_tool import CodeExecuteTool


def build_tool_registry() -> ToolRegistry:
    registry=ToolRegistry()
    registry.register(ReadFileTool())
    registry.register(NetworkFetchDemoTool())
    registry.register(SummarizeTextModelTool())
    registry.register(ReasoningModelTool())
    registry.register(CodingModelTool())
    registry.register(CodeExecuteTool())
    registry.register(OcrProcessTool())
    registry.register(KnowledgeSearchTool(get_retriever()))
    return registry


default_registry=build_tool_registry()
