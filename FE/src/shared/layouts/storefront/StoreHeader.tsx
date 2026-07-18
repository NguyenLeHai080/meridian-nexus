import type { ReactNode } from 'react'
import { Link, NavLink } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import type { AuthenticatedUser } from '@/core/auth/auth.types'
import type { StorefrontSite } from '@/modules/commerce/types/commerce.types'
import { LanguageSwitcher } from '@/shared/components/LanguageSwitcher'

interface StoreHeaderProps {
  site: StorefrontSite
  user: AuthenticatedUser | null
  cartCount: number
}

function getAccountPath(user: AuthenticatedUser | null): string {
  if (user === null) {
    return '/login'
  }

  if (user.permissions.includes('dashboard.view')) {
    return '/admin'
  }

  return '/profile'
}

function getAccountLabel(
  user: AuthenticatedUser | null,
  accountLabel: string,
  signInLabel: string,
): string {
  if (user === null) {
    return signInLabel
  }

  return accountLabel
}

function createNavigation(site: StorefrontSite): ReactNode[] {
  const navigation: ReactNode[] = []

  for (const item of site.navigation) {
    navigation.push(
      <NavLink key={item.path} to={item.path} end={item.path === '/'}>
        {item.label}
      </NavLink>,
    )
  }

  return navigation
}

export function StoreHeader({ site, user, cartCount }: StoreHeaderProps) {
  const { t } = useTranslation()
  const accountPath = getAccountPath(user)
  const accountLabel = getAccountLabel(user, t('account'), t('signIn'))
  const navigation = createNavigation(site)

  return (
    <>
      <div className="announcement">{site.announcement}</div>
      <header className="store-header">
        <Link className="store-logo" to="/">
          <span>{site.brand.mark}</span>
          {site.brand.name}
        </Link>
        <nav>{navigation}</nav>
        <div className="store-actions">
          <LanguageSwitcher />
          <Link to={accountPath}>{accountLabel}</Link>
          <Link to="/checkout">
            {t('bag')} <b>{cartCount}</b>
          </Link>
        </div>
      </header>
    </>
  )
}
