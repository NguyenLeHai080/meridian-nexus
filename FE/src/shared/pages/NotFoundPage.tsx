import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

export function NotFoundPage() {
  const { t } = useTranslation('common')

  return (
    <main className="not-found">
      <span>404</span>
      <h1>{t('notFoundTitle')}</h1>
      <Link to="/">{t('returnHome')}</Link>
    </main>
  )
}
