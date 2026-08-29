from __future__ import annotations

import os
from pathlib import Path

from services.knowledge.ocr_vlm.ollama_vlm_adapter import OllamaVlmAdapter
from services.orchestrator.tools.base import ToolAdapter


class OcrProcessTool(ToolAdapter):
    id="ocr.process"
    required_permissions=["file.read"]
    declares_network_access=False

    def __init__(self):
        self._adapter=OllamaVlmAdapter(model=os.environ.get("VISION_MODEL_NAME") or os.environ.get("OCR_MODEL_NAME"))

    def invoke(self, inputs: dict) -> dict:
        path=inputs.get("path")
        if not path: raise ValueError("OcrProcessTool requires path")
        p=Path(path)
        if p.suffix.lower()==".pdf":
            try:
                import fitz
                doc=fitz.open(path); contents=[]; evidence=[]
                max_pages=min(len(doc), int(inputs.get("max_pages",5)))
                for page_no in range(max_pages):
                    page=doc[page_no]
                    pix=page.get_pixmap(matrix=fitz.Matrix(1.4,1.4),alpha=False)
                    image_path=Path(path).with_name(f"{p.stem}__page_{page_no+1}.png")
                    pix.save(str(image_path))
                    try:
                        result=self._adapter.invoke(str(image_path), prompt="Read this scanned industrial document page. Extract all visible text, labels, measurements, dates, findings, and other observable information. Do not invent missing content.")
                        text=result.get("content",""); contents.append(f"[Page {page_no+1}]\n{text}")
                        for e in result.get("evidence",[]):
                            e["page_or_region"]=f"page_{page_no+1}"; e["source"]=path; evidence.append(e)
                    finally:
                        try:image_path.unlink()
                        except OSError:pass
                return {"content":"\n\n".join(contents),"path":path,"model_id":self._adapter.id,"evidence":evidence}
            except ImportError as exc:
                raise RuntimeError("PyMuPDF is required for PDF vision processing") from exc
        return self._adapter.invoke(path, prompt="Read this industrial image carefully. Extract visible text and describe relevant engineering observations. Do not invent facts.")
