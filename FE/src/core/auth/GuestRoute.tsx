import { Navigate, Outlet } from 'react-router-dom'
import { useAuthStore } from './auth-store'
import { getPostLoginPath } from './auth-navigation'

export function GuestRoute() {
  const user = useAuthStore((state) => state.user)

  if (user !== null) {
    return <Navigate to={getPostLoginPath(user)} replace />
  }

  return <Outlet />
}
