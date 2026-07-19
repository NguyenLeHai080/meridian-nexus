import { apiClient } from '@/core/api/client'
import type { ApiResponse, PaginatedResult, PaginationMeta } from '@/core/api/types'
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

async function getPage<T>(url: string, page: number): Promise<PaginatedResult<T>> {
  const { data } = await apiClient.get<ApiResponse<T[]> & PaginationMeta>(url, {
    params: { page, per_page: 25 },
  })
  const meta = data.meta as PaginationMeta | undefined
  if (meta === undefined) {
    throw new Error('Paginated API response is missing pagination metadata')
  }
  return { items: data.data, pagination: meta.pagination }
}

export const adminApi = {
  metadata: () => getData<AdminMetadata>('/admin/metadata'),
  dashboard: () => getData<DashboardData>('/admin/dashboard'),
  products: (page: number) => getPage<Product>('/admin/products', page),
  createProduct: async (input: CreateProductInput) =>
    (await apiClient.post<ApiResponse<Product>>('/admin/products', input)).data.data,
  categories: () => getData<Category[]>('/admin/categories'),
  createCategory: async (input: { name: string; description?: string }) =>
    (await apiClient.post<ApiResponse<Category>>('/admin/categories', input)).data.data,
  orders: (page: number) => getPage<Order>('/admin/orders', page),
  updateOrder: async (id: number, input: UpdateOrderInput) =>
    (await apiClient.patch<ApiResponse<Order>>(`/admin/orders/${id}`, input)).data.data,
  promotions: () => getData<Promotion[]>('/admin/promotions'),
  createPromotion: async (input: CreatePromotionInput) =>
    (await apiClient.post<ApiResponse<Promotion>>('/admin/promotions', input)).data.data,
  users: (page: number) => getPage<AdminUser>('/admin/users', page),
  roles: () => getData<Role[]>('/admin/roles'),
  updateRoles: async (userId: number, roles: string[]) =>
    (await apiClient.put<ApiResponse<AdminUser>>(`/admin/users/${userId}/roles`, { roles })).data
      .data,
  conversations: (page: number) => getPage<Conversation>('/admin/conversations', page),
  conversation: (id: number) => getData<Conversation>(`/admin/conversations/${id}`),
  reply: async (id: number, message: string) =>
    (await apiClient.post<ApiResponse<Conversation>>(`/admin/conversations/${id}`, { message }))
      .data.data,
  posts: (page: number) => getPage<Post>('/admin/posts', page),
  createPost: async (input: CreatePostInput) =>
    (await apiClient.post<ApiResponse<Post>>('/admin/posts', input)).data.data,
  deletePost: async (id: number) => {
    await apiClient.delete(`/admin/posts/${id}`)
  },
  contacts: (page: number) => getPage<ContactMessage>('/admin/contacts', page),
  updateContact: async (id: number, status: ContactMessage['status']) =>
    (await apiClient.patch<ApiResponse<ContactMessage>>(`/admin/contacts/${id}`, { status })).data
      .data,
}
