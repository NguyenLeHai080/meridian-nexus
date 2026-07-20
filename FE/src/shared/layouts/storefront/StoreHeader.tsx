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

function SearchIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="11" cy="11" r="6.5" />
      <path d="m16 16 4 4" />
    </svg>
  )
}

function AccountIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="12" cy="8" r="3.5" />
      <path d="M5.5 20c.5-4 2.7-6 6.5-6s6 2 6.5 6" />
    </svg>
  )
}

function CalendarIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M6.5 3.5v3M17.5 3.5v3M4 9h16M5.5 5h13A1.5 1.5 0 0 1 20 6.5v12a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 4 18.5v-12A1.5 1.5 0 0 1 5.5 5Z" />
      <path d="m9 14 2 2 4-4" />
    </svg>
  )
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

export function StoreHeader({ site, user, cartCount }: StoreHeaderProps) {
  const { t } = useTranslation(['common', 'storefront'])
  const accountPath = getAccountPath(user)
  const accountLabel = getAccountLabel(user, t('account'), t('signIn'))
  void site
  void cartCount

  return (
    <>
      <div className="announcement">{site.announcement}</div>
      <header className="store-header">
        <Link className="store-logo" to="/">
          <img src="/nail-assets/Sixthsense_Logo_thumbnail_2.svg" alt="" />
          <strong>
            MERIDIAN NEXUS<small>DIGITAL STUDIO & AI SOLUTIONS</small>
          </strong>
        </Link>
        <nav>
          <NavLink to="/" end>
            {t('storefront:homePage.navigation.home')}
          </NavLink>
          <NavLink to="/about">{t('storefront:homePage.navigation.about')}</NavLink>
          <NavLink to="/contact">{t('storefront:homePage.navigation.visit')}</NavLink>
          <NavLink to="/products">{t('storefront:homePage.navigation.shop')}</NavLink>
          <NavLink to="/contact">{t('storefront:homePage.navigation.sip')}</NavLink>
          <NavLink to="/contact">{t('storefront:homePage.navigation.contact')}</NavLink>
        </nav>
        <div className="store-actions">
          <LanguageSwitcher />
          <Link
            className="header-search"
            to="/products"
            aria-label={t('storefront:homePage.actions.search')}
          >
            <SearchIcon />
          </Link>
          <Link className="header-account" to={accountPath} aria-label={accountLabel}>
            <AccountIcon />
          </Link>
          <Link className="header-booking" to="/contact">
            <CalendarIcon />
            <span>{t('storefront:homePage.actions.bookNow')}</span>
          </Link>
        </div>
      </header>
    </>
  )
}
