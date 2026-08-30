"""Artifact writer for user-requested deliverables."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from uuid import uuid4

from services.orchestrator.tools.base import ToolAdapter

OUTPUT_ROOT = (
    Path(__file__).resolve().parents[4] / "data" / "outputs"
)


def _filename_stem(task_id: str, requested: str | None) -> str:
    if requested:
        stem = Path(requested).stem.strip()
    else:
        stem = f"pramaan_{task_id[:8]}"
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("._-")
    return stem or f"pramaan_{task_id[:8]}"


def _text_from_upstream(inputs: dict) -> str:
    # Preferred source is explicit.
    preferred = inputs.get("content")
    if isinstance(preferred, str) and preferred.strip():
        return preferred.strip()

    content_from = inputs.get("content_from")
    if isinstance(content_from, str):
        value = inputs.get(f"upstream_{content_from}")
        if isinstance(value, dict):
            for key in ("summary", "content", "answer", "text"):
                if isinstance(value.get(key), str) and value[key].strip():
                    return value[key].strip()

    # Otherwise choose the last useful upstream model/tool output.
    candidates: list[str] = []
    for key, value in inputs.items():
        if not str(key).startswith("upstream_") or not isinstance(value, dict):
            continue
        for field in ("summary", "content", "answer", "text"):
            item = value.get(field)
            if isinstance(item, str) and item.strip():
                candidates.append(item.strip())
                break

    if candidates:
        return candidates[-1]

    raise ValueError("artifact.write found no upstream content to write")


def _normalize_lines(text: str, line_count: int | None) -> str:
    clean = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    if not line_count or line_count <= 0:
        return clean

    lines = clean.splitlines() if clean else []
    if len(lines) > line_count:
        lines = lines[:line_count]
    while len(lines) < line_count:
        lines.append("")
    # For text deliverables, pad with empty strings only if source was shorter.
    return "\n".join(lines)


class ArtifactWriteTool(ToolAdapter):
    id = "artifact.write"
    required_permissions: list[str] = []
    declares_network_access = False

    def invoke(self, inputs: dict) -> dict:
        task_id = str(inputs.get("task_id") or uuid4())
        fmt = str(inputs.get("format") or "txt").lower().lstrip(".")
        if fmt not in {"txt", "md", "json", "csv", "docx"}:
            raise ValueError(f"Unsupported artifact format: {fmt}")

        text = _text_from_upstream(inputs)
        if fmt in {"txt", "md"}:
            text = _normalize_lines(text, inputs.get("line_count"))

        OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
        name = _filename_stem(task_id, inputs.get("filename"))
        path = OUTPUT_ROOT / f"{name}.{fmt}"

        if fmt in {"txt", "md"}:
            path.write_text(text + "\n", encoding="utf-8")
            mime = "text/plain" if fmt == "txt" else "text/markdown"

        elif fmt == "json":
            path.write_text(
                json.dumps(
                    {"task_id": task_id, "content": text},
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            mime = "application/json"

        elif fmt == "csv":
            rows = [[line] for line in text.splitlines() if line.strip()]
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["content"])
                writer.writerows(rows)
            mime = "text/csv"

        else:
            from docx import Document

            doc = Document()
            for line in text.splitlines() or [text]:
                doc.add_paragraph(line)
            doc.save(path)
            mime = (
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            )

        return {
            "artifact": {
                "path": str(path),
                "filename": path.name,
                "format": fmt,
                "mime_type": mime,
                "size_bytes": path.stat().st_size,
            }
        }
