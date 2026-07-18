import { apiClient } from '@/core/api/client'
import type { ApiResponse } from '@/core/api/types'
import type {
  Category,
  Conversation,
  Order,
  Post,
  Product,
  Promotion,
} from '@/modules/commerce/types/commerce.types'
import type {
  AdminMetadata,
  AdminUser,
  ContactMessage,
  CreatePostInput,
  CreateProductInput,
  CreatePromotionInput,
  DashboardData,
  Role,
  UpdateOrderInput,
} from '../types/admin.types'

async function getData<T>(url: string): Promise<T> {
  const { data } = await apiClient.get<ApiResponse<T>>(url)
  return data.data
}

export const adminApi = {
  metadata: () => getData<AdminMetadata>('/admin/metadata'),
  dashboard: () => getData<DashboardData>('/admin/dashboard'),
  products: () => getData<Product[]>('/admin/products'),
  createProduct: async (input: CreateProductInput) =>
    (await apiClient.post<ApiResponse<Product>>('/admin/products', input)).data.data,
  categories: () => getData<Category[]>('/admin/categories'),
  createCategory: async (input: { name: string; description?: string }) =>
    (await apiClient.post<ApiResponse<Category>>('/admin/categories', input)).data.data,
  orders: () => getData<Order[]>('/admin/orders'),
  updateOrder: async (id: number, input: UpdateOrderInput) =>
    (await apiClient.patch<ApiResponse<Order>>(`/admin/orders/${id}`, input)).data.data,
  promotions: () => getData<Promotion[]>('/admin/promotions'),
  createPromotion: async (input: CreatePromotionInput) =>
    (await apiClient.post<ApiResponse<Promotion>>('/admin/promotions', input)).data.data,
  users: () => getData<AdminUser[]>('/admin/users'),
  roles: () => getData<Role[]>('/admin/roles'),
  updateRoles: async (userId: number, roles: string[]) =>
    (await apiClient.put<ApiResponse<AdminUser>>(`/admin/users/${userId}/roles`, { roles })).data
      .data,
  conversations: () => getData<Conversation[]>('/admin/conversations'),
  conversation: (id: number) => getData<Conversation>(`/admin/conversations/${id}`),
  reply: async (id: number, message: string) =>
    (await apiClient.post<ApiResponse<Conversation>>(`/admin/conversations/${id}`, { message }))
      .data.data,
  posts: () => getData<Post[]>('/admin/posts'),
  createPost: async (input: CreatePostInput) =>
    (await apiClient.post<ApiResponse<Post>>('/admin/posts', input)).data.data,
  deletePost: async (id: number) => {
    await apiClient.delete(`/admin/posts/${id}`)
  },
  contacts: () => getData<ContactMessage[]>('/admin/contacts'),
  updateContact: async (id: number, status: ContactMessage['status']) =>
    (await apiClient.patch<ApiResponse<ContactMessage>>(`/admin/contacts/${id}`, { status })).data
      .data,
}
