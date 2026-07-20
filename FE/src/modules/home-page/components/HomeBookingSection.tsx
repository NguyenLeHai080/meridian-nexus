import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

export function HomeBookingSection() {
  const { t } = useTranslation('storefront')

  return (
    <section className="nail-booking" data-nail-reveal>
      <img src="/nail-assets/Sixthsense_Logo_thumbnail_2.svg" alt="" />
      <p>{t('homePage.booking.intro')}</p>
      <h2>{t('homePage.booking.title')}</h2>
      <div className="nail-actions">
        <Link className="nail-button nail-button--light" to="/contact">
          {t('homePage.booking.appointment')}
        </Link>
        <Link className="nail-button nail-button--light" to="/contact">
          {t('homePage.booking.call')}
        </Link>
      </div>
    </section>
  )
}
