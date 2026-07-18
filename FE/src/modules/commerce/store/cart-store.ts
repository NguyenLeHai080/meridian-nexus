import { create } from 'zustand'
import type { Product } from '../types/commerce.types'

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

export const useCartStore = create<CartState>((set) => ({
  items: [],
  add: (product) =>
    set((state) => {
      const existing = state.items.find((item) => item.product.id === product.id)

      if (existing === undefined) {
        return { items: [...state.items, { product, quantity: 1 }] }
      }

      const items = state.items.map((item) => {
        if (item.product.id === product.id) {
          return { ...item, quantity: Math.min(item.quantity + 1, product.stock) }
        }

        return item
      })

      return { items }
    }),
  remove: (productId) =>
    set((state) => ({ items: state.items.filter((item) => item.product.id !== productId) })),
  setQuantity: (productId, quantity) =>
    set((state) => {
      const items = state.items.map((item) => {
        if (item.product.id === productId) {
          return { ...item, quantity: Math.max(1, Math.min(quantity, item.product.stock)) }
        }

        return item
      })

      return { items }
    }),
  clear: () => set({ items: [] }),
}))
