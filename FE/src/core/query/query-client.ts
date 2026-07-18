import { QueryClient } from '@tanstack/react-query'
import { ApiError } from '@/core/api/errors'

function shouldRetry(failureCount: number, error: unknown): boolean {
  if (error instanceof ApiError && error.status !== null && error.status < 500) {
    return false
  }

  return failureCount < 2
}

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: shouldRetry,
      staleTime: 30_000,
    },
    mutations: {
      retry: false,
    },
  },
})
