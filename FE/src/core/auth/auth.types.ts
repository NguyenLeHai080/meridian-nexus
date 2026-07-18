export interface AuthenticatedUser {
  id: number
  name: string
  email: string
  email_verified_at: string | null
  created_at: string
  roles: string[]
  permissions: string[]
}
