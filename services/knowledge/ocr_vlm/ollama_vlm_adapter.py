from __future__ import annotations

import base64
import os
import time
from pathlib import Path

import httpx

from services.orchestrator.errors import ModelUnavailableError


class OllamaVlmAdapter:
    capabilities = ["vision", "document_analysis", "ocr"]

    def __init__(self, model: str | None = None, host: str | None = None, port: int | None = None):
        self._model = model or os.environ.get("VISION_MODEL_NAME") or os.environ.get("OCR_MODEL_NAME") or "gemma3:4b"
        self._host = host or os.environ.get("MODEL_RUNTIME_HOST", "localhost")
        self._port = port or int(os.environ.get("MODEL_RUNTIME_PORT", "11434"))
        self.id=f"ollama-vlm:{self._model}"
        self.base_url=f"http://{self._host}:{self._port}"

    def invoke(self, image_path: str, prompt: str = "Extract the visible information accurately. Describe only what is supported by the image.") -> dict:
        try:
            image_b64=base64.b64encode(Path(image_path).read_bytes()).decode("utf-8")
            start=time.monotonic()
            resp=httpx.post(f"{self.base_url}/api/generate",json={"model":self._model,"prompt":prompt,"images":[image_b64],"stream":False,"think":False,"options":{"temperature":0}},timeout=180.0)
            resp.raise_for_status(); data=resp.json()
        except Exception as exc:
            raise ModelUnavailableError(f"Ollama VLM ({self._model}) failed: {exc}",detail=repr(exc)) from exc
        text=str(data.get("response","")).strip()
        return {"content":text,"path":image_path,"model_id":self.id,"latency_ms":int((time.monotonic()-start)*1000),"evidence":[{"claim":text,"source":image_path,"page_or_region":None,"model":self.id,"confidence":None,"validation_state":"unverified"}]}

    def health_check(self)->bool:
        try:
            r=httpx.get(f"{self.base_url}/api/tags",timeout=3.0); r.raise_for_status()
            return any((m.get("name") or "")==self._model for m in r.json().get("models",[]))
        except Exception:return False

    def metadata(self)->dict:
        return {"id":self.id,"model_name":self._model,"capabilities":self.capabilities,"modalities":["image"],"runtime":"ollama","local":True}
