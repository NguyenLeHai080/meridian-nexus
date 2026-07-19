import type { AuthenticatedUser } from '@/core/auth/auth.types'

export type User = AuthenticatedUser

export interface AuthPayload {
  user: User
}

export interface LoginPayload {
  user: User | null
  mfa_required: boolean
  challenge_token: string | null
}

export interface RegisterPayload {
  user: User | null
  verification_required: boolean
}

export interface LoginInput {
  email: string
  password: string
}

export interface RegisterInput extends LoginInput {
  name: string
  password_confirmation: string
}

export interface ResetPasswordInput {
  token: string
  email: string
  password: string
  password_confirmation: string
}

export interface MfaSetupPayload {
  secret: string
  provisioning_uri: string
}

export interface MfaConfirmPayload {
  user: User
  recovery_codes: string[]
}
