import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

export function VerifyEmailSentPage() {
  const { t } = useTranslation('auth')
  return (
    <section className="auth-card">
      <div className="eyebrow">{t('verification.eyebrow')}</div>
      <h1>{t('verification.sentTitle')}</h1>
      <p className="auth-card__lead">{t('verification.sentText')}</p>
      <Link to="/login">{t('verification.backToLogin')}</Link>
    </section>
  )
}
