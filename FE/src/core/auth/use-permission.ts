import { useAuthStore } from './auth-store'

export function usePermission(permission: string): boolean {
  return useAuthStore((state) => state.user?.permissions.includes(permission) ?? false)
}

export function usePermissions(): string[] {
  return useAuthStore((state) => state.user?.permissions ?? [])
}
