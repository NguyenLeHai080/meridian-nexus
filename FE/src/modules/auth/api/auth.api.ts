import { apiClient } from '@/core/api/client'
import type { ApiResponse } from '@/core/api/types'
import type { AuthPayload, LoginInput, RegisterInput } from '../types/auth.types'

export async function login(input: LoginInput): Promise<AuthPayload> {
  const { data } = await apiClient.post<ApiResponse<AuthPayload>>('/auth/login', input)
  return data.data
}

export async function register(input: RegisterInput): Promise<AuthPayload> {
  const { data } = await apiClient.post<ApiResponse<AuthPayload>>('/auth/register', input)
  return data.data
}

export async function logout(): Promise<void> {
  await apiClient.post('/auth/logout')
}
