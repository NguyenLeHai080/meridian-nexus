import { beforeEach, describe, expect, it } from 'vitest'
import type { Product } from '../types/commerce.types'
import { CART_STORAGE_KEY, useCartStore } from './cart-store'

function product(overrides: Partial<Product> = {}): Product {
  return {
    id: 1,
    name: 'Test product',
    slug: 'test-product',
    sku: 'TEST-001',
    excerpt: null,
    description: null,
    price: 25,
    sale_price: null,
    stock: 3,
    images: [],
    is_featured: false,
    category: null,
    published_at: '2026-07-20T00:00:00Z',
    ...overrides,
  }
}

describe('cart store', () => {
  beforeEach(() => {
    localStorage.clear()
    useCartStore.setState({ items: [] })
  })

  it('adds products and caps quantity at available stock', () => {
    const item = product({ stock: 2 })

    useCartStore.getState().add(item)
    useCartStore.getState().add(item)
    useCartStore.getState().add(item)

    expect(useCartStore.getState().items).toEqual([{ product: item, quantity: 2 }])
  })

  it('does not add products that are out of stock', () => {
    useCartStore.getState().add(product({ stock: 0 }))

    expect(useCartStore.getState().items).toEqual([])
  })

  it('normalizes quantity and removes stale out-of-stock items', () => {
    const item = product({ stock: 3 })
    useCartStore.setState({ items: [{ product: item, quantity: 1 }] })

    useCartStore.getState().setQuantity(item.id, 2.8)
    expect(useCartStore.getState().items[0]?.quantity).toBe(2)

    useCartStore.setState({ items: [{ product: { ...item, stock: 0 }, quantity: 2 }] })
    useCartStore.getState().setQuantity(item.id, 1)
    expect(useCartStore.getState().items).toEqual([])
  })

  it('leaves unrelated items unchanged and ignores unknown products', () => {
    const first = product()
    const second = product({ id: 2, sku: 'TEST-002' })
    useCartStore.setState({
      items: [
        { product: first, quantity: 1 },
        { product: second, quantity: 1 },
      ],
    })

    useCartStore.getState().add(first)
    useCartStore.getState().setQuantity(999, 2)

    expect(useCartStore.getState().items).toEqual([
      { product: first, quantity: 2 },
      { product: second, quantity: 1 },
    ])
  })

  it('removes individual products and clears the cart', () => {
    const first = product()
    const second = product({ id: 2, sku: 'TEST-002' })
    useCartStore.setState({
      items: [
        { product: first, quantity: 1 },
        { product: second, quantity: 1 },
      ],
    })

    useCartStore.getState().remove(first.id)
    expect(useCartStore.getState().items).toEqual([{ product: second, quantity: 1 }])

    useCartStore.getState().clear()
    expect(useCartStore.getState().items).toEqual([])
  })

  it('persists only cart items in local storage', () => {
    const item = product()
    useCartStore.getState().add(item)

    const stored = JSON.parse(localStorage.getItem(CART_STORAGE_KEY) ?? '{}') as {
      state?: { items?: unknown[] }
      version?: number
    }

    expect(stored.version).toBe(1)
    expect(stored.state?.items).toEqual([{ product: item, quantity: 1 }])
    expect(Object.keys(stored.state ?? {})).toEqual(['items'])
  })
})
