# PRAMAAN — Ollama setup

## Current development model

The current development profile uses `qwen3:4b` as the reasoning/planning model. It is suitable for the local RTX 3050 4 GB development workstation.

## Windows local runtime

1. Install Ollama.
2. Set `OLLAMA_MODELS` to a model directory on a data drive if required.
3. Set `OLLAMA_NO_CLOUD=1`.
4. Pull the model:

```powershell
ollama pull qwen3:4b
```

5. Start the local server:

```powershell
ollama serve
```

6. In the PRAMAAN `.env`, set:

```env
MODEL_RUNTIME=ollama
MODEL_RUNTIME_HOST=localhost
MODEL_RUNTIME_PORT=11434
REASONING_MODEL_NAME=qwen3:4b
```

The application uses the ModelAdapter boundary, so adding another open-weight model later does not require changing the orchestrator.

## Air-gapped verification

Model weights must be downloaded before an air-gapped run. After all required weights are present, disconnect the workstation/server from the Internet and verify that a real PRAMAAN task still completes. `OLLAMA_NO_CLOUD=1` disables Ollama cloud functionality; the remaining network boundary is enforced by PRAMAAN's own policy layer.

## Model-backed planning

When `REASONING_MODEL_NAME` is configured, the task run path calls the model-backed planner. The planner requests JSON schema output, disables visible thinking output, validates the response, and rejects unsupported tools before execution.

## Docker note (Windows)
If the backend runs inside Docker while Ollama runs on Windows host, configure the backend's `MODEL_RUNTIME_HOST` as `host.docker.internal` and make the Ollama listener reachable from Docker (for example `OLLAMA_HOST=0.0.0.0:11434`). Keep Docker/host networking limited to the local machine/network. PRAMAAN still uses the local Ollama runtime and `OLLAMA_NO_CLOUD=1`; no cloud inference is required.
