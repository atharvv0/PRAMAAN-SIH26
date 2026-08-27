import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type UserRole = 'operator' | 'reviewer' | 'admin'

export interface AuthUser {
  id: string
  name: string
  role: UserRole
  org: string
}

interface AuthState {
  user: AuthUser | null
  signIn: (role: UserRole) => void
  signOut: () => void
}

const ROLE_USERS: Record<UserRole, AuthUser> = {
  operator: {
    id: 'usr-op-01',
    name: 'R. Shetty',
    role: 'operator',
    org: 'MRPL — Inspection Ops',
  },
  reviewer: {
    id: 'usr-rev-01',
    name: 'A. Pai',
    role: 'reviewer',
    org: 'MRPL — Technical Review',
  },
  admin: {
    id: 'usr-adm-01',
    name: 'K. Rao',
    role: 'admin',
    org: 'MRPL — Platform Admin',
  },
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      signIn: (role) => set({ user: ROLE_USERS[role] }),
      signOut: () => set({ user: null }),
    }),
    { name: 'pramaan-auth' },
  ),
)

interface WorkbenchState {
  workspaceId: string
  workspaceName: string
  demoMode: boolean
  sidebarCollapsed: boolean
  setWorkspace: (id: string, name: string) => void
  setDemoMode: (on: boolean) => void
  toggleSidebar: () => void
}

export const useWorkbenchStore = create<WorkbenchState>()(
  persist(
    (set) => ({
      workspaceId: 'ws-mrpl-inspection',
      workspaceName: 'MRPL Inspection Review',
      demoMode: true,
      sidebarCollapsed: false,
      setWorkspace: (id, name) => set({ workspaceId: id, workspaceName: name }),
      setDemoMode: (demoMode) => set({ demoMode }),
      toggleSidebar: () =>
        set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
    }),
    { name: 'pramaan-workbench' },
  ),
)
