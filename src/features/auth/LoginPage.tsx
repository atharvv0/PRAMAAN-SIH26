import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { useAuthStore, type UserRole } from '@/store'
import { cn } from '@/lib/utils'

const ROLES: { id: UserRole; label: string; brief: string }[] = [
  {
    id: 'operator',
    label: 'Operator',
    brief: 'Submit work packages, monitor runs, open evidence.',
  },
  {
    id: 'reviewer',
    label: 'Reviewer',
    brief: 'Inspect claims, decide HITL approvals, audit provenance.',
  },
  {
    id: 'admin',
    label: 'Admin',
    brief: 'Sovereignty policy, model registry, system settings.',
  },
]

export function LoginPage() {
  const navigate = useNavigate()
  const signIn = useAuthStore((s) => s.signIn)
  const [role, setRole] = useState<UserRole>('operator')

  function handleSignIn() {
    signIn(role)
    navigate('/')
  }

  return (
    <div className="min-h-screen flex">
      {/* Brand plane */}
      <aside className="hidden lg:flex w-[42%] max-w-xl flex-col justify-between border-r border-border bg-surface/90 p-8 relative overflow-hidden">
        <div
          className="pointer-events-none absolute inset-0 opacity-[0.35]"
          style={{
            backgroundImage:
              'linear-gradient(rgba(36,48,65,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(36,48,65,0.5) 1px, transparent 1px)',
            backgroundSize: '24px 24px',
          }}
          aria-hidden
        />
        <div className="relative">
          <div className="inline-flex items-center gap-3">
            <div className="size-9 bg-accent text-canvas flex items-center justify-center font-bold text-sm">
              P
            </div>
            <div>
              <div className="text-[15px] font-semibold tracking-[0.12em]">PRAMAAN</div>
              <div className="text-[10px] text-text-muted tracking-wider uppercase mt-0.5">
                SIH26117 · MRPL
              </div>
            </div>
          </div>
        </div>

        <div className="relative space-y-4 max-w-sm">
          <h1 className="text-[22px] font-semibold leading-snug tracking-tight text-text">
            Sovereign on-premise agentic execution
          </h1>
          <p className="text-[12.5px] text-text-secondary leading-relaxed">
            Delegate confidential multimodal industrial work to local models — with
            every tool call, evidence link, and network boundary observable.
          </p>
          <dl className="border border-border bg-panel divide-y divide-border text-[11px]">
            <div className="flex justify-between px-3 py-2">
              <dt className="text-text-muted">Egress</dt>
              <dd className="text-blocked font-semibold">DENY BY DEFAULT</dd>
            </div>
            <div className="flex justify-between px-3 py-2">
              <dt className="text-text-muted">Processing</dt>
              <dd className="text-text font-medium">Local / on-prem</dd>
            </div>
            <div className="flex justify-between px-3 py-2">
              <dt className="text-text-muted">Audit</dt>
              <dd className="text-success font-medium">Recording</dd>
            </div>
          </dl>
        </div>

        <p className="relative text-[10px] text-text-muted font-mono">
          Frontend demo session · FastAPI contracts pending integration
        </p>
      </aside>

      <main className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-md border border-border bg-panel">
          <div className="border-b border-border px-5 py-3.5 flex items-center gap-3 lg:hidden">
            <div className="size-7 bg-accent text-canvas flex items-center justify-center font-bold text-xs">
              P
            </div>
            <div>
              <div className="text-sm font-semibold tracking-[0.08em]">PRAMAAN</div>
              <div className="text-[10px] text-text-muted">Sovereign Workbench</div>
            </div>
          </div>

          <div className="px-5 py-5 space-y-4">
            <div>
              <h2 className="text-[15px] font-semibold text-text">Sign in</h2>
              <p className="text-[11.5px] text-text-muted mt-1 leading-relaxed">
                Role selection maps to a local operator profile for evaluation. No
                credentials leave this host.
              </p>
            </div>

            <div>
              <div className="text-micro text-text-muted mb-2">Role</div>
              <div className="border border-border divide-y divide-border">
                {ROLES.map((r) => (
                  <button
                    key={r.id}
                    type="button"
                    onClick={() => setRole(r.id)}
                    className={cn(
                      'w-full text-left px-3 py-2.5 transition-colors relative',
                      role === r.id
                        ? 'bg-raised'
                        : 'hover:bg-raised/50',
                    )}
                  >
                    {role === r.id ? (
                      <span
                        className="absolute left-0 top-1 bottom-1 w-0.5 bg-accent"
                        aria-hidden
                      />
                    ) : null}
                    <div className="text-[13px] font-medium text-text">{r.label}</div>
                    <div className="text-[11px] text-text-muted mt-0.5">{r.brief}</div>
                  </button>
                ))}
              </div>
            </div>

            <Button variant="primary" className="w-full" onClick={handleSignIn}>
              Continue as {ROLES.find((r) => r.id === role)?.label}
            </Button>
          </div>
        </div>
      </main>
    </div>
  )
}
