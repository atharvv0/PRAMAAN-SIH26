import { Navigate, Outlet, createBrowserRouter, useNavigate } from 'react-router-dom'
import { AppShell } from '@/components/layout/AppShell'
import { OverviewPage } from '@/features/dashboard/OverviewPage'
import { WorkspacesPage } from '@/features/workspaces/WorkspacesPage'
import { TasksPage } from '@/features/tasks/TasksPage'
import { TaskCreatePage } from '@/features/tasks/TaskCreatePage'
import { RunsPage } from '@/features/agent-run/RunsPage'
import { AgentRunPage } from '@/features/agent-run/AgentRunPage'
import { EvidencePage } from '@/features/evidence/EvidencePage'
import { DeliverablesPage } from '@/features/deliverables/DeliverablesPage'
import { SovereigntyPage } from '@/features/sovereignty/SovereigntyPage'
import { ApprovalsPage } from '@/features/approvals/ApprovalsPage'
import { AuditPage } from '@/features/audit/AuditPage'
import { ModelsPage } from '@/features/models/ModelsPage'
import { SettingsPage } from '@/features/settings/SettingsPage'
import { AssistantPage } from '@/features/assistant/AssistantPage'
import { AdminUsersPage } from '@/features/admin/AdminUsersPage'
import { LoginPage } from '@/features/auth/LoginPage'
import { useAuthStore } from '@/store'
import { EmptyState } from '@/components/common/States'
import { Button } from '@/components/ui/Button'

function RequireAuth() { const user = useAuthStore((s) => s.user); return user ? <Outlet /> : <Navigate to="/login" replace /> }
function RequireRole({ roles }: { roles: Array<'operator' | 'reviewer' | 'admin'> }) { const user = useAuthStore((s) => s.user); return user && roles.includes(user.role) ? <Outlet /> : <Navigate to="/" replace /> }
function GuestOnly() { const user = useAuthStore((s) => s.user); return user ? <Navigate to="/" replace /> : <Outlet /> }
function NotFoundPage() { const navigate = useNavigate(); return <div className="mx-auto max-w-xl py-16"><EmptyState title="Page not found" description="The requested PRAMAAN route does not exist." action={<Button onClick={() => navigate(-1)}>Go back</Button>} /></div> }

export const router = createBrowserRouter([
  { path: '/login', element: <GuestOnly />, children: [{ index: true, element: <LoginPage /> }] },
  { path: '/', element: <RequireAuth />, children: [{ element: <AppShell />, children: [
    { index: true, element: <OverviewPage /> },
    { path: 'workspaces', element: <WorkspacesPage /> },
    { path: 'tasks', element: <TasksPage /> },
    { path: 'tasks/new', element: <TaskCreatePage /> },
    { path: 'runs', element: <RunsPage /> },
    { path: 'runs/:runId', element: <AgentRunPage /> },
    { path: 'evidence', element: <EvidencePage /> },
    { path: 'evidence/:id', element: <EvidencePage /> },
    { path: 'deliverables', element: <DeliverablesPage /> },
    { path: 'assistant', element: <AssistantPage /> },
    { path: 'admin/users', element: <RequireRole roles={['admin']} />, children: [{ index: true, element: <AdminUsersPage /> }] },
    { path: 'sovereignty', element: <SovereigntyPage /> },
    { path: 'approvals', element: <RequireRole roles={['reviewer', 'admin']} />, children: [{ index: true, element: <ApprovalsPage /> }] },
    { path: 'audit', element: <RequireRole roles={['admin']} />, children: [{ index: true, element: <AuditPage /> }] },
    { path: 'models', element: <RequireRole roles={['reviewer', 'admin']} />, children: [{ index: true, element: <ModelsPage /> }] },
    { path: 'settings', element: <SettingsPage /> },
    { path: '*', element: <NotFoundPage /> },
  ] }] },
  { path: '*', element: <Navigate to="/login" replace /> },
])
