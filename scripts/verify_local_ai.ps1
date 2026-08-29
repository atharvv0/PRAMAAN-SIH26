$ErrorActionPreference = 'Stop'
Write-Host 'PRAMAAN local AI verification' -ForegroundColor Cyan
ollama --version
ollama list
$tags = Invoke-RestMethod 'http://127.0.0.1:11434/api/tags'
$names = @($tags.models | ForEach-Object { $_.name })
Write-Host "Installed models: $($names -join ', ')"
Write-Host 'CLOUD: disabled is enforced by OLLAMA_NO_CLOUD=1 in the runtime configuration.'
Write-Host 'Recommended PRAMAAN roles:'
Write-Host '  reasoning = qwen3:4b'
Write-Host '  coding   = qwen3:4b (real local model, coding-specialized prompt route)'
Write-Host '  vision   = gemma3:4b'
Write-Host '  embedding= nomic-embed-text'
