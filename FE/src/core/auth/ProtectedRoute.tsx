import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuthStore } from './auth-store'

export function ProtectedRoute() {
  const user = useAuthStore((state) => state.user)
  const location = useLocation()

  if (user === null) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  return <Outlet />
}
