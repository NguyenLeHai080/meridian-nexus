import { create } from 'zustand'
import { createJSONStorage, persist } from 'zustand/middleware'

interface ChatState {
  open: boolean
  token: string | null
  message: string
  guest: { name: string; email: string }
  setOpen: (open: boolean) => void
  setToken: (token: string) => void
  setMessage: (message: string) => void
  setGuest: (guest: { name: string; email: string }) => void
}

export const useChatStore = create<ChatState>()(
  persist(
    (set) => ({
      open: false,
      token: null,
      message: '',
      guest: { name: '', email: '' },
      setOpen: (open) => set({ open }),
      setToken: (token) => set({ token }),
      setMessage: (message) => set({ message }),
      setGuest: (guest) => set({ guest }),
    }),
    {
      name: 'northstar-chat',
      storage: createJSONStorage(() => sessionStorage),
      partialize: (state) => ({ token: state.token }),
    },
  ),
)
