import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useResetPassword } from '../hooks/use-auth-mutations'

export function ResetPasswordPage() {
  const { t } = useTranslation('auth')
  const [searchParams] = useSearchParams()
  const [password, setPassword] = useState('')
  const [confirmation, setConfirmation] = useState('')
  const reset = useResetPassword()
  const token = searchParams.get('token') || ''
  const email = searchParams.get('email') || ''

  if (reset.isSuccess) {
    return (
      <section className="auth-card">
        <h1>{t('password.completeTitle')}</h1>
        <p className="auth-card__lead">{t('password.completeText')}</p>
        <Link to="/login">{t('password.signIn')}</Link>
      </section>
    )
  }

  return (
    <section className="auth-card">
      <div className="eyebrow">{t('password.eyebrow')}</div>
      <h1>{t('password.resetTitle')}</h1>
      <form
        onSubmit={(event) => {
          event.preventDefault()
          reset.mutate({ token, email, password, password_confirmation: confirmation })
        }}
      >
        <label>
          {t('register.password')}
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            minLength={12}
            required
          />
        </label>
        <label>
          {t('register.confirmPassword')}
          <input
            type="password"
            value={confirmation}
            onChange={(event) => setConfirmation(event.target.value)}
            minLength={12}
            required
          />
        </label>
        <button className="auth-submit" disabled={!token || !email || reset.isPending}>
          {t('password.reset')}
        </button>
      </form>
    </section>
  )
}
