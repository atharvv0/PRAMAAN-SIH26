import { useEffect, useMemo, useRef, useState, type DragEvent, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { FilePlus2, FileText, Image, Play, Paperclip, Trash2, UploadCloud } from 'lucide-react'
import { api, ApiError } from '@/api'
import { Button } from '@/components/ui/Button'
import { Field, Input, Select, Textarea } from '@/components/ui/Field'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { ErrorState, LoadingState, PageHeader, SectionLabel } from '@/components/common/States'
import { useCreateTask, useRunTask, useWorkspaces } from '@/hooks'
import { useAuthStore, useWorkbenchStore } from '@/store'
import type { TaskFile, TaskFileType } from '@/types/task'
import { cn, formatBytes } from '@/lib/utils'

interface LocalFile {
  id: string
  file: File
  state: 'pending' | 'uploading' | 'uploaded' | 'failed'
  stored?: TaskFile
  error?: string
}

const ACCEPT = '.pdf,.png,.jpg,.jpeg,.webp,.gif,.svg,.xlsx,.xls,.csv,.doc,.docx,.txt,.md'
const MAX_FILE_BYTES = 100 * 1024 * 1024

function makeFileId(file: File) {
  const unique = typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function' ? crypto.randomUUID() : `${Date.now()}-${Math.random().toString(36).slice(2)}`
  return `${file.name}-${file.size}-${file.lastModified}-${unique}`
}

function inferType(name: string): TaskFileType {
  const lower = name.toLowerCase()
  if (lower.endsWith('.pdf')) return 'pdf'
  if (/\.(png|jpe?g|webp|gif|svg)$/.test(lower)) return 'image'
  if (/\.(xlsx|xls|csv)$/.test(lower)) return 'spreadsheet'
  if (/\.(docx?|txt|md)$/.test(lower)) return 'document'
  return 'other'
}

export function TaskCreatePage() {
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const { workspaceId, setWorkspace } = useWorkbenchStore()
  const workspaces = useWorkspaces()
  const create = useCreateTask()
  const run = useRunTask()
  const inputRef = useRef<HTMLInputElement>(null)
  const [title, setTitle] = useState('')
  const [instruction, setInstruction] = useState('')
  const [selectedWs, setSelectedWs] = useState(workspaceId)
  const [sensitivity, setSensitivity] = useState<'internal' | 'confidential' | 'restricted'>('confidential')
  const [files, setFiles] = useState<LocalFile[]>([])
  const [dragOver, setDragOver] = useState(false)
  const [fileError, setFileError] = useState('')
  const [submitError, setSubmitError] = useState('')

  useEffect(() => {
    if (!selectedWs && workspaceId) setSelectedWs(workspaceId)
  }, [selectedWs, workspaceId])

  useEffect(() => {
    if (!selectedWs) return
    const workspace = workspaces.data?.find((item) => item.id === selectedWs)
    if (workspace) setWorkspace(workspace.id, workspace.name)
  }, [selectedWs, workspaces.data, setWorkspace])

  const canSubmit = useMemo(() => {
    const hasUsableFile = files.some((entry) => entry.state === 'pending' || entry.state === 'uploaded')
    const uploading = files.some((entry) => entry.state === 'uploading')
    return title.trim().length >= 3 && instruction.trim().length >= 10 && Boolean(selectedWs) && hasUsableFile && !uploading && !create.isPending && !run.isPending
  }, [title, instruction, selectedWs, files, create.isPending, run.isPending])

  function addFiles(list: FileList | null) {
    if (!list) return
    setFileError('')
    const incoming: LocalFile[] = []
    for (const file of Array.from(list)) {
      if (file.size <= 0) continue
      if (file.size > MAX_FILE_BYTES) {
        setFileError(`${file.name} exceeds the 100 MB browser upload limit.`)
        continue
      }
      const duplicate = files.some((entry) => entry.file.name === file.name && entry.file.size === file.size && entry.file.lastModified === file.lastModified)
      if (!duplicate) incoming.push({ id: makeFileId(file), file, state: 'pending' })
    }
    if (incoming.length) setFiles((current) => [...current, ...incoming])
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault()
    setDragOver(false)
    addFiles(event.dataTransfer.files)
  }

  function removeFile(id: string) {
    setFiles((current) => current.filter((item) => item.id !== id))
  }

  async function submit(event: FormEvent) {
    event.preventDefault()
    setSubmitError('')
    if (!canSubmit) {
      if (!files.length) setSubmitError('Attach at least one source file before creating the task.')
      return
    }

    const createdBy = user?.email || user?.id || 'local-session'
    const uploadedIds: string[] = []
    const next = [...files]

    try {
      for (let index = 0; index < next.length; index += 1) {
        const entry = next[index]
        if (!entry) continue
        if (entry.state === 'uploaded' && entry.stored?.id) {
          uploadedIds.push(entry.stored.id)
          continue
        }
        if (entry.state !== 'pending') continue

        next[index] = { ...entry, state: 'uploading', error: undefined }
        setFiles([...next])
        try {
          const stored = await api.uploadFile(entry.file, selectedWs, createdBy)
          const normalized = { ...stored, type: inferType(stored.name) }
          next[index] = { ...entry, state: 'uploaded', stored: normalized }
          uploadedIds.push(normalized.id)
          setFiles([...next])
        } catch (error) {
          const message = error instanceof ApiError ? error.message : error instanceof Error ? error.message : 'Upload failed.'
          next[index] = { ...entry, state: 'failed', error: message }
          setFiles([...next])
          throw error
        }
      }

      if (!uploadedIds.length) throw new Error('No source files were accepted by the local API.')

      const task = await create.mutateAsync({
        title: title.trim(),
        instruction: instruction.trim(),
        workspaceId: selectedWs,
        createdBy,
        sensitivity,
        file_ids: uploadedIds,
      })

      // Task creation and execution are separate backend operations. Start the
      // authoritative run explicitly instead of assuming POST /tasks auto-runs.
      const startedRun = await run.mutateAsync(task.id)
      navigate(`/runs/${startedRun.id}`)
    } catch (error) {
      const message = error instanceof ApiError ? `${error.message}${error.status ? ` (HTTP ${error.status})` : ''}` : error instanceof Error ? error.message : 'The local API rejected the operation.'
      setSubmitError(message)
    }
  }

  if (workspaces.isLoading) return <LoadingState label="Loading workspace context…" />
  if (workspaces.isError || !workspaces.data) return <ErrorState title="Workspace context unavailable" description="A task cannot be created until the local API returns available workspaces." onRetry={() => void workspaces.refetch()} />

  return (
    <div className="space-y-4">
      <PageHeader eyebrow="Work package" title="Create task" description="Define the workload, attach source material, then start an explicit local agent run." actions={<Link to="/tasks" className="inline-flex h-8 items-center border border-border bg-raised px-3 text-[11px] font-medium text-text hover:bg-hover">Cancel</Link>} />

      <form onSubmit={(event) => void submit(event)} className="grid gap-4 lg:grid-cols-[1.15fr_.85fr]">
        <section className="border border-border bg-panel">
          <SectionLabel>Task definition</SectionLabel>
          <div className="space-y-4 p-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="Title"><Input autoFocus value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Turnaround inspection review" aria-invalid={title.length > 0 && title.trim().length < 3} /></Field>
              <Field label="Sensitivity"><Select value={sensitivity} onChange={(e) => setSensitivity(e.target.value as typeof sensitivity)}><option value="internal">Internal</option><option value="confidential">Confidential</option><option value="restricted">Restricted</option></Select></Field>
            </div>
            <Field label="Intent / instruction" hint="State the outcome, source context, constraints, and review expectations."><Textarea value={instruction} onChange={(e) => setInstruction(e.target.value)} placeholder="Describe what the local agent should analyze, reconcile, draft, or verify…" /></Field>
            {submitError ? <ErrorState className="m-0" title="Task operation failed" description={submitError} /> : null}
            <div className="flex flex-wrap items-center justify-between gap-3 border-t border-border pt-3">
              <div className="text-[11px] text-text-muted">Execution remains under the backend sovereignty policy.</div>
              <Button type="submit" variant="primary" size="lg" disabled={!canSubmit} leftIcon={<Play className="size-4" />}>{run.isPending ? 'Starting…' : create.isPending ? 'Creating…' : 'Create & start task'}</Button>
            </div>
          </div>
        </section>

        <section className="border border-border bg-panel">
          <SectionLabel>Source files</SectionLabel>
          <div className="p-4">
            <div role="button" tabIndex={0} onClick={() => inputRef.current?.click()} onKeyDown={(event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); inputRef.current?.click() } }} onDragOver={(event) => { event.preventDefault(); setDragOver(true) }} onDragLeave={() => setDragOver(false)} onDrop={handleDrop} className={cn('flex min-h-[210px] cursor-pointer flex-col items-center justify-center rounded-sm border border-dashed px-4 text-center transition-colors', dragOver ? 'border-accent bg-accent-soft' : 'border-border bg-canvas hover:border-border-strong hover:bg-raised')}>
              <UploadCloud className="size-8 text-accent" aria-hidden />
              <div className="mt-3 text-[13px] font-semibold text-text">Drag & drop source files here</div>
              <div className="mt-1 max-w-sm text-[11px] leading-relaxed text-text-muted">or choose files from this device. Files are uploaded only to the configured PRAMAAN API.</div>
              <span className="mt-4 inline-flex h-8 items-center gap-2 border border-accent/50 bg-accent-soft px-3 text-[11px] font-semibold text-accent"><FilePlus2 className="size-3.5" aria-hidden />Browse files</span>
              <input ref={inputRef} type="file" multiple accept={ACCEPT} className="sr-only" onChange={(event) => { addFiles(event.target.files); event.currentTarget.value = '' }} />
            </div>
            <div className="mt-2 text-[10px] text-text-muted">PDF, images, spreadsheets, Word and text · maximum 100 MB per file</div>
            {fileError ? <div className="mt-3 border border-danger/35 bg-danger-soft px-3 py-2 text-[10.5px] text-danger" role="alert">{fileError}</div> : null}

            <div className="mt-3 space-y-2">
              {files.length === 0 ? <div className="border border-border bg-surface px-3 py-3 text-[11px] text-text-muted">No files attached.</div> : files.map((entry) => <div key={entry.id} className="flex items-center gap-3 border border-border bg-surface px-3 py-2.5"><FileIcon type={inferType(entry.file.name)} /><div className="min-w-0 flex-1"><div className="truncate text-[12px] font-medium text-text">{entry.file.name}</div><div className="mt-0.5 flex flex-wrap items-center gap-2 text-[10px] text-text-muted"><span>{formatBytes(entry.file.size)}</span>{entry.state === 'uploaded' && entry.stored ? <StatusBadge status={entry.stored.status} compact showIcon={false} /> : <span>{entry.state}</span>}</div>{entry.error ? <div className="mt-1 text-[10px] text-danger">{entry.error}</div> : null}</div>{entry.state !== 'uploading' ? <button type="button" className="grid size-7 shrink-0 place-items-center text-text-muted hover:bg-raised hover:text-danger" onClick={() => removeFile(entry.id)} aria-label={`Remove ${entry.file.name}`}><Trash2 className="size-3.5" aria-hidden /></button> : null}</div>)}
            </div>
            <div className="mt-4 border-t border-border pt-3 text-[10.5px] leading-relaxed text-text-muted">The backend remains authoritative for content acceptance, storage, sovereignty policy, model routing, evidence, and audit.</div>
          </div>
        </section>
      </form>
    </div>
  )
}

function FileIcon({ type }: { type: TaskFileType }) {
  return type === 'image' ? <Image className="size-4 text-accent" aria-hidden /> : type === 'pdf' || type === 'document' ? <FileText className="size-4 text-accent" aria-hidden /> : <Paperclip className="size-4 text-accent" aria-hidden />
}
