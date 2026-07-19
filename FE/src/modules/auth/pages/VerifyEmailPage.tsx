import { useSearchParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useVerifyEmail } from '../hooks/use-auth-mutations'

export function VerifyEmailPage() {
  const { t } = useTranslation('auth')
  const [searchParams] = useSearchParams()
  const verification = useVerifyEmail()
  const token = searchParams.get('token')

  return (
    <section className="auth-card">
      <div className="eyebrow">{t('verification.eyebrow')}</div>
      <h1>{t('verification.title')}</h1>
      <p className="auth-card__lead">{t('verification.text')}</p>
      <button
        className="auth-submit"
        disabled={token === null || verification.isPending}
        onClick={() => {
          if (token !== null) {
            verification.mutate(token)
          }
        }}
      >
        {t('verification.submit')}
      </button>
    </section>
  )
}
