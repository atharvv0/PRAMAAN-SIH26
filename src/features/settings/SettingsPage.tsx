import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import {
  MetaRow,
  PageHeader,
  SectionLabel,
} from '@/components/common/States'
import { SovereigntyIndicator } from '@/components/common/Indicators'
import { api } from '@/api'
import { useAuthStore, useWorkbenchStore } from '@/store'
import { cn } from '@/lib/utils'

export function SettingsPage() {
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const signOut = useAuthStore((s) => s.signOut)
  const { demoMode, setDemoMode, workspaceName, workspaceId } = useWorkbenchStore()

  function handleSignOut() {
    signOut()
    navigate('/login')
  }

  return (
    <div className="space-y-3 max-w-2xl">
      <PageHeader
        eyebrow="System"
        title="Settings"
        description="Demo controls and session status for the local workbench."
      />

      <section className="border border-border bg-panel">
        <SectionLabel>Session</SectionLabel>
        <dl className="px-3 py-2">
          <MetaRow label="Operator" value={user?.name ?? 'Unsigned'} />
          <MetaRow label="Role" value={user?.role ?? '—'} />
          <MetaRow label="Org" value={user?.org ?? '—'} />
          <MetaRow label="Workspace" value={workspaceName} />
          <MetaRow label="Workspace ID" value={workspaceId} mono />
        </dl>
        <div className="px-3 pb-3">
          <Button variant="danger" size="sm" onClick={handleSignOut}>
            Sign out
          </Button>
        </div>
      </section>

      <section className="border border-border bg-panel">
        <SectionLabel>Demo mode</SectionLabel>
        <div className="px-3 py-3 flex items-center justify-between gap-4">
          <div>
            <div className="text-[13px] text-text font-medium">Use demo dataset</div>
            <p className="text-[11px] text-text-muted mt-0.5 leading-relaxed">
              When enabled, the UI is backed by the local mock adapter and SIH demo
              inspection package.
            </p>
          </div>
          <button
            type="button"
            role="switch"
            aria-checked={demoMode}
            onClick={() => setDemoMode(!demoMode)}
            className={cn(
              'relative h-7 w-12 shrink-0 border transition-colors',
              demoMode
                ? 'bg-accent-soft border-accent/50'
                : 'bg-raised border-border',
            )}
          >
            <span
              className={cn(
                'absolute top-0.5 size-5 bg-text transition-[left]',
                demoMode ? 'left-[22px] bg-accent' : 'left-0.5',
              )}
            />
          </button>
        </div>
      </section>

      <section className="border border-border bg-panel">
        <SectionLabel>API & system status</SectionLabel>
        <dl className="px-3 py-2">
          <MetaRow
            label="API mode"
            value={
              <span className="font-mono uppercase">{api.mode}</span>
            }
          />
          <MetaRow
            label="Sovereignty"
            value={<SovereigntyIndicator compact />}
          />
          <MetaRow
            label="Local core"
            value={<span className="text-success">Healthy</span>}
          />
          <MetaRow
            label="Demo banner"
            value={demoMode ? 'Visible in shell' : 'Hidden'}
          />
        </dl>
      </section>
    </div>
  )
}
