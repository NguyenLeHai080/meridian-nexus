import { useTranslation } from 'react-i18next'

export function AboutPage() {
  const { t } = useTranslation('storefront')
  return (
    <>
      <section className="page-hero page-hero--story">
        <span className="store-kicker">{t('about.eyebrow')}</span>
        <h1>
          {t('about.title')}
          <br />
          <em>{t('about.accent')}</em>
        </h1>
      </section>
      <section className="story-grid">
        <div>
          <span>01 / {t('about.section')}</span>
          <h2>{t('about.heading')}</h2>
        </div>
        <div>
          <p>{t('about.paragraph1')}</p>
          <p>{t('about.paragraph2')}</p>
        </div>
      </section>
      <section className="story-image">
        <img
          src="https://images.unsplash.com/photo-1497366811353-6870744d04b2?auto=format&fit=crop&w=1800&q=90"
          alt={t('about.imageAlt')}
        />
      </section>
      <section className="values">
        <article>
          <span>01</span>
          <h3>{t('about.value1')}</h3>
        </article>
        <article>
          <span>02</span>
          <h3>{t('about.value2')}</h3>
        </article>
        <article>
          <span>03</span>
          <h3>{t('about.value3')}</h3>
        </article>
      </section>
    </>
  )
}
