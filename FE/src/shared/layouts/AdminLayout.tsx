import { useAuthStore } from '@/core/auth/auth-store'
import { useLogout } from '@/modules/auth/hooks/use-auth-mutations'
import { PageLoader } from '@/shared/components/PageLoader'
import { AdminMain } from './admin/AdminMain'
import { AdminSidebar } from './admin/AdminSidebar'

export function AdminLayout() {
  const user = useAuthStore((state) => state.user)
  const logout = useLogout()

  if (user === null) {
    return <PageLoader />
  }

  function handleLogout() {
    logout.mutate()
  }

  return (
    <div className="admin-shell">
      <AdminSidebar user={user} onLogout={handleLogout} />
      <AdminMain />
    </div>
  )
}
