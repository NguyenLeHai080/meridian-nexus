import type { AuthenticatedUser } from './auth.types'

export function getPostLoginPath(user: AuthenticatedUser): '/admin' | '/profile' {
  const isPrivileged = user.roles.includes('admin') || user.roles.includes('manager')
  if (isPrivileged && !user.mfa_enabled) {
    return '/profile'
  }
  if (user.permissions.includes('dashboard.view')) {
    return '/admin'
  }

  return '/profile'
}
