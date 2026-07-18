import type { ReactNode } from 'react'
import { NavLink } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import type { AuthenticatedUser } from '@/core/auth/auth.types'
import { LanguageSwitcher } from '@/shared/components/LanguageSwitcher'
import { useAdminLabel } from '@/modules/admin/hooks/use-admin-label'

interface AdminSidebarProps {
  user: AuthenticatedUser
  onLogout: () => void
}

interface AdminNavigationItem {
  path: string
  labelKey: string
  permission: string
}

const navigationItems: AdminNavigationItem[] = [
  { path: '/admin', labelKey: 'sidebar.overview', permission: 'dashboard.view' },
  { path: '/admin/products', labelKey: 'sidebar.products', permission: 'products.view' },
  { path: '/admin/orders', labelKey: 'sidebar.orders', permission: 'orders.view' },
  { path: '/admin/promotions', labelKey: 'sidebar.promotions', permission: 'promotions.view' },
  { path: '/admin/content', labelKey: 'sidebar.content', permission: 'content.manage' },
  { path: '/admin/users', labelKey: 'sidebar.users', permission: 'users.view' },
  { path: '/admin/chat', labelKey: 'sidebar.conversations', permission: 'chat.view' },
]

function createNavigation(
  user: AuthenticatedUser,
  translate: (key: string) => string,
): ReactNode[] {
  const navigation: ReactNode[] = []
  let visibleIndex = 0

  for (const item of navigationItems) {
    if (!user.permissions.includes(item.permission)) {
      continue
    }

    visibleIndex += 1
    navigation.push(
      <NavLink key={item.path} to={item.path} end={item.path === '/admin'}>
        <span>0{visibleIndex}</span>
        {translate(item.labelKey)}
      </NavLink>,
    )
  }

  return navigation
}

export function AdminSidebar({ user, onLogout }: AdminSidebarProps) {
  const { t } = useTranslation('admin')
  const label = useAdminLabel()
  const navigation = createNavigation(user, t)
  const roleLabels: string[] = []

  for (const role of user.roles) {
    roleLabels.push(label('role', role))
  }

  return (
    <aside className="admin-sidebar">
      <div className="admin-sidebar__top">
        <div className="admin-brand">
          <span>N</span>
          <div>
            Northstar<small>{t('sidebar.office')}</small>
          </div>
        </div>
        <LanguageSwitcher />
      </div>
      <nav>{navigation}</nav>
      <a className="admin-store-link" href="/">
        {t('sidebar.storefront')}
      </a>
      <div className="admin-user">
        <div>{user.name.charAt(0)}</div>
        <span>
          <strong>{user.name}</strong>
          <small>{roleLabels.join(', ')}</small>
        </span>
        <button aria-label={t('sidebar.signOut')} onClick={onLogout}>
          {t('sidebar.out')}
        </button>
      </div>
    </aside>
  )
}
