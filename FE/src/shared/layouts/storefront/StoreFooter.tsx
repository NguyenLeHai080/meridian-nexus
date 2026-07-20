import { Link } from 'react-router-dom'
import type { ReactNode } from 'react'
import { useTranslation } from 'react-i18next'
import type { StorefrontSite } from '@/modules/commerce/types/commerce.types'

function FooterColumn({
  title,
  children,
  className = '',
}: {
  title: string
  children: ReactNode
  className?: string
}) {
  return (
    <section className={className}>
      <h3>{title}</h3>
      {children}
    </section>
  )
}

export function StoreFooter({ site }: { site: StorefrontSite }) {
  const { t } = useTranslation('storefront')
  const footerPosts = [
    ['TNV_6179.jpg', t('homePage.footer.post1')],
    ['nail_recep.jpg', t('homePage.footer.post2')],
    ['Yoga.jpg', t('homePage.footer.post3')],
  ] as const

  return (
    <footer className="store-footer nail-footer">
      <FooterColumn title={t('homePage.footer.aboutTitle')}>
        <p>{t('homePage.footer.aboutText')}</p>
      </FooterColumn>
      <FooterColumn title={t('homePage.footer.contactTitle')}>
        <address className="nail-footer__address">
          <span>
            {t('homePage.footer.consultation')}:{' '}
            <Link to="/contact">{t('homePage.footer.requestConsultation')}</Link>
          </span>
          <span>
            {t('homePage.footer.email')}:{' '}
            <a href={`mailto:${site.contact.email}`}>{site.contact.email}</a>
          </span>
          <span>{t('homePage.footer.location')}</span>
        </address>
        <Link className="nail-footer__direction" to="/contact">
          {t('homePage.footer.directions')}
        </Link>
      </FooterColumn>
      <FooterColumn title={t('homePage.footer.news')} className="nail-footer__posts">
        {footerPosts.map(([image, title]) => (
          <Link key={title} to="/journal">
            <img src={`/nail-assets/${image}`} alt="" />
            <span>{title}</span>
          </Link>
        ))}
      </FooterColumn>
      <div className="nail-footer__bottom">
        <span>Copyright 2026 ©</span>
        <span>{site.brand.name}</span>
        <span>f · i · x · p · in</span>
      </div>
    </footer>
  )
}
