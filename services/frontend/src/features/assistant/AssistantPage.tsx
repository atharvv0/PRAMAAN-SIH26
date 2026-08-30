import { useState } from 'react'
import { Bot, Send, ShieldCheck, Sparkles } from 'lucide-react'
import { PageHeader, SectionLabel } from '@/components/common/States'
import { Button } from '@/components/ui/Button'
import { Textarea } from '@/components/ui/Field'
import { api } from '@/api/client'
import { useAuthStore } from '@/store'

export function AssistantPage() {
  const user = useAuthStore((s) => s.user)
  const [message, setMessage] = useState('')
  const [answer, setAnswer] = useState('')
  const [model, setModel] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function send() {
    if (!message.trim() || busy) return
    setBusy(true); setError('')
    try {
      const result = await api.chatAssistant(message.trim())
      setAnswer(result.response)
      setModel(result.modelId)
      setMessage('')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Assistant request failed.')
    } finally { setBusy(false) }
  }

  return <div className="space-y-4">
    <PageHeader eyebrow="Local intelligence" title="AI Assistant" description="Private workbench assistant powered by the local model stack. Hidden reasoning is never displayed." />
    <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_320px]">
      <section className="border border-border bg-panel">
        <SectionLabel>Conversation</SectionLabel>
        <div className="min-h-[360px] p-4">
          {!answer ? <div className="grid min-h-[300px] place-items-center text-center"><div><div className="mx-auto grid size-12 place-items-center border border-accent/30 bg-accent-soft"><Bot className="size-6 text-accent" /></div><h3 className="mt-3 text-[14px] font-semibold">How can I help?</h3><p className="mt-1 max-w-md text-[11px] leading-relaxed text-text-muted">Ask about a task, document workflow, evidence, models, or how to use the PRAMAAN workbench.</p></div></div> : <div><div className="border border-border bg-surface p-3 text-[12px] leading-6 text-text">{answer}</div><div className="mt-2 text-[10px] text-text-muted">Generated locally by {model || 'local model'}.</div></div>}
        </div>
        <div className="border-t border-border p-3">
          <Textarea value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Ask PRAMAAN Assistant…" rows={4} />
          {error ? <div className="mt-2 text-[11px] text-danger">{error}</div> : null}
          <div className="mt-2 flex items-center justify-between gap-2"><span className="text-[10px] text-text-muted"><Sparkles className="mr-1 inline size-3" />Local-only response path</span><Button type="button" variant="primary" disabled={!message.trim() || busy} onClick={() => void send()} rightIcon={<Send className="size-3.5" />}>{busy ? 'Thinking…' : 'Send'}</Button></div>
        </div>
      </section>
      <aside className="border border-border bg-panel">
        <SectionLabel>Assistant policy</SectionLabel>
        <div className="space-y-3 p-4 text-[11px] leading-relaxed text-text-secondary">
          <div className="flex items-start gap-2"><ShieldCheck className="mt-0.5 size-4 shrink-0 text-accent" /><span>Role: <strong className="text-text">{user?.role ?? 'operator'}</strong></span></div>
          <p>The assistant uses the local Model Router and does not intentionally expose hidden chain-of-thought or internal tool prompts.</p>
          <p>Task-specific facts should be supplied through the task/run context; the assistant will not fabricate missing information.</p>
        </div>
      </aside>
    </div>
  </div>
}
