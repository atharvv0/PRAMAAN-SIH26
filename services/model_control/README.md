# PRAMAAN Model Control

Model Control separates model selection from the rest of the system.

## Runtime

The current local runtime is Ollama. Add models through environment configuration rather than hard-coding model names into the router.

Recommended local roles for the SIH MVP:

- Reasoning/planning: `qwen3:4b`
- Coding: `qwen3:4b` through the coding capability route (replace with a stronger local coding model on a larger GPU without changing the interface)
- Vision/OCR: `gemma3:4b`
- Embeddings: `nomic-embed-text`

## Selection flow

`Task → required capability/modality → ModelRegistry → health check → selected local adapter`

The router must remain capability-driven. Adding a new model should only require registration/configuration, not new model-name branches in the router.

## Sovereignty

Ollama is expected to run locally with `OLLAMA_NO_CLOUD=1`. The PRAMAAN application does not call OpenAI, Anthropic, Google, or other hosted AI APIs.


## PRAMAAN SIH MVP auto-discovery

When no role environment variables are set, the registry auto-discovers local
Ollama models. For the standard SIH MVP local set:
- `qwen3:4b` is preferred for `reasoning`, `summarize_text`, and `coding`.
- `gemma3:4b` is preferred for `vision`, `ocr`, and `document_analysis`.
- embedding models such as `nomic-embed-text` are intentionally excluded from
  generation routing and remain owned by the Knowledge/RAG embedding subsystem.

Vision/OCR adapters advertise both `text` and `image` modalities and forward
`images` to Ollama's `/api/generate` endpoint when supplied.
