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
        suffix = p.suffix.lower()
        if suffix==".pdf":
            try:
                import fitz
                doc=fitz.open(path); contents=[]; evidence=[]
                requested_max = inputs.get("max_pages")
                max_pages = len(doc) if requested_max in (None, "", 0) else min(len(doc), int(requested_max))
                for page_no in range(max_pages):
                    page=doc[page_no]
                    pix=page.get_pixmap(matrix=fitz.Matrix(1.4,1.4),alpha=False)
                    image_path=Path(path).with_name(f"{p.stem}__page_{page_no+1}.png")
                    pix.save(str(image_path))
                    try:
                        result=self._adapter.invoke(str(image_path), prompt="Read this scanned industrial document page. Extract all visible text, labels, measurements, dates, findings, tables, and other observable information. Do not invent missing content.")
                        text=result.get("content",""); contents.append(f"[Page {page_no+1}]\n{text}")
                        for e in result.get("evidence",[]):
                            e["page_or_region"]=f"page_{page_no+1}"; e["source"]=path; evidence.append(e)
                    finally:
                        try:image_path.unlink()
                        except OSError:pass
                return {"content":"\n\n".join(contents),"path":path,"model_id":self._adapter.id,"evidence":evidence}
            except ImportError as exc:
                raise RuntimeError("PyMuPDF is required for PDF vision processing") from exc

        if suffix == ".pptx":
            try:
                from pptx import Presentation
                import tempfile
                prs = Presentation(path)
                contents=[]; evidence=[]
                for slide_no, slide in enumerate(prs.slides, 1):
                    slide_text=[]
                    for shape in slide.shapes:
                        if getattr(shape, "has_text_frame", False):
                            text=shape.text.strip()
                            if text: slide_text.append(text)
                        if getattr(shape, "shape_type", None) == 13:  # picture
                            blob = shape.image.blob
                            suffix2 = Path(shape.image.filename).suffix or ".png"
                            with tempfile.NamedTemporaryFile(suffix=suffix2, delete=False) as fh:
                                fh.write(blob); temp_path=fh.name
                            try:
                                result=self._adapter.invoke(temp_path, prompt="Analyze this embedded presentation image/diagram. Extract visible labels, values, annotations and relevant visual findings. Do not invent content.")
                                visual=result.get("content", "")
                                if visual: slide_text.append("[Embedded image analysis]\n" + visual)
                                for e in result.get("evidence", []):
                                    e["page_or_region"]=f"slide_{slide_no}"; e["source"]=path; evidence.append(e)
                            finally:
                                try: Path(temp_path).unlink()
                                except OSError: pass
                    contents.append(f"[Slide {slide_no}]\n" + "\n".join(slide_text))
                return {"content":"\n\n".join(contents),"path":path,"model_id":self._adapter.id,"evidence":evidence}
            except ImportError as exc:
                raise RuntimeError("python-pptx is required for PPTX vision processing") from exc

        return self._adapter.invoke(path, prompt="Read this industrial image carefully. Extract visible text, labels, measurements and relevant visual observations. Do not invent facts.")
