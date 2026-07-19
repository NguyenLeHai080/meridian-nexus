import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { queryKeys } from '@/core/query/query-keys'
import { adminApi } from '../api/admin.api'
import type {
  ContactMessage,
  CreatePostInput,
  CreateProductInput,
  CreatePromotionInput,
  UpdateOrderInput,
} from '../types/admin.types'

const adminListStaleTime = 2 * 60 * 1000

export const useAdminMetadata = (enabled = true) =>
  useQuery({
    queryKey: queryKeys.admin.metadata,
    queryFn: adminApi.metadata,
    staleTime: Infinity,
    enabled,
  })

export const useAdminDashboard = () =>
  useQuery({
    queryKey: queryKeys.admin.dashboard,
    queryFn: adminApi.dashboard,
    staleTime: 60_000,
  })

export const useAdminProducts = (page: number) =>
  useQuery({
    queryKey: queryKeys.admin.products(page),
    queryFn: () => adminApi.products(page),
    staleTime: adminListStaleTime,
  })

export const useAdminCategories = (enabled = true) =>
  useQuery({
    queryKey: queryKeys.admin.categories,
    queryFn: adminApi.categories,
    staleTime: adminListStaleTime,
    enabled,
  })

export function useCreateProduct(onCreated?: () => void) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (input: CreateProductInput) => adminApi.createProduct(input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.products() })
      onCreated?.()
    },
  })
}

export function useCreateCategory(onCreated?: () => void) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: adminApi.createCategory,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.categories })
      onCreated?.()
    },
  })
}

export const useAdminOrders = (page: number) =>
  useQuery({
    queryKey: queryKeys.admin.orders(page),
    queryFn: () => adminApi.orders(page),
    staleTime: adminListStaleTime,
  })

export function useUpdateOrder() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, input }: { id: number; input: UpdateOrderInput }) =>
      adminApi.updateOrder(id, input),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.admin.orders() }),
  })
}

export const useAdminPromotions = () =>
  useQuery({
    queryKey: queryKeys.admin.promotions,
    queryFn: adminApi.promotions,
    staleTime: adminListStaleTime,
  })

export function useCreatePromotion(onCreated?: () => void) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (input: CreatePromotionInput) => adminApi.createPromotion(input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.promotions })
      onCreated?.()
    },
  })
}

export const useAdminUsers = (page: number) =>
  useQuery({
    queryKey: queryKeys.admin.users(page),
    queryFn: () => adminApi.users(page),
    staleTime: adminListStaleTime,
  })

export const useAdminRoles = () =>
  useQuery({ queryKey: queryKeys.admin.roles, queryFn: adminApi.roles, staleTime: Infinity })

export function useUpdateUserRoles() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, roles }: { id: number; roles: string[] }) => adminApi.updateRoles(id, roles),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.admin.users() }),
  })
}

export const useAdminConversations = (page: number) =>
  useQuery({
    queryKey: queryKeys.admin.conversations(page),
    queryFn: () => adminApi.conversations(page),
    staleTime: 30_000,
    refetchInterval: 30_000,
  })

export const useAdminConversation = (id: number | null) =>
  useQuery({
    queryKey: queryKeys.admin.conversation(id),
    queryFn: () => adminApi.conversation(id!),
    enabled: id !== null,
  })

export function useReplyToConversation(id: number | null) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (message: string) => adminApi.reply(id!, message),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.admin.conversations() }),
  })
}

export const useAdminPosts = (page: number, enabled = true) =>
  useQuery({
    queryKey: queryKeys.admin.posts(page),
    queryFn: () => adminApi.posts(page),
    staleTime: adminListStaleTime,
    enabled,
  })

export const useAdminContacts = (page: number, enabled = true) =>
  useQuery({
    queryKey: queryKeys.admin.contacts(page),
    queryFn: () => adminApi.contacts(page),
    staleTime: 60_000,
    enabled,
  })

export function useCreatePost(onCreated?: () => void) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (input: CreatePostInput) => adminApi.createPost(input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.posts() })
      onCreated?.()
    },
  })
}

export function useDeletePost() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: adminApi.deletePost,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.admin.posts() }),
  })
}

export function useUpdateContact() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, status }: { id: number; status: ContactMessage['status'] }) =>
      adminApi.updateContact(id, status),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.admin.contacts() }),
  })
}
