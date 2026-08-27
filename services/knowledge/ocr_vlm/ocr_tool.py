"""
OcrProcessTool — real ToolAdapter wrapping PaddleOcrAdapter. id: ocr.process
(the REAL tool id — distinct from services/orchestrator/tools/examples.py's
ocr.process_naive demo placeholder, which the planner still uses by default —
see planner.py TODO for how to switch over once this is verified working on
real hardware).
"""
from __future__ import annotations

from services.knowledge.ocr_vlm.paddle_adapter import PaddleOcrAdapter
from services.orchestrator.tools.base import ToolAdapter


class OcrProcessTool(ToolAdapter):
    id = "ocr.process"
    required_permissions = ["file.read"]
    declares_network_access = False

    def __init__(self) -> None:
        self._adapter = PaddleOcrAdapter()

    def invoke(self, inputs: dict) -> dict:
        path = inputs.get("path")
        if not path:
            raise ValueError("OcrProcessTool requires 'path' in inputs")
        return self._adapter.invoke(path)
