# PRAMAAN E2E final hardening

This revision hardens document understanding, evidence, artifacts, and downloads.

## Supported runtime paths
- text files: native extraction -> model reasoning
- PDF: native extraction; scanned/visual pages -> Gemma VLM/OCR
- images: Gemma VLM/OCR
- PPTX: slide text + embedded-image VLM/OCR
- DOCX: paragraphs/tables
- XLSX/XLSM: worksheet cell extraction
- CSV/JSON/Markdown/TXT: native text extraction

## Artifacts
`artifact.write` supports txt, md, json, csv, docx, pdf, pptx, xlsx. Artifact outputs are persisted into the DB as FileRecord + Deliverable and downloaded through an authenticated blob request so custom auth headers work.

## Evidence
OCR/VLM and RAG results are converted to EvidenceRecord. Qdrant searches can be filtered by user/workspace metadata to avoid cross-user retrieval leakage.
