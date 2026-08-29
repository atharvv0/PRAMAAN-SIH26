import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type UserRole = 'operator' | 'reviewer' | 'admin'
export type ThemeMode = 'dark' | 'light' | 'system'

export interface AuthUser {
  id: string
  name: string
  role: UserRole
  org: string
  email: string
}

interface AuthState {
  user: AuthUser | null
  setUser: (user: AuthUser) => void
  signOut: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      setUser: (user) => set({ user }),
      signOut: () => set({ user: null }),
    }),
    { name: 'pramaan-auth-v2' },
  ),
)

interface WorkbenchState {
  workspaceId: string
  workspaceName: string
  sidebarCollapsed: boolean
  theme: ThemeMode
  setWorkspace: (id: string, name: string) => void
  toggleSidebar: () => void
  setTheme: (theme: ThemeMode) => void
}

export const useWorkbenchStore = create<WorkbenchState>()(
  persist(
    (set) => ({
      workspaceId: '',
      workspaceName: 'No workspace selected',
      sidebarCollapsed: false,
      theme: 'light',
      setWorkspace: (id, name) => set({ workspaceId: id, workspaceName: name }),
      toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
      setTheme: (theme) => set({ theme }),
    }),
    { name: 'pramaan-workbench-v2' },
  ),
)
