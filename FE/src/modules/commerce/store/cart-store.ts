import { create } from 'zustand'
import { createJSONStorage, persist } from 'zustand/middleware'
import type { Product } from '../types/commerce.types'

export const CART_STORAGE_KEY = 'northstar-cart'

export interface CartItem {
  product: Product
  quantity: number
}

interface CartState {
  items: CartItem[]
  add: (product: Product) => void
  remove: (productId: number) => void
  setQuantity: (productId: number, quantity: number) => void
  clear: () => void
}

export const useCartStore = create<CartState>()(
  persist(
    (set) => ({
      items: [],
      add: (product) =>
        set((state) => {
          if (product.stock <= 0) {
            return state
          }

          const existing = state.items.find((item) => item.product.id === product.id)

          if (existing === undefined) {
            return { items: [...state.items, { product, quantity: 1 }] }
          }

          const items = state.items.map((item) => {
            if (item.product.id === product.id) {
              return { ...item, product, quantity: Math.min(item.quantity + 1, product.stock) }
            }

            return item
          })

          return { items }
        }),
      remove: (productId) =>
        set((state) => ({ items: state.items.filter((item) => item.product.id !== productId) })),
      setQuantity: (productId, quantity) =>
        set((state) => {
          const item = state.items.find((candidate) => candidate.product.id === productId)
          if (item === undefined) {
            return state
          }
          if (item.product.stock <= 0) {
            return { items: state.items.filter((candidate) => candidate.product.id !== productId) }
          }

          const normalizedQuantity = Math.max(1, Math.min(Math.trunc(quantity), item.product.stock))
          const items = state.items.map((candidate) => {
            if (candidate.product.id === productId) {
              return { ...candidate, quantity: normalizedQuantity }
            }

            return candidate
          })

          return { items }
        }),
      clear: () => set({ items: [] }),
    }),
    {
      name: CART_STORAGE_KEY,
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({ items: state.items }),
      version: 1,
    },
  ),
)
