import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useForgotPassword } from '../hooks/use-auth-mutations'

export function ForgotPasswordPage() {
  const { t } = useTranslation('auth')
  const [email, setEmail] = useState('')
  const request = useForgotPassword()

  return (
    <section className="auth-card">
      <div className="eyebrow">{t('password.eyebrow')}</div>
      <h1>{t('password.forgotTitle')}</h1>
      <p className="auth-card__lead">{t('password.forgotText')}</p>
      <form
        onSubmit={(event) => {
          event.preventDefault()
          request.mutate(email)
        }}
      >
        <label>
          {t('login.email')}
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </label>
        <button className="auth-submit" disabled={request.isPending}>
          {t('password.send')}
        </button>
        {request.isSuccess && <p>{t('password.sent')}</p>}
      </form>
    </section>
  )
}
