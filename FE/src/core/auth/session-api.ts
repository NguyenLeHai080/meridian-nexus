import { apiClient } from '@/core/api/client'
import type { ApiResponse } from '@/core/api/types'
import type { AuthenticatedUser } from './auth.types'

export interface AuthSession {
  authenticated: boolean
  user: AuthenticatedUser | null
}

let bootstrapRequest: Promise<AuthSession> | null = null

export function getAuthSession(): Promise<AuthSession> {
  if (!bootstrapRequest) {
    bootstrapRequest = apiClient
      .get<ApiResponse<AuthSession>>('/auth/session')
      .then(({ data }) => data.data)
      .catch((error: unknown) => {
        bootstrapRequest = null
        throw error
      })
  }

  return bootstrapRequest
}

export async function getCurrentUser(): Promise<AuthenticatedUser> {
  const { data } = await apiClient.get<ApiResponse<AuthenticatedUser>>('/auth/me')
  return data.data
}
