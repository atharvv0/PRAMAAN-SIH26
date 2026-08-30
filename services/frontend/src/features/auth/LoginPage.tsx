import { useState, type FormEvent } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { ArrowRight, Eye, EyeOff, KeyRound, Moon, ShieldCheck, Sun, UserPlus } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Field, Input } from '@/components/ui/Field'
import { useAuthStore, useWorkbenchStore } from '@/store'
import { authenticateLocalAccount, passwordPolicy, registerLocalAccount } from '@/lib/localAuth'
import { api } from '@/api'
import { cn } from '@/lib/utils'

const roles = [
  ['operator', 'Operator', 'Create work packages and monitor execution.'],
  ['reviewer', 'Reviewer', 'Validate evidence and make approval decisions.'],
  ['admin', 'Administrator', 'Review platform state and sovereign controls.'],
] as const

type Mode = 'signin' | 'signup'

export function LoginPage() {
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const setUser = useAuthStore((s) => s.setUser)
  const theme = useWorkbenchStore((s) => s.theme)
  const setTheme = useWorkbenchStore((s) => s.setTheme)
  const [mode, setMode] = useState<Mode>('signin')
  const [identifier, setIdentifier] = useState('')
  const [userId, setUserId] = useState('')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [org, setOrg] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  if (user) return <Navigate to="/" replace />

  function switchMode(next: Mode) {
    setMode(next)
    setError('')
    setPassword('')
    setConfirm('')
  }

  async function submit(event: FormEvent) {
    event.preventDefault()
    setError('')
    setBusy(true)
    try {
      let localUser
      if (mode === 'signin') {
        localUser = await authenticateLocalAccount(identifier, password)
      } else {
        if (password !== confirm) throw new Error('Passwords do not match.')
        localUser = await registerLocalAccount({ id: userId, name, email, org, password })
      }
      setUser(localUser)
      try {
        const serverUser = await api.getCurrentUser()
        setUser({ ...localUser, id: localUser.id, name: serverUser.name || localUser.name, email: serverUser.email || localUser.email, role: serverUser.role })
      } catch {
        // Local auth remains usable when the backend is temporarily unavailable.
      }
      navigate('/', { replace: true })
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Authentication failed.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="min-h-screen bg-canvas lg:grid lg:grid-cols-[minmax(0,1.08fr)_minmax(500px,0.92fr)]">
      <section className="relative hidden overflow-hidden border-r border-border bg-surface lg:flex lg:flex-col lg:justify-between lg:p-10">
        <div className="pointer-events-none absolute inset-0" aria-hidden>
          <div className="absolute inset-0 opacity-40 [background-image:linear-gradient(var(--color-border)_1px,transparent_1px),linear-gradient(90deg,var(--color-border)_1px,transparent_1px)] [background-size:40px_40px]" />
          <div className="absolute -left-24 top-16 size-[28rem] rounded-full bg-accent/10 blur-3xl" />
          <div className="absolute bottom-0 right-0 size-96 rounded-full bg-info/10 blur-3xl" />
        </div>
        <div className="relative">
          <img src="/brand/pramaan-wordmark.png" alt="PRAMAAN — Intelligent Digital Trust" className="w-[280px]" />
          <div className="mt-14 max-w-2xl">
            <p className="text-micro text-accent">SOVEREIGN AI WORKBENCH</p>
            <h1 className="mt-3 text-5xl font-semibold leading-[1.05] tracking-[-0.04em] text-text">Confidential work. Local execution. Verifiable outcomes.</h1>
            <p className="mt-6 max-w-xl text-[15px] leading-7 text-text-secondary">PRAMAAN coordinates local models, controlled tools, evidence, approvals, and audit records without introducing a cloud AI dependency into the workbench.</p>
          </div>
        </div>
        <div className="relative grid max-w-2xl grid-cols-3 gap-px overflow-hidden rounded-sm border border-border bg-border">
          <Feature label="PROCESSING" value="LOCAL / ON-PREM" />
          <Feature label="EGRESS" value="POLICY CONTROLLED" />
          <Feature label="AUDIT" value="RECORDED" />
        </div>
      </section>

      <main className="relative flex min-h-screen items-center justify-center p-4 sm:p-8">
        <button type="button" onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')} className="absolute right-4 top-4 grid size-9 place-items-center rounded-sm border border-border bg-panel text-text-muted shadow-sm transition-colors hover:bg-raised hover:text-text sm:right-8 sm:top-8" aria-label={theme === 'light' ? 'Switch to dark theme' : 'Switch to light theme'}>{theme === 'light' ? <Moon className="size-4" /> : <Sun className="size-4" />}</button>
        <form onSubmit={(event) => void submit(event)} className="w-full max-w-[560px] overflow-hidden rounded-sm border border-border bg-panel shadow-[0_24px_80px_rgba(15,35,48,.12)]">
          <div className="border-b border-border px-6 py-5 sm:px-8">
            <div className="flex items-center gap-3 lg:hidden">
              <img src="/brand/pramaan-mark.png" alt="PRAMAAN" className="size-10 object-contain" />
              <div><div className="font-semibold tracking-[0.14em] text-accent">PRAMAAN</div><div className="text-[9px] tracking-[0.08em] text-text-muted">SOVEREIGN WORKBENCH</div></div>
            </div>
            <div className="mt-5 lg:mt-0">
              <div className="text-micro text-accent">IDENTITY & ACCESS</div>
              <h2 className="mt-1 text-2xl font-semibold tracking-tight">{mode === 'signin' ? 'Sign in' : 'Create local account'}</h2>
              <p className="mt-2 text-[12px] leading-relaxed text-text-muted">{mode === 'signin' ? 'Authenticate to the browser-local PRAMAAN workbench.' : 'Create a browser-local operator account for this workbench installation.'}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 border-b border-border p-1.5 bg-surface">
            <button type="button" onClick={() => switchMode('signin')} className={cn('h-9 text-[12px] font-semibold transition-colors', mode === 'signin' ? 'bg-panel text-text shadow-sm' : 'text-text-muted hover:text-text')}>Sign in</button>
            <button type="button" onClick={() => switchMode('signup')} className={cn('h-9 text-[12px] font-semibold transition-colors', mode === 'signup' ? 'bg-panel text-text shadow-sm' : 'text-text-muted hover:text-text')}>Create account</button>
          </div>

          <div className="space-y-5 px-6 py-6 sm:px-8">
            {mode === 'signin' ? (
              <>
                <Field label="User ID or work email"><Input autoFocus autoComplete="username" value={identifier} onChange={(e) => { setIdentifier(e.target.value); setError('') }} placeholder="operator-01 or name@organization.com" /></Field>
                <PasswordField value={password} onChange={setPassword} visible={showPassword} onToggle={() => setShowPassword((value) => !value)} autoComplete="current-password" />
              </>
            ) : (
              <>
                <div className="grid gap-4 sm:grid-cols-2">
                  <Field label="User ID"><Input autoFocus autoComplete="username" value={userId} onChange={(e) => { setUserId(e.target.value.toLowerCase()); setError('') }} placeholder="operator-01" /></Field>
                  <Field label="Full name"><Input autoComplete="name" value={name} onChange={(e) => setName(e.target.value)} placeholder="Your full name" /></Field>
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <Field label="Work email"><Input type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="name@organization.com" /></Field>
                  <Field label="Organization / unit"><Input autoComplete="organization" value={org} onChange={(e) => setOrg(e.target.value)} placeholder="Organization" /></Field>
                </div>
                <PasswordField value={password} onChange={setPassword} visible={showPassword} onToggle={() => setShowPassword((value) => !value)} autoComplete="new-password" />
                <Field label="Confirm password"><Input type={showPassword ? 'text' : 'password'} autoComplete="new-password" value={confirm} onChange={(e) => setConfirm(e.target.value)} placeholder="Repeat password" /></Field>
                <div className="border border-border bg-surface px-3 py-2.5 text-[10.5px] leading-relaxed text-text-muted"><KeyRound className="mr-1.5 inline size-3.5 text-accent" aria-hidden />{passwordPolicy()}</div>
                <div><div className="text-micro mb-2 text-text-muted">Initial role</div><div className="grid gap-2 md:grid-cols-3">{roles.map(([id, label, brief]) => <div key={id} className={cn('border border-border bg-canvas p-3', id !== 'operator' && 'opacity-60')}><div className="text-[12px] font-semibold text-text">{label}</div><div className="mt-1 text-[10px] leading-snug text-text-muted">{brief}</div>{id === 'operator' ? <div className="mt-2 text-[9px] font-semibold uppercase tracking-wider text-accent">Default</div> : <div className="mt-2 text-[9px] uppercase tracking-wider text-text-muted">Assigned by policy</div>}</div>)}</div></div>
              </>
            )}

            {error ? <div className="border border-danger/35 bg-danger-soft px-3 py-2.5 text-[11px] leading-relaxed text-danger" role="alert">{error}</div> : null}
            <Button type="submit" variant="primary" size="lg" className="w-full" disabled={busy} rightIcon={<ArrowRight className="size-4" />}>{busy ? 'Please wait…' : mode === 'signin' ? 'Enter local workbench' : 'Create account & enter'}</Button>
            <div className="flex items-start gap-2 border border-border bg-surface px-3 py-2.5 text-[10.5px] leading-relaxed text-text-muted"><ShieldCheck className="mt-0.5 size-3.5 shrink-0 text-accent" aria-hidden /><span>Credentials are stored only in this browser using a salted PBKDF2 password hash. This is a local access layer, not enterprise identity authentication.</span></div>
            {mode === 'signup' ? <div className="flex items-center gap-2 text-[10.5px] text-text-muted"><UserPlus className="size-3.5" aria-hidden />New accounts start as operators. Privileged roles should be provisioned by the authoritative backend when server-side identity is available.</div> : null}
          </div>
        </form>
      </main>
    </div>
  )
}

function PasswordField({ value, onChange, visible, onToggle, autoComplete }: { value: string; onChange: (value: string) => void; visible: boolean; onToggle: () => void; autoComplete: string }) {
  return <Field label="Password"><div className="relative"><Input type={visible ? 'text' : 'password'} autoComplete={autoComplete} value={value} onChange={(e) => onChange(e.target.value)} placeholder="Password" className="pr-10" /><button type="button" onClick={onToggle} className="absolute right-0 top-0 grid h-8 w-9 place-items-center text-text-muted hover:text-text" aria-label={visible ? 'Hide password' : 'Show password'}>{visible ? <EyeOff className="size-3.5" /> : <Eye className="size-3.5" />}</button></div></Field>
}

function Feature({ label, value }: { label: string; value: string }) {
  return <div className="bg-panel px-4 py-3"><div className="text-micro text-text-muted">{label}</div><div className="mt-1 text-[11px] font-semibold text-text">{value}</div></div>
}
