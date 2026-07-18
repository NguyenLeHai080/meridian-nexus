import type { AuthenticatedUser } from './auth.types'

export function getPostLoginPath(user: AuthenticatedUser): '/admin' | '/profile' {
  if (user.permissions.includes('dashboard.view')) {
    return '/admin'
  }

  return '/profile'
}
