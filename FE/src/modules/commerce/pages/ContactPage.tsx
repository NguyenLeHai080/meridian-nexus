import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useSendContact } from '../hooks/use-commerce-data'

export function ContactPage() {
  const { t } = useTranslation('storefront')
  const [sent, setSent] = useState(false)
  const mutation = useSendContact(() => setSent(true))
  let formContent = (
    <>
      <label>
        {t('contact.name')}
        <input name="name" required />
      </label>
      <label>
        {t('contact.email')}
        <input name="email" type="email" required />
      </label>
      <label>
        {t('contact.phone')}
        <input name="phone" />
      </label>
      <label>
        {t('contact.subject')}
        <input name="subject" required />
      </label>
      <label>
        {t('contact.message')}
        <textarea name="message" rows={6} required />
      </label>
      <button className="store-button" disabled={mutation.isPending}>
        {t('contact.send')}
      </button>
    </>
  )

  if (sent) {
    formContent = (
      <div className="contact-success">
        <span>OK</span>
        <h2>{t('contact.received')}</h2>
        <p>{t('contact.replySoon')}</p>
      </div>
    )
  }

  return (
    <section className="contact-page">
      <div>
        <span className="store-kicker">{t('contact.eyebrow')}</span>
        <h1>{t('contact.title')}</h1>
        <p>{t('contact.intro')}</p>
        <dl>
          <dt>{t('contact.email')}</dt>
          <dd>hello@northstar.test</dd>
          <dt>{t('contact.studio')}</dt>
          <dd>{t('contact.studioAddress')}</dd>
          <dt>{t('contact.hours')}</dt>
          <dd>{t('contact.hoursValue')}</dd>
        </dl>
      </div>
      <form
        onSubmit={(event) => {
          event.preventDefault()
          mutation.mutate(
            Object.fromEntries(new FormData(event.currentTarget)) as Record<string, string>,
          )
        }}
      >
        {formContent}
      </form>
    </section>
  )
}
