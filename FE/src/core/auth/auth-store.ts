import { create } from 'zustand'
import type { AuthenticatedUser } from './auth.types'

interface AuthState {
  user: AuthenticatedUser | null
  initialized: boolean
  setSession: (user: AuthenticatedUser) => void
  setUser: (user: AuthenticatedUser | null) => void
  markInitialized: () => void
  clearSession: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  initialized: false,
  setSession: (user) => set({ user, initialized: true }),
  setUser: (user) => set({ user }),
  markInitialized: () => set({ initialized: true }),
  clearSession: () => set({ user: null, initialized: true }),
}))
