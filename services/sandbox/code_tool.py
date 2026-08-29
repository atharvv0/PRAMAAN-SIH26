from __future__ import annotations

import ast
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from services.orchestrator.tools.base import ToolAdapter


_BLOCKED_IMPORTS={"socket","requests","httpx","urllib","ftplib","paramiko","subprocess","shutil","ctypes"}
_BLOCKED_CALLS={"os.system","os.popen","subprocess.run","subprocess.Popen","subprocess.call"}


def _validate_code(code: str) -> None:
    tree=ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                if n.name.split(".")[0] in _BLOCKED_IMPORTS: raise ValueError(f"Sandbox rejected import: {n.name}")
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] in _BLOCKED_IMPORTS: raise ValueError(f"Sandbox rejected import: {node.module}")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                fq=f"{node.func.value.id}.{node.func.attr}"
                if fq in _BLOCKED_CALLS: raise ValueError(f"Sandbox rejected call: {fq}")


class CodeGenerateTool(ToolAdapter):
    id="code.generate"
    required_permissions=[]
    declares_network_access=False

    def __init__(self, model_tool): self._model_tool=model_tool
    def invoke(self, inputs: dict)->dict:
        prompt=inputs.get("prompt") or inputs.get("intent")
        if not prompt: raise ValueError("code.generate requires prompt")
        result=self._model_tool.generate_code(prompt)
        return result


class CodeExecuteTool(ToolAdapter):
    id="code.execute"
    required_permissions=["sandbox.execute"]
    declares_network_access=False

    def invoke(self, inputs: dict)->dict:
        code=inputs.get("code")
        if not code:
            for v in inputs.values():
                if isinstance(v,dict) and v.get("code"):
                    code=v["code"]; break
        if not code: raise ValueError("code.execute requires code")
        _validate_code(code)
        timeout=int(os.environ.get("SANDBOX_TIMEOUT_SECONDS","20"))
        with tempfile.TemporaryDirectory(prefix="pramaan-sandbox-") as td:
            path=Path(td)/"main.py"; path.write_text(code,encoding="utf-8")
            env={"PYTHONIOENCODING":"utf-8","PATH":os.environ.get("PATH","")}
            proc=subprocess.run([sys.executable,"-I",str(path)],cwd=td,capture_output=True,text=True,timeout=timeout,env=env)
            return {"code":code,"stdout":proc.stdout,"stderr":proc.stderr,"returncode":proc.returncode,"status":"passed" if proc.returncode==0 else "failed"}
