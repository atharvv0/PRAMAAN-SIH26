import { Check, LogOut } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Field, Select } from '@/components/ui/Field'
import { MetaRow, PageHeader, SectionLabel } from '@/components/common/States'
import { HealthIndicator } from '@/components/common/Indicators'
import { useAuthStore, useWorkbenchStore, type ThemeMode } from '@/store'
import { api } from '@/api'
import { useHealth } from '@/hooks'
import { useNavigate } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'

export function SettingsPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const user = useAuthStore((s) => s.user)
  const signOut = useAuthStore((s) => s.signOut)
  const { workspaceId, workspaceName, theme, setTheme } = useWorkbenchStore()
  const health = useHealth()

  return <div className="space-y-4">
    <PageHeader eyebrow="Configuration" title="Settings" description="Local identity, workspace context, and appearance. Server-side authorization remains authoritative when provided by the deployment." actions={<Button size="sm" variant="danger" onClick={() => { signOut(); queryClient.clear(); navigate('/login', { replace: true }) }} leftIcon={<LogOut className="size-3.5" />}>Sign out</Button>} />

    <section className="border border-border bg-panel"><SectionLabel>Session</SectionLabel><dl className="px-4 py-2"><MetaRow label="User ID" value={user?.id ?? '—'} mono /><MetaRow label="Operator" value={user?.name ?? '—'} /><MetaRow label="Role" value={user?.role ?? '—'} /><MetaRow label="Organization" value={user?.org ?? '—'} /><MetaRow label="Email" value={user?.email ?? '—'} /><MetaRow label="Session" value="Browser-local session" /></dl></section>

    <section className="border border-border bg-panel"><SectionLabel>Workbench</SectionLabel><div className="grid gap-4 p-4 md:grid-cols-2"><Field label="Appearance" hint="Applied immediately in this browser."><Select value={theme} onChange={(e) => setTheme(e.target.value as ThemeMode)}><option value="dark">Dark</option><option value="light">Light</option><option value="system">System</option></Select></Field><div className="border border-border bg-surface px-3 py-3"><div className="text-micro text-text-muted">Active workspace</div><div className="mt-1 text-[13px] font-medium text-text">{workspaceName}</div><div className="mt-1 font-mono text-[10px] text-text-muted">{workspaceId || 'Not selected'}</div></div></div></section>

    <section className="border border-border bg-panel"><SectionLabel>Local API</SectionLabel><dl className="px-4 py-2"><MetaRow label="Base URL" value={import.meta.env.VITE_API_BASE_URL || '/api/v1'} mono /><MetaRow label="Mode" value={api.mode.toUpperCase()} /><MetaRow label="Health" value={<HealthIndicator />} /><MetaRow label="Connection" value={health.isError ? 'Unavailable' : health.isLoading ? 'Checking…' : 'Reachable'} /></dl><div className="border-t border-border bg-surface px-4 py-3 text-[11px] text-text-muted">API state is read-only here. Server configuration belongs to the deployment environment.</div></section>

    <div className="flex items-center gap-2 text-[10.5px] text-success"><Check className="size-3.5" aria-hidden />No synthetic dataset or external AI provider is enabled by this frontend.</div>
  </div>
}
