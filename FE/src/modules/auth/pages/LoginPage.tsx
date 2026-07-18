import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { LoginForm } from '../components/LoginForm'

export function LoginPage() {
  const { t } = useTranslation('auth')
  return (
    <section className="auth-card">
      <div className="eyebrow">{t('login.eyebrow')}</div>
      <h1>{t('login.title')}</h1>
      <p className="auth-card__lead">{t('login.lead')}</p>
      <LoginForm />
      <p className="auth-card__switch">
        {t('login.newHere')} <Link to="/register">{t('login.createAccount')}</Link>
      </p>
    </section>
  )
}
