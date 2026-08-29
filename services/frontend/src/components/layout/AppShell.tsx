import { useState } from 'react'
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { Activity, Boxes, CheckSquare, ClipboardList, FileOutput, Fingerprint, LayoutDashboard, Menu, PanelLeftClose, PanelLeftOpen, ScanSearch, Settings, Shield, Workflow, LogOut, Moon, Sun } from 'lucide-react'
import { SovereigntyIndicator, HealthIndicator } from '@/components/common/Indicators'
import { useAuthStore, useWorkbenchStore } from '@/store'
import { useHealth } from '@/hooks'
import { cn } from '@/lib/utils'
import { useQueryClient } from '@tanstack/react-query'

const NAV = [
  { to: '/', label: 'Overview', icon: LayoutDashboard, end: true },
  { to: '/workspaces', label: 'Workspaces', icon: Boxes },
  { to: '/tasks', label: 'Tasks', icon: ClipboardList },
  { to: '/runs', label: 'Runs', icon: Workflow },
  { to: '/evidence', label: 'Evidence', icon: ScanSearch },
  { to: '/deliverables', label: 'Deliverables', icon: FileOutput },
  { to: '/approvals', label: 'Approvals', icon: CheckSquare },
  { to: '/sovereignty', label: 'Sovereignty', icon: Shield },
  { to: '/audit', label: 'Audit', icon: Fingerprint },
  { to: '/models', label: 'Model Registry', icon: Activity },
  { to: '/settings', label: 'Settings', icon: Settings },
]

function breadcrumbFromPath(pathname: string) {
  const labels: Record<string, string> = { workspaces: 'Workspaces', tasks: 'Tasks', runs: 'Runs', evidence: 'Evidence', deliverables: 'Deliverables', approvals: 'Approvals', sovereignty: 'Sovereignty', audit: 'Audit', models: 'Model Registry', settings: 'Settings', new: 'New task' }
  const parts = pathname.split('/').filter(Boolean)
  return parts.length ? ['Overview', ...parts.map((p) => labels[p] ?? p)] : ['Overview']
}

export function AppShell() {
  const location = useLocation()
  const navigate = useNavigate()
  const qc = useQueryClient()
  const user = useAuthStore((s) => s.user)
  const signOut = useAuthStore((s) => s.signOut)
  const { workspaceName, sidebarCollapsed, toggleSidebar, theme, setTheme } = useWorkbenchStore()
  const health = useHealth()
  const [mobileOpen, setMobileOpen] = useState(false)

  function handleSignOut() {
    signOut()
    qc.clear()
    navigate('/login', { replace: true })
  }

  return <div className="min-h-screen bg-canvas text-text">
    <div className="sticky top-0 z-40 flex h-8 items-center gap-3 border-b border-border bg-surface/95 px-3 text-[10px] backdrop-blur">
      <div className="flex items-center gap-2"><img src="/brand/pramaan-mark.png" alt="" className="size-4 object-contain" /><span className="font-semibold tracking-[0.18em] text-accent">PRAMAAN</span><span className="hidden text-text-muted sm:inline">SOVEREIGN WORKBENCH</span></div>
      <div className="ml-auto flex items-center gap-2"><HealthIndicator compact /><span className="hidden md:inline"><SovereigntyIndicator compact /></span></div>
    </div>

    <div className="flex min-h-[calc(100vh-2rem)]">
      {mobileOpen ? <button className="fixed inset-0 z-30 bg-black/45 md:hidden" aria-label="Close navigation" onClick={() => setMobileOpen(false)} /> : null}
      <aside className={cn('fixed inset-y-8 left-0 z-40 flex w-[258px] -translate-x-full flex-col border-r border-border bg-surface transition-transform md:static md:translate-x-0', mobileOpen && 'translate-x-0', sidebarCollapsed ? 'md:w-[70px]' : 'md:w-[250px]')}>
        <div className="flex h-[72px] items-center gap-3 border-b border-border px-4">
          <img
            src="/brand/pramaan-mark.png"
            alt="PRAMAAN"
            className={cn(
              'shrink-0 object-contain',
              sidebarCollapsed ? 'size-10' : 'size-10',
            )}
          />
          {!sidebarCollapsed ? (
            <div className="min-w-0">
              <div className="font-semibold tracking-[0.14em] text-accent">
                PRAMAAN
              </div>
              <div className="mt-0.5 text-[9px] font-medium tracking-[0.08em] text-text-muted">
                SOVEREIGN WORKBENCH
              </div>
            </div>
          ) : null}
        </div>
        <div className="border-b border-border px-3 py-2.5"><div className="text-micro text-text-muted">Workspace</div><div className={cn('mt-1 truncate text-[12px] font-medium text-text', sidebarCollapsed && 'text-center')}>{sidebarCollapsed ? '—' : workspaceName}</div></div>
        <nav className="flex-1 overflow-y-auto p-2" aria-label="Primary">
          {NAV.map((item) => { const Icon = item.icon; return <NavLink key={item.to} to={item.to} end={item.end} title={item.label} onClick={() => setMobileOpen(false)} className={({ isActive }) => cn('group relative mb-0.5 flex items-center gap-3 px-3 py-2.5 text-[12px] font-medium transition-colors', isActive ? 'bg-raised text-text' : 'text-text-secondary hover:bg-raised/70 hover:text-text')}>
            {({ isActive }) => <><span className={cn('absolute left-0 top-2 bottom-2 w-0.5', isActive ? 'bg-accent' : 'bg-transparent')} /><Icon className={cn('size-4 shrink-0', isActive ? 'text-accent' : 'text-text-muted group-hover:text-text')} aria-hidden />{!sidebarCollapsed ? <span>{item.label}</span> : null}</>}
          </NavLink> })}
        </nav>
        <div className="space-y-2 border-t border-border p-2.5">
          {!sidebarCollapsed ? <div className="border border-border bg-panel px-3 py-2.5"><div className="text-[11px] font-medium text-text">{user?.name}</div><div className="mt-0.5 truncate text-[10px] text-text-muted">{user?.role} · {user?.org}</div></div> : null}
          <button type="button" onClick={handleSignOut} className="flex h-8 w-full items-center justify-center gap-2 border border-border text-[11px] text-text-muted hover:bg-raised hover:text-text" title="Sign out"><LogOut className="size-3.5" aria-hidden />{!sidebarCollapsed ? 'Sign out' : null}</button>
          <button type="button" onClick={toggleSidebar} className="hidden h-8 w-full items-center justify-center gap-2 border border-border text-[11px] text-text-muted hover:bg-raised hover:text-text md:flex" aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}>{sidebarCollapsed ? <PanelLeftOpen className="size-3.5" /> : <><PanelLeftClose className="size-3.5" />Collapse</>}</button>
        </div>
      </aside>

      <div className="min-w-0 flex-1">
        <header className="sticky top-8 z-20 border-b border-border bg-panel/95 backdrop-blur">
          <div className="flex min-h-14 items-center gap-3 px-4 lg:px-6"><button type="button" className="grid size-8 place-items-center border border-border md:hidden" onClick={() => setMobileOpen(true)} aria-label="Open navigation"><Menu className="size-4" /></button><div className="min-w-0 flex-1"><div className="flex items-center gap-1 text-[10px] text-text-muted"><span className="font-mono">WS</span><span>/</span><span className="truncate">{workspaceName}</span></div><nav className="mt-1 flex flex-wrap items-center gap-1.5 text-[12px]" aria-label="Breadcrumb">{breadcrumbFromPath(location.pathname).map((c, i) => <span key={`${c}-${i}`} className={cn('flex items-center gap-1.5', i === 0 ? 'text-text-muted' : i === breadcrumbFromPath(location.pathname).length - 1 ? 'font-medium text-text' : 'text-text-secondary')}>{i ? <span aria-hidden>/</span> : null}{c}</span>)}</nav></div><div className="flex items-center gap-2"><HealthIndicator /><button type="button" onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')} className="grid size-8 place-items-center border border-border bg-surface text-text-muted transition-colors hover:bg-raised hover:text-text" aria-label={theme === 'light' ? 'Switch to dark theme' : 'Switch to light theme'} title={theme === 'light' ? 'Dark theme' : 'Light theme'}>{theme === 'light' ? <Moon className="size-3.5" /> : <Sun className="size-3.5" />}</button>{health.isError ? <span className="hidden text-[10px] text-warning lg:inline">Local API unavailable</span> : null}</div></div>
        </header>
        <main className="min-h-[calc(100vh-7.5rem)]"><div className="mx-auto w-full max-w-[1600px] p-4 lg:p-6"><Outlet /></div></main>
      </div>
    </div>
  </div>
}
