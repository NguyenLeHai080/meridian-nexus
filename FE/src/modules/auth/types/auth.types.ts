import type { AuthenticatedUser } from '@/core/auth/auth.types'

export type User = AuthenticatedUser

export interface AuthPayload {
  user: User
}

export interface LoginInput {
  email: string
  password: string
}

export interface RegisterInput extends LoginInput {
  name: string
  password_confirmation: string
}
