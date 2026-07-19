import { apiClient } from '@/core/api/client'
import type { ApiResponse } from '@/core/api/types'
import type {
  AuthPayload,
  LoginInput,
  LoginPayload,
  MfaConfirmPayload,
  MfaSetupPayload,
  RegisterInput,
  RegisterPayload,
  ResetPasswordInput,
} from '../types/auth.types'

export async function login(input: LoginInput): Promise<LoginPayload> {
  const { data } = await apiClient.post<ApiResponse<LoginPayload>>('/auth/login', input)
  return data.data
}

export async function verifyMfa(challengeToken: string, code: string): Promise<AuthPayload> {
  const { data } = await apiClient.post<ApiResponse<AuthPayload>>('/auth/mfa/challenge', {
    challenge_token: challengeToken,
    code,
  })
  return data.data
}

export async function setupMfa(password: string): Promise<MfaSetupPayload> {
  const { data } = await apiClient.post<ApiResponse<MfaSetupPayload>>('/auth/mfa/setup', {
    password,
  })
  return data.data
}

export async function confirmMfa(code: string): Promise<MfaConfirmPayload> {
  const { data } = await apiClient.post<ApiResponse<MfaConfirmPayload>>('/auth/mfa/confirm', {
    code,
  })
  return data.data
}

export async function register(input: RegisterInput): Promise<RegisterPayload> {
  const { data } = await apiClient.post<ApiResponse<RegisterPayload>>('/auth/register', input)
  return data.data
}

export async function verifyEmail(token: string): Promise<AuthPayload> {
  const { data } = await apiClient.post<ApiResponse<AuthPayload>>('/auth/verify-email', { token })
  return data.data
}

export async function forgotPassword(email: string): Promise<void> {
  await apiClient.post('/auth/forgot-password', { email })
}

export async function resetPassword(input: ResetPasswordInput): Promise<void> {
  await apiClient.post('/auth/reset-password', input)
}

export async function logout(): Promise<void> {
  await apiClient.post('/auth/logout')
}
