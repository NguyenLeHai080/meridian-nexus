import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { RegisterForm } from '../components/RegisterForm'

export function RegisterPage() {
  const { t } = useTranslation('auth')
  return (
    <section className="auth-card">
      <div className="eyebrow">{t('register.eyebrow')}</div>
      <h1>{t('register.title')}</h1>
      <p className="auth-card__lead">{t('register.lead')}</p>
      <RegisterForm />
      <p className="auth-card__switch">
        {t('register.already')} <Link to="/login">{t('register.signIn')}</Link>
      </p>
    </section>
  )
}
