export interface AuthenticatedUser {
  id: number
  name: string
  email: string
  email_verified_at: string | null
  mfa_enabled: boolean
  created_at: string
  roles: string[]
  permissions: string[]
}
