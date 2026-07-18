import type { AuthenticatedUser } from '@/core/auth/auth.types'
import type { Order, Product, Promotion, Post } from '@/modules/commerce/types/commerce.types'

export interface SelectOption<T extends string = string> {
  value: T
  label: string
}

export interface AdminMetadata {
  options: {
    order_statuses: SelectOption[]
    payment_statuses: SelectOption[]
    product_statuses: SelectOption[]
    promotion_types: SelectOption[]
    post_statuses: SelectOption[]
    contact_statuses: SelectOption<ContactMessage['status']>[]
  }
  defaults: {
    order_status: string
    payment_status: string
    product_status: string
    promotion_type: string
    promotion_is_active: boolean
    post_status: string
    contact_status: ContactMessage['status']
  }
  publishing: {
    product_status: string
    post_status: Post['status']
  }
}

export interface DashboardData {
  revenue: number
  orders: number
  pending_orders: number
  products: number
  low_stock_products: number
  customers: number
  open_conversations: number
  recent_orders: Array<
    Pick<Order, 'id' | 'number' | 'customer_name' | 'status' | 'total' | 'created_at'>
  >
}

export interface Role {
  id: number
  name: string
  label: string
  permissions: { id: number; name: string; label: string }[]
}

export interface ContactMessage {
  id: number
  name: string
  email: string
  phone: string | null
  subject: string
  message: string
  status: 'new' | 'in_progress' | 'resolved' | 'spam'
  created_at: string
}

export interface CreateProductInput {
  name: string
  sku: string
  category_id: number | null
  price: number
  sale_price: number | null
  stock: number
  images: string[]
  excerpt: string | null
  description: string | null
  is_featured: boolean
  status: string
  published_at: string | null
}

export interface CreatePromotionInput {
  name: string
  code: string | null
  type: string
  value: number
  minimum_order: number
  starts_at: string | null
  ends_at: string | null
  is_active: boolean
}

export interface CreatePostInput {
  title: string
  slug: string | null
  excerpt: string | null
  content: string
  cover_image: string | null
  status: Post['status']
  published_at: string | null
}

export type UpdateOrderInput = Pick<Order, 'status' | 'payment_status'>
export type AdminUser = AuthenticatedUser
export type AdminProduct = Product
export type AdminPromotion = Promotion
