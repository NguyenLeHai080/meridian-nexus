import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import { queryKeys } from '@/core/query/query-keys'
import {
  checkout,
  getChat,
  getCustomerOrders,
  getPost,
  getPosts,
  getProduct,
  getProducts,
  getStorefrontHome,
  replyChat,
  sendContact,
  startChat,
} from '../api/commerce.api'

export const useStorefrontHome = () => {
  const { i18n } = useTranslation()
  const language = i18n.resolvedLanguage || i18n.language || 'en'

  return useQuery({
    queryKey: queryKeys.commerce.home(language),
    queryFn: getStorefrontHome,
    placeholderData: keepPreviousData,
  })
}

function useActiveLanguage(): string {
  const { i18n } = useTranslation()
  return i18n.resolvedLanguage || i18n.language || 'en'
}

export const useProducts = (params: { search?: string; category?: string }) => {
  const language = useActiveLanguage()
  return useQuery({
    queryKey: queryKeys.commerce.products(language, params),
    queryFn: () => getProducts(params),
    placeholderData: keepPreviousData,
  })
}

export const useProduct = (slug?: string) => {
  const language = useActiveLanguage()
  return useQuery({
    queryKey: queryKeys.commerce.product(language, slug),
    queryFn: () => getProduct(slug!),
    enabled: Boolean(slug),
    placeholderData: keepPreviousData,
  })
}

export const usePosts = () => {
  const language = useActiveLanguage()
  return useQuery({
    queryKey: queryKeys.commerce.posts(language),
    queryFn: getPosts,
    placeholderData: keepPreviousData,
  })
}

export const usePost = (slug?: string) => {
  const language = useActiveLanguage()
  return useQuery({
    queryKey: queryKeys.commerce.post(language, slug),
    queryFn: () => getPost(slug!),
    enabled: Boolean(slug),
    placeholderData: keepPreviousData,
  })
}

export const useCustomerOrders = () =>
  useQuery({ queryKey: queryKeys.commerce.customerOrders, queryFn: getCustomerOrders })

export const useSendContact = (onSent?: () => void) =>
  useMutation({ mutationFn: sendContact, onSuccess: onSent })

export const useCheckout = (onCompleted?: () => void) => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: checkout,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.commerce.customerOrders })
      onCompleted?.()
    },
  })
}

export const useChatConversation = (token: string | null, enabled: boolean) =>
  useQuery({
    queryKey: queryKeys.commerce.chat(token),
    queryFn: () => getChat(token!),
    enabled: Boolean(token && enabled),
    refetchInterval: 8_000,
  })

export function useSendChatMessage(token: string | null) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (input: { message: string; guest?: { name: string; email: string } }) => {
      if (token !== null) {
        return replyChat(token, input.message)
      }

      return startChat({ ...input.guest, message: input.message })
    },
    onSuccess: (conversation) => {
      queryClient.setQueryData(queryKeys.commerce.chat(conversation.token), conversation)
    },
  })
}
