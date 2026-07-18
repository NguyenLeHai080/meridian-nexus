import { Outlet } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { env } from '@/core/config/env'
import { LanguageSwitcher } from '@/shared/components/LanguageSwitcher'

export function AuthLayout() {
  const { t } = useTranslation('auth')

  return (
    <main className="auth-shell">
      <aside className="auth-story">
        <div className="brand">
          <span className="brand__mark">N</span>
          {env.appName}
        </div>
        <div className="auth-story__copy">
          <span>{t('layout.eyebrow')}</span>
          <h2>
            {t('layout.titleLine1')}
            <br />
            {t('layout.titleLine2')}
          </h2>
          <p>{t('layout.description')}</p>
        </div>
        <div className="auth-story__grid" aria-hidden="true" />
      </aside>
      <div className="auth-panel">
        <div className="auth-language">
          <LanguageSwitcher />
        </div>
        <Outlet />
      </div>
    </main>
  )
}
