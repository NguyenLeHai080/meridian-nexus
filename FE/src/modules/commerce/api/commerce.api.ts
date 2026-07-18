import { apiClient, createIdempotencyKey } from '@/core/api/client'
import type { ApiResponse, PaginationMeta } from '@/core/api/types'
import type { Conversation, Order, Post, Product, StorefrontHome } from '../types/commerce.types'

export async function getStorefrontHome(): Promise<StorefrontHome> {
  const { data } = await apiClient.get<ApiResponse<StorefrontHome>>('/storefront/home')
  return data.data
}

export async function getProducts(params?: {
  search?: string
  category?: string
}): Promise<{ data: Product[]; meta: PaginationMeta }> {
  const { data } = await apiClient.get<ApiResponse<Product[]> & { meta: PaginationMeta }>(
    '/storefront/products',
    { params },
  )
  return { data: data.data, meta: data.meta }
}

export async function getProduct(slug: string): Promise<Product> {
  const { data } = await apiClient.get<ApiResponse<Product>>(`/storefront/products/${slug}`)
  return data.data
}

export async function getPosts(): Promise<Post[]> {
  const { data } = await apiClient.get<ApiResponse<Post[]>>('/storefront/posts')
  return data.data
}

export async function getPost(slug: string): Promise<Post> {
  const { data } = await apiClient.get<ApiResponse<Post>>(`/storefront/posts/${slug}`)
  return data.data
}

export async function sendContact(input: Record<string, string>): Promise<void> {
  await apiClient.post('/storefront/contact', input)
}

export async function getCustomerOrders(): Promise<Order[]> {
  const { data } = await apiClient.get<ApiResponse<Order[]>>('/customer/orders')
  return data.data
}

export async function checkout(input: {
  items: { product_id: number; quantity: number }[]
  phone: string
  address: { line: string; city: string; country: string }
  promotion_code?: string
}): Promise<Order> {
  const { data } = await apiClient.post<ApiResponse<Order>>('/customer/orders', input, {
    headers: { 'Idempotency-Key': createIdempotencyKey() },
  })
  return data.data
}

export async function startChat(input: {
  name?: string
  email?: string
  message: string
}): Promise<Conversation> {
  const { data } = await apiClient.post<ApiResponse<Conversation>>('/storefront/chat', input)
  return data.data
}

export async function getChat(token: string): Promise<Conversation> {
  const { data } = await apiClient.get<ApiResponse<Conversation>>(`/storefront/chat/${token}`)
  return data.data
}

export async function replyChat(token: string, message: string): Promise<Conversation> {
  const { data } = await apiClient.post<ApiResponse<Conversation>>(`/storefront/chat/${token}`, {
    message,
  })
  return data.data
}
