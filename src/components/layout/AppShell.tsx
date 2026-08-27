import { NavLink, Outlet, useLocation } from 'react-router-dom'
import {
  Activity,
  Boxes,
  CheckSquare,
  ClipboardList,
  FileOutput,
  Fingerprint,
  LayoutDashboard,
  PanelLeftClose,
  PanelLeftOpen,
  ScanSearch,
  Settings,
  Shield,
  Workflow,
} from 'lucide-react'
import { SovereigntyIndicator } from '@/components/common/Indicators'
import { useAuthStore, useWorkbenchStore } from '@/store'
import { cn } from '@/lib/utils'
import { api } from '@/api'

const NAV = [
  { to: '/', label: 'Overview', icon: LayoutDashboard, end: true },
  { to: '/workspaces', label: 'Workspaces', icon: Boxes },
  { to: '/tasks', label: 'Tasks', icon: ClipboardList },
  { to: '/runs', label: 'Runs', icon: Workflow },
  { to: '/evidence', label: 'Evidence', icon: ScanSearch },
  { to: '/deliverables', label: 'Deliverables', icon: FileOutput },
  { to: '/sovereignty', label: 'Sovereignty', icon: Shield },
  { to: '/approvals', label: 'Approvals', icon: CheckSquare },
  { to: '/audit', label: 'Audit', icon: Fingerprint },
  { to: '/models', label: 'Model Registry', icon: Activity },
  { to: '/settings', label: 'Settings', icon: Settings },
]

const CRUMBS: Record<string, string> = {
  '': 'Overview',
  workspaces: 'Workspaces',
  tasks: 'Tasks',
  runs: 'Runs',
  evidence: 'Evidence',
  deliverables: 'Deliverables',
  sovereignty: 'Sovereignty',
  approvals: 'Approvals',
  audit: 'Audit',
  models: 'Model Registry',
  settings: 'Settings',
  login: 'Sign in',
  new: 'New',
}

function breadcrumbFromPath(pathname: string): string[] {
  const parts = pathname.split('/').filter(Boolean)
  if (parts.length === 0) return ['Overview']
  return parts.map((p) => CRUMBS[p] ?? p)
}

export function AppShell() {
  const location = useLocation()
  const user = useAuthStore((s) => s.user)
  const { workspaceName, sidebarCollapsed, toggleSidebar, demoMode } =
    useWorkbenchStore()
  const crumbs = breadcrumbFromPath(location.pathname)

  return (
    <div className="min-h-screen flex flex-col bg-transparent text-text">
      {/* Compact plant status rail */}
      <div className="h-6 shrink-0 border-b border-border bg-surface/95 flex items-center gap-3 px-3 text-[10px] font-mono tracking-wide">
        <span className="text-accent font-semibold tracking-[0.14em]">PRAMAAN</span>
        <span className="text-text-muted">SIH26117</span>
        <span className="hidden md:inline text-text-muted">MRPL · On-prem workbench</span>
        <div className="ml-auto flex items-center gap-3">
          <span className="inline-flex items-center gap-1.5 text-success">
            <span className="size-1.5 bg-success" aria-hidden />
            CORE OK
          </span>
          <span className="text-text-muted">API/{api.mode.toUpperCase()}</span>
          {demoMode ? (
            <span className="text-warning border border-warning/35 bg-warning-soft px-1.5 py-px">
              DEMO
            </span>
          ) : null}
        </div>
      </div>

      <div className="flex flex-1 min-h-0">
        <aside
          className={cn(
            'shrink-0 border-r border-border bg-surface/95 flex flex-col transition-[width] duration-150',
            sidebarCollapsed ? 'w-[52px]' : 'w-[208px]',
          )}
        >
          <div className="h-11 flex items-center gap-2.5 px-3 border-b border-border">
            <div
              className="size-6 shrink-0 bg-accent text-canvas flex items-center justify-center font-bold text-[11px] tracking-tight"
              aria-hidden
            >
              P
            </div>
            {!sidebarCollapsed ? (
              <div className="min-w-0 leading-none">
                <div className="text-[13px] font-semibold tracking-[0.06em]">
                  PRAMAAN
                </div>
                <div className="text-[9px] text-text-muted mt-0.5 tracking-wider uppercase">
                  Sovereign workbench
                </div>
              </div>
            ) : null}
          </div>

          <nav className="flex-1 overflow-y-auto py-1.5" aria-label="Primary">
            {NAV.map((item) => {
              const Icon = item.icon
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.end}
                  title={item.label}
                  className={({ isActive }) =>
                    cn(
                      'group relative mx-1.5 mb-px flex items-center gap-2.5 px-2.5 py-[7px] text-[12px] transition-colors',
                      isActive
                        ? 'bg-raised text-text'
                        : 'text-text-secondary hover:bg-raised/60 hover:text-text',
                    )
                  }
                >
                  {({ isActive }) => (
                    <>
                      {isActive ? (
                        <span
                          className="absolute left-0 top-1 bottom-1 w-0.5 bg-accent"
                          aria-hidden
                        />
                      ) : null}
                      <Icon
                        className={cn(
                          'size-3.5 shrink-0',
                          isActive ? 'text-accent' : 'opacity-70',
                        )}
                        aria-hidden
                      />
                      {!sidebarCollapsed ? <span>{item.label}</span> : null}
                    </>
                  )}
                </NavLink>
              )
            })}
          </nav>

          <div className="border-t border-border p-2 space-y-2">
            {!sidebarCollapsed ? (
              <>
                <SovereigntyIndicator compact />
                <div className="px-1 pt-0.5">
                  <div className="text-[11px] font-medium text-text-secondary truncate">
                    {user?.name ?? 'Unsigned'}
                  </div>
                  <div className="text-[10px] text-text-muted capitalize">
                    {user?.role ?? '—'} · {user?.org?.split('—')[0]?.trim() ?? 'Local'}
                  </div>
                </div>
              </>
            ) : (
              <div className="flex justify-center">
                <SovereigntyIndicator compact />
              </div>
            )}
            <button
              type="button"
              onClick={toggleSidebar}
              className="w-full h-7 inline-flex items-center justify-center gap-1.5 text-text-muted hover:text-text hover:bg-raised text-[11px]"
              aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            >
              {sidebarCollapsed ? (
                <PanelLeftOpen className="size-3.5" />
              ) : (
                <>
                  <PanelLeftClose className="size-3.5" />
                  Collapse
                </>
              )}
            </button>
          </div>
        </aside>

        <div className="flex-1 flex flex-col min-w-0">
          <header className="h-11 shrink-0 border-b border-border bg-panel/90 backdrop-blur-[2px] flex items-center gap-3 px-4">
            <div className="min-w-0 flex-1">
              <div className="text-[10px] text-text-muted font-mono tracking-wide truncate">
                WS · {workspaceName}
              </div>
              <nav
                aria-label="Breadcrumb"
                className="flex items-center gap-1.5 text-[12px] leading-tight"
              >
                {crumbs.map((c, i) => (
                  <span key={`${c}-${i}`} className="flex items-center gap-1.5">
                    {i > 0 ? (
                      <span className="text-text-muted" aria-hidden>
                        /
                      </span>
                    ) : null}
                    <span
                      className={
                        i === crumbs.length - 1
                          ? 'text-text font-medium'
                          : 'text-text-secondary'
                      }
                    >
                      {c}
                    </span>
                  </span>
                ))}
              </nav>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <SovereigntyIndicator compact />
              <div className="hidden lg:flex items-center gap-2 border border-border h-7 px-2 text-[11px] text-text-muted bg-canvas min-w-[160px]">
                <span>Search workbench</span>
                <kbd className="ml-auto font-mono text-[9px] border border-border px-1 text-text-muted">
                  ⌘K
                </kbd>
              </div>
              <div className="h-7 pl-1.5 pr-2 border border-border flex items-center gap-2 text-[11px] bg-canvas">
                <span className="size-5 bg-raised border border-border flex items-center justify-center text-[10px] font-semibold text-accent">
                  {(user?.name ?? '?').slice(0, 1)}
                </span>
                <span className="hidden md:inline text-text-secondary max-w-[100px] truncate">
                  {user?.name}
                </span>
              </div>
            </div>
          </header>

          <main className="flex-1 overflow-auto">
            <div className="min-h-full p-3 md:p-4 lg:p-5">
              <Outlet />
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}
