import { useMemo, useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { FilePlus2, Loader2, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Field, Input, Select, Textarea } from '@/components/ui/Field'
import { StatusBadge } from '@/components/ui/StatusBadge'
import {
  ErrorState,
  LoadingState,
  PageHeader,
  SectionLabel,
} from '@/components/common/States'
import { useCreateTask, useWorkspaces } from '@/hooks'
import { useAuthStore, useWorkbenchStore } from '@/store'
import type { TaskFile, TaskFileType } from '@/types/task'
import { cn, formatBytes } from '@/lib/utils'

const EXAMPLE_INSTRUCTION =
  'Review the confidential MRPL turnaround inspection package for CDU-101. Extract findings from the scanned inspection report, cross-reference annotated P&ID regions against SOP-MRPL-INSP-042, reconcile thickness / corrosion readings in the measurement workbook, and draft an Approval Note for the Inspection Authority. All processing must remain on-prem; deny external model or network calls.'

type DemoPreset = {
  name: string
  type: TaskFileType
  sizeBytes: number
  label: string
}

const DEMO_PRESETS: DemoPreset[] = [
  {
    label: 'PDF',
    name: 'CDU101_Inspection_Report_Scan.pdf',
    type: 'pdf',
    sizeBytes: 4_820_441,
  },
  {
    label: 'P&ID',
    name: 'P&ID_CDU101_Annotated.png',
    type: 'image',
    sizeBytes: 2_140_880,
  },
  {
    label: 'XLSX',
    name: 'Thickness_Corrosion_Readings.xlsx',
    type: 'spreadsheet',
    sizeBytes: 186_432,
  },
  {
    label: 'SOP',
    name: 'SOP-MRPL-INSP-042_Visual_Inspection.docx',
    type: 'document',
    sizeBytes: 412_096,
  },
]

export function TaskCreatePage() {
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const { workspaceId, setWorkspace } = useWorkbenchStore()
  const { data: workspaces, isLoading: wsLoading, isError: wsError, refetch } =
    useWorkspaces()
  const createTask = useCreateTask()

  const [title, setTitle] = useState('Inspection Package Review')
  const [instruction, setInstruction] = useState('')
  const [selectedWs, setSelectedWs] = useState(workspaceId)
  const [files, setFiles] = useState<TaskFile[]>([])
  const [dragOver, setDragOver] = useState(false)

  const canSubmit = useMemo(
    () =>
      title.trim().length > 0 &&
      instruction.trim().length > 0 &&
      selectedWs.length > 0 &&
      !createTask.isPending,
    [title, instruction, selectedWs, createTask.isPending],
  )

  function addDemoFile(preset: DemoPreset) {
    setFiles((prev) => {
      if (prev.some((f) => f.name === preset.name)) return prev
      return [
        ...prev,
        {
          id: `file-${Date.now()}-${preset.type}`,
          name: preset.name,
          type: preset.type,
          sizeBytes: preset.sizeBytes,
          status: 'pending',
          localProcessing: true,
        },
      ]
    })
  }

  function removeFile(id: string) {
    setFiles((prev) => prev.filter((f) => f.id !== id))
  }

  function onDropFiles(fileList: FileList | null) {
    if (!fileList) return
    const next: TaskFile[] = []
    for (const file of Array.from(fileList)) {
      const type = inferType(file.name)
      next.push({
        id: `file-${Date.now()}-${file.name}`,
        name: file.name,
        type,
        sizeBytes: file.size,
        status: 'pending',
        localProcessing: true,
      })
    }
    setFiles((prev) => [...prev, ...next])
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!canSubmit) return

    const ws = workspaces?.find((w) => w.id === selectedWs)
    if (ws) setWorkspace(ws.id, ws.name)

    try {
      const task = await createTask.mutateAsync({
        title: title.trim(),
        instruction: instruction.trim(),
        workspaceId: selectedWs,
        createdBy: user?.id ?? 'demo.operator@local',
        files: files.map((f) => ({ ...f, status: 'queued' as const })),
      })
      if (task.runId) {
        navigate(`/runs/${task.runId}`)
      } else {
        navigate('/tasks')
      }
    } catch {
      // mutation error surfaced below
    }
  }

  if (wsLoading) return <LoadingState label="Loading workspaces…" />
  if (wsError || !workspaces) {
    return (
      <ErrorState
        title="Workspaces unavailable"
        onRetry={() => void refetch()}
      />
    )
  }

  return (
    <div className="space-y-3">
      <PageHeader
        eyebrow="Work package"
        title="Create task"
        description="Industrial intake — inputs, intent, and execution context for local agent processing."
      />

      <div className="border border-border bg-panel px-3 py-2 flex flex-wrap gap-x-6 gap-y-1 text-[11px] text-text-muted">
        <span>
          Flow:{' '}
          <span className="text-text-secondary font-medium">Inputs → Intent → Execution</span>
        </span>
        <span className="font-mono">Egress deny-by-default</span>
        <span className="font-mono">Local models only</span>
      </div>

      <form onSubmit={(e) => void handleSubmit(e)} className="space-y-3">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-3 border border-border bg-panel lg:divide-x divide-border">
          {/* INPUTS */}
          <section className="flex flex-col min-h-[360px] border-b lg:border-b-0 border-border">
            <SectionLabel>01 · Inputs</SectionLabel>
            <div className="p-3 flex flex-col gap-3 flex-1">
              <div
                onDragOver={(e) => {
                  e.preventDefault()
                  setDragOver(true)
                }}
                onDragLeave={() => setDragOver(false)}
                onDrop={(e) => {
                  e.preventDefault()
                  setDragOver(false)
                  onDropFiles(e.dataTransfer.files)
                }}
                className={cn(
                  'border border-dashed px-3 py-6 text-center transition-colors',
                  dragOver
                    ? 'border-accent bg-accent-soft'
                    : 'border-border bg-canvas',
                )}
              >
                <FilePlus2 className="size-5 text-text-muted mx-auto mb-2" />
                <p className="text-[12px] text-text-secondary">
                  Drop documents here (demo accepts any file metadata)
                </p>
                <label className="mt-2 inline-block">
                  <input
                    type="file"
                    multiple
                    className="sr-only"
                    onChange={(e) => onDropFiles(e.target.files)}
                  />
                  <span className="text-[11px] text-accent cursor-pointer hover:underline">
                    Browse files
                  </span>
                </label>
              </div>

              <div>
                <div className="text-micro text-text-muted mb-1.5">Demo attachments</div>
                <div className="flex flex-wrap gap-1.5">
                  {DEMO_PRESETS.map((p) => (
                    <Button
                      key={p.label}
                      type="button"
                      size="sm"
                      onClick={() => addDemoFile(p)}
                    >
                      + {p.label}
                    </Button>
                  ))}
                </div>
              </div>

              <div className="border border-border flex-1 overflow-auto">
                {files.length === 0 ? (
                  <p className="text-[11px] text-text-muted px-3 py-4">
                    No files attached. Local processing only.
                  </p>
                ) : (
                  <ul className="divide-y divide-border">
                    {files.map((f) => (
                      <li
                        key={f.id}
                        className="px-2.5 py-2 flex items-start gap-2 text-[12px]"
                      >
                        <div className="min-w-0 flex-1">
                          <div className="text-text font-medium truncate">{f.name}</div>
                          <div className="flex flex-wrap items-center gap-2 mt-1 text-[10px] text-text-muted">
                            <span className="uppercase">{f.type}</span>
                            <span className="font-mono">{formatBytes(f.sizeBytes)}</span>
                            <StatusBadge status={f.status} compact />
                            {f.localProcessing ? (
                              <span className="text-success">Local processing</span>
                            ) : null}
                          </div>
                        </div>
                        <button
                          type="button"
                          onClick={() => removeFile(f.id)}
                          className="text-text-muted hover:text-danger p-1"
                          aria-label={`Remove ${f.name}`}
                        >
                          <Trash2 className="size-3.5" />
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          </section>

          {/* INTENT */}
          <section className="flex flex-col min-h-[360px] border-b lg:border-b-0 border-border">
            <SectionLabel>02 · Intent</SectionLabel>
            <div className="p-3 flex flex-col gap-3 flex-1">
              <Field label="Task title">
                <Input
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Inspection Package Review"
                  required
                />
              </Field>
              <Field
                label="Instruction"
                hint="Describe extraction, cross-check, and deliverable expectations."
                className="flex-1"
              >
                <Textarea
                  value={instruction}
                  onChange={(e) => setInstruction(e.target.value)}
                  className="min-h-[200px] flex-1"
                  placeholder="Operator instruction for the local agent…"
                  required
                />
              </Field>
              <Button
                type="button"
                size="sm"
                onClick={() => setInstruction(EXAMPLE_INSTRUCTION)}
              >
                Prefill example instruction
              </Button>
            </div>
          </section>

          {/* EXECUTION CONTEXT */}
          <section className="flex flex-col min-h-[360px]">
            <SectionLabel>03 · Execution</SectionLabel>
            <div className="p-3 flex flex-col gap-3 flex-1">
              <Field label="Workspace" hint="All processing stays within sovereign boundary.">
                <Select
                  value={selectedWs}
                  onChange={(e) => setSelectedWs(e.target.value)}
                >
                  {workspaces.map((w) => (
                    <option key={w.id} value={w.id}>
                      {w.name}
                    </option>
                  ))}
                </Select>
              </Field>

              <div className="border border-border bg-canvas px-3 py-2 text-[12px] space-y-1.5">
                <div className="text-micro text-text-muted">Policy posture</div>
                <div className="text-text-secondary">Egress: deny-by-default</div>
                <div className="text-text-secondary">Models: local / deterministic only</div>
                <div className="text-text-secondary">Audit: recording on submit</div>
                <div className="text-text-secondary">
                  Operator: {user?.name ?? 'Unsigned'} ({user?.role ?? '—'})
                </div>
              </div>

              <div className="mt-auto space-y-2">
                {createTask.isError ? (
                  <p className="text-[11px] text-danger">
                    Failed to create task. Retry or check local API.
                  </p>
                ) : null}
                <Button
                  type="submit"
                  variant="primary"
                  className="w-full"
                  disabled={!canSubmit}
                  leftIcon={
                    createTask.isPending ? (
                      <Loader2 className="size-3.5 animate-spin" />
                    ) : undefined
                  }
                >
                  {createTask.isPending ? 'Queuing…' : 'Submit & open run'}
                </Button>
              </div>
            </div>
          </section>
        </div>
      </form>
    </div>
  )
}

function inferType(name: string): TaskFileType {
  const lower = name.toLowerCase()
  if (lower.endsWith('.pdf')) return 'pdf'
  if (/\.(png|jpe?g|webp|gif)$/.test(lower)) return 'image'
  if (/\.(xlsx|xls|csv)$/.test(lower)) return 'spreadsheet'
  if (/\.(docx?|txt|md)$/.test(lower)) return 'document'
  return 'other'
}
