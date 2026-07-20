import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useStorefrontHome } from '@/modules/commerce/hooks/use-commerce-data'
import { HomeBookingSection } from '../components/HomeBookingSection'
import { useHomeReveal } from '../hooks/use-home-reveal'

const services = [
  ['manicures', 'Nail_care.svg', 'mani_Icon.svg'],
  ['pedicures', 'pedi_icon.svg', 'Pedi_1.svg'],
  ['manicurePedicure', 'mani_and_pedi.png', 'mani_and_pedi_1.png'],
  ['shellac', 'shellac_icon.svg', 'shellac_front.svg'],
  ['artificialNails', 'Nails_Cutting.svg', 'nail_enhance.svg'],
  ['dippingPowders', 'nail_enhance.svg', 'dip_powers_icon_.svg'],
] as const

const heroSlides = [
  ['healing', 'spa-girl-4.png'],
  ['care', 'spa-girl-1.png'],
] as const

const packages = [
  ['website', 'NUGENESIS.jpeg'],
  ['wordpress', 'MASSAGE03.jpeg'],
  ['automation', 'FACIAL03.jpeg'],
  ['aiCreative', 'MANICURE-PEDICURE.jpeg'],
] as const

export function HomePage() {
  const { t } = useTranslation('storefront')
  const { data } = useStorefrontHome()
  const [heroSlide, setHeroSlide] = useState(0)
  const [serviceSlide, setServiceSlide] = useState(0)
  useHomeReveal()

  useEffect(() => {
    const timer = window.setInterval(() => setHeroSlide((current) => (current + 1) % 2), 6000)
    return () => window.clearInterval(timer)
  }, [])

  useEffect(() => {
    const timer = window.setInterval(
      () => setServiceSlide((current) => (current + 1) % services.length),
      5000,
    )
    return () => window.clearInterval(timer)
  }, [])

  if (data === undefined) return null

  return (
    <div className="nail-home nail-original">
      <section className="nail-hero nail-hero--original">
        <div className="nail-hero__content" key={`copy-${heroSlide}`}>
          <p className="nail-hero__brand">{t('homePage.hero.brand')}</p>
          <h1>{t(`homePage.hero.slides.${heroSlides[heroSlide][0]}`)}</h1>
          <Link className="nail-button nail-button--outline" to="/contact">
            {t('homePage.actions.bookAppointments')}
          </Link>
        </div>
        <div className="nail-hero__model" key={`model-${heroSlide}`}>
          <span className="nail-hero__shape" />
          <img src={`/nail-assets/${heroSlides[heroSlide][1]}`} alt={t('homePage.images.hero')} />
        </div>
      </section>

      <section className="nail-about" data-nail-reveal>
        <div className="nail-about__photos">
          <img src="/nail-assets/TNV_6015.jpg" alt={t('homePage.images.salon')} />
          <img src="/nail-assets/nail_recep.jpg" alt={t('homePage.images.reception')} />
          <img src="/nail-assets/TNV_6063.jpg" alt={t('homePage.images.treatment')} />
        </div>
        <div className="nail-about__content">
          <p className="nail-kicker">
            {t('homePage.about.kickerBefore')} <strong>{t('homePage.about.kickerStrong')}</strong>{' '}
            {t('homePage.about.kickerAfter')}
          </p>
          <h2>{t('homePage.about.title')}</h2>
          <p>{t('homePage.about.paragraph1')}</p>
          <p>{t('homePage.about.paragraph2')}</p>
          <div className="nail-actions">
            <Link className="nail-button nail-button--outline" to="/about">
              {t('homePage.actions.ourService')}
            </Link>
            <Link className="nail-button nail-button--outline" to="/contact">
              {t('homePage.actions.makeCall')}
            </Link>
          </div>
        </div>
        <img className="nail-about__leaf" src="/nail-assets/leaf-icon.png" alt="" />
      </section>

      <section className="nail-services" id="services" data-nail-reveal>
        <header className="nail-section-heading">
          <h2>
            {t('homePage.services.eyebrow')} <span>{t('homePage.services.title')}</span>
          </h2>
          <p>{t('homePage.services.intro')}</p>
        </header>
        <div className="nail-service-viewport">
          <div
            className="nail-service-grid"
            style={{ transform: `translateX(-${serviceSlide * 330}px)` }}
          >
            {[...services, ...services].map(([service, backgroundIcon, frontIcon], index) => (
              <article key={`${service}-${index}`}>
                <div className="nail-service-icon">
                  <img
                    className="nail-service-icon__background"
                    src={`/nail-assets/${backgroundIcon}`}
                    alt=""
                  />
                  <span>
                    <img src={`/nail-assets/${frontIcon}`} alt="" />
                  </span>
                </div>
                <h3>{t(`homePage.services.items.${service}.title`)}</h3>
                <p>{t(`homePage.services.items.${service}.text`)}</p>
                <Link to="/products">{t('homePage.actions.readMore')}</Link>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="nail-quality" data-nail-reveal>
        <div>
          <p className="nail-kicker">{t('homePage.quality.kicker')}</p>
          <h2>{t('homePage.quality.title')}</h2>
          <p>{t('homePage.quality.text')}</p>
          <Link className="nail-button nail-button--dark" to="/contact">
            {t('homePage.actions.bookAppointments')}
          </Link>
        </div>
        <div className="nail-quality__offers">
          <article className="nail-offer nail-offer--foundation" data-nail-tilt>
            <div>
              <span>{t('homePage.quality.foundation')}</span>
              <strong>{t('homePage.quality.naturalTone')}</strong>
              <Link to="/products">{t('homePage.actions.shopNow')}</Link>
            </div>
          </article>
          <article className="nail-offer nail-offer--cosmetic" data-nail-tilt>
            <div>
              <span>{t('homePage.quality.cosmetic')}</span>
              <strong>{t('homePage.quality.floralCream')}</strong>
              <Link to="/products">{t('homePage.actions.shopNow')}</Link>
            </div>
          </article>
        </div>
      </section>

      <section className="nail-story" data-nail-reveal>
        <div className="nail-story__copy">
          <p className="nail-kicker">
            {t('homePage.story.kickerBefore')} <strong>{t('homePage.story.kickerStrong')}</strong>{' '}
            {t('homePage.story.kickerAfter')}
          </p>
          <h2>
            {t('homePage.story.title')} <span>{t('homePage.story.accent')}</span>
          </h2>
          <p>{t('homePage.story.text')}</p>
          <div className="nail-story__tiles">
            <span>
              <strong data-nail-count="50">0</strong>
              {t('homePage.story.capacity')}
            </span>
            <span>
              <strong data-nail-count="24">0</strong>
              {t('homePage.story.squareFoot')}
            </span>
          </div>
        </div>
        <div className="nail-story__image" data-nail-tilt>
          <img src="/nail-assets/homepage_be_yourself_party.jpg" alt={t('homePage.images.event')} />
        </div>
        <img className="nail-story__leaf" src="/nail-assets/leaf-icon.png" alt="" />
        <div className="nail-brand-strip">
          {['OPI.png', 'CND.jpeg', 'DND.jpeg', 'NUGENESIS.jpeg', 'comfortzone.jpeg'].map(
            (brand) => (
              <img key={brand} src={`/nail-assets/${brand}`} alt="" />
            ),
          )}
        </div>
      </section>

      <section className="nail-pricing" data-nail-reveal>
        <header className="nail-section-heading">
          <p>
            {t('homePage.pricing.kickerBefore')}{' '}
            <strong>{t('homePage.pricing.kickerStrong')}</strong>{' '}
            {t('homePage.pricing.kickerAfter')}
          </p>
          <h2>
            {t('homePage.pricing.title')} <span>{t('homePage.pricing.accent')}</span>
          </h2>
        </header>
        <div className="nail-pricing__grid">
          {packages.map(([packageName, image]) => (
            <article key={packageName} data-nail-tilt>
              <img src={`/nail-assets/${image}`} alt="" />
              <div>
                <h3>{t(`homePage.pricing.packages.${packageName}`)}</h3>
                <p>{t('homePage.pricing.description')}</p>
              </div>
              <strong>{t(`homePage.pricing.labels.${packageName}`)}</strong>
            </article>
          ))}
        </div>
      </section>

      <section className="nail-journal" data-nail-reveal>
        <header className="nail-section-heading">
          <h2>
            {t('homePage.journal.title')} <span>{t('homePage.journal.accent')}</span>
          </h2>
          <p>{t('homePage.journal.intro')}</p>
        </header>
        <div className="nail-journal__grid">
          {data.latest_posts.slice(0, 3).map((post, index) => (
            <article key={post.id}>
              <Link to={`/journal/${post.slug}`}>
                <img
                  src={
                    post.cover_image ||
                    [
                      '/nail-assets/TNV_6179.jpg',
                      '/nail-assets/nail_recep.jpg',
                      '/nail-assets/Yoga.jpg',
                    ][index]
                  }
                  alt=""
                />
              </Link>
              <h3>
                <Link to={`/journal/${post.slug}`}>{post.title}</Link>
              </h3>
              <p>{post.excerpt}</p>
            </article>
          ))}
        </div>
      </section>

      <HomeBookingSection />
    </div>
  )
}
