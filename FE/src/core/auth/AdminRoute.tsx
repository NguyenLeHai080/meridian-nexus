import { Navigate, Outlet } from 'react-router-dom'
import { useAuthStore } from './auth-store'

export function AdminRoute() {
  const user = useAuthStore((state) => state.user)

  if (user !== null && user.permissions.includes('dashboard.view')) {
    return <Outlet />
  }

  return <Navigate to="/profile" replace />
}
