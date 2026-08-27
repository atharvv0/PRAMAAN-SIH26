import { Navigate, Outlet, createBrowserRouter } from 'react-router-dom'
import { AppShell } from '@/components/layout/AppShell'
import { LoginPage } from '@/features/auth/LoginPage'
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
import { useAuthStore } from '@/store'

function RequireAuth() {
  const user = useAuthStore((s) => s.user)
  if (!user) return <Navigate to="/login" replace />
  return <Outlet />
}

function GuestOnly() {
  const user = useAuthStore((s) => s.user)
  if (user) return <Navigate to="/" replace />
  return <Outlet />
}

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <GuestOnly />,
    children: [{ index: true, element: <LoginPage /> }],
  },
  {
    path: '/',
    element: <RequireAuth />,
    children: [
      {
        element: <AppShell />,
        children: [
          { index: true, element: <OverviewPage /> },
          { path: 'workspaces', element: <WorkspacesPage /> },
          { path: 'tasks', element: <TasksPage /> },
          { path: 'tasks/new', element: <TaskCreatePage /> },
          { path: 'runs', element: <RunsPage /> },
          { path: 'runs/:runId', element: <AgentRunPage /> },
          { path: 'evidence', element: <EvidencePage /> },
          { path: 'evidence/:id', element: <EvidencePage /> },
          { path: 'deliverables', element: <DeliverablesPage /> },
          { path: 'sovereignty', element: <SovereigntyPage /> },
          { path: 'approvals', element: <ApprovalsPage /> },
          { path: 'audit', element: <AuditPage /> },
          { path: 'models', element: <ModelsPage /> },
          { path: 'settings', element: <SettingsPage /> },
        ],
      },
    ],
  },
  { path: '*', element: <Navigate to="/" replace /> },
])
