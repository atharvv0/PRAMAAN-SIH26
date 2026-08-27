"""
PaddleOcrAdapter — real ModelAdapter (docs/agent-contract.md) wrapping PaddleOCR-VL
per the dossier's tech choice (docs/architecture.md Technology Decision Snapshot).

STATUS: implemented and installs cleanly (`pip install paddleocr paddlepaddle`),
but model weight download failed in the sandbox this was built in — no network
route to PaddleOCR's model hosting (see docs/developer-setup.md network notes).
The exact failure, captured live:

    Exception: No available model hosting platforms detected.
    Please check your network connection.

**Verify this on a machine with real internet access before demo day** — run
`python -c "from services.knowledge.ocr_vlm.paddle_adapter import PaddleOcrAdapter;
print(PaddleOcrAdapter().health_check())"` from repo root. If it returns False,
check your network, or pre-download the PaddleOCR model cache ahead of the offline
demo (PaddleOCR caches to disk after the first successful run — the sovereign/
air-gapped deployment should ship with that cache pre-populated, not download at
demo time).

On any failure, this adapter raises ModelUnavailableError (retryable, per
docs/agent-contract.md) instead of crashing the executor.
"""
from __future__ import annotations

from services.orchestrator.errors import ModelUnavailableError

_ocr_instance = None


def _get_ocr():
    global _ocr_instance
    if _ocr_instance is None:
        from paddleocr import PaddleOCR

        _ocr_instance = PaddleOCR(use_textline_orientation=False, lang="en")
    return _ocr_instance


class PaddleOcrAdapter:
    id = "paddleocr_vl"
    capabilities = ["ocr", "document_analysis"]

    def invoke(self, image_path: str) -> dict:
        try:
            ocr = _get_ocr()
            result = ocr.ocr(image_path)
        except Exception as exc:  # noqa: BLE001 — any load/inference failure -> typed error
            raise ModelUnavailableError(
                f"PaddleOCR could not process '{image_path}': {exc}", detail=repr(exc)
            ) from exc

        lines: list[str] = []
        evidence: list[dict] = []
        for page in result or []:
            for entry in page or []:
                text, confidence = entry[1]
                lines.append(text)
                evidence.append(
                    {
                        "claim": text,
                        "source": image_path,
                        "page_or_region": None,
                        "confidence": float(confidence),
                        "validation_state": "unverified",
                    }
                )
        return {"content": "\n".join(lines), "path": image_path, "evidence": evidence}

    def health_check(self) -> bool:
        try:
            _get_ocr()
            return True
        except Exception:
            return False

    def metadata(self) -> dict:
        return {"id": self.id, "capabilities": self.capabilities}
