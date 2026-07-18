import { Outlet } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { env } from '@/core/config/env'
import { useAuthStore } from '@/core/auth/auth-store'
import { useLogout } from '@/modules/auth/hooks/use-auth-mutations'
import { LanguageSwitcher } from '@/shared/components/LanguageSwitcher'
import { PageLoader } from '@/shared/components/PageLoader'

export function AppLayout() {
  const { t } = useTranslation('common')
  const user = useAuthStore((state) => state.user)
  const logout = useLogout()

  if (user === null) {
    return <PageLoader />
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand__mark">N</span>
          {env.appName}
        </div>
        <nav className="sidebar__nav" aria-label={t('primaryNavigation')}>
          <a className="sidebar__link sidebar__link--active" href="/admin">
            <span>01</span>
            {t('overview')}
          </a>
        </nav>
        <LanguageSwitcher />
        <div className="sidebar__profile">
          <span className="avatar">{user.name.charAt(0).toUpperCase()}</span>
          <div>
            <strong>{user.name}</strong>
            <small>{user.email}</small>
          </div>
          <button type="button" onClick={() => logout.mutate()} aria-label={t('signOut')}>
            ↗
          </button>
        </div>
      </aside>
      <main className="app-content">
        <Outlet />
      </main>
    </div>
  )
}
