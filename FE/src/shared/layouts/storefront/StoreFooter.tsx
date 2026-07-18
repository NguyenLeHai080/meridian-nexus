import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import type { StorefrontSite } from '@/modules/commerce/types/commerce.types'

interface StoreFooterProps {
  site: StorefrontSite
}

function createExploreLinks(site: StorefrontSite): ReactNode[] {
  const links: ReactNode[] = []

  for (const item of site.navigation) {
    if (item.path === '/') {
      continue
    }

    if (item.path === '/contact') {
      continue
    }

    links.push(
      <Link key={item.path} to={item.path}>
        {item.label}
      </Link>,
    )
  }

  return links
}

export function StoreFooter({ site }: StoreFooterProps) {
  const { t } = useTranslation()
  const exploreLinks = createExploreLinks(site)

  return (
    <footer className="store-footer">
      <div>
        <Link className="store-logo store-logo--light" to="/">
          <span>{site.brand.mark}</span>
          {site.brand.name}
        </Link>
        <p>{site.footer.tagline}</p>
      </div>
      <div>
        <small>{t('explore')}</small>
        {exploreLinks}
      </div>
      <div>
        <small>{t('help')}</small>
        <Link to="/contact">{t('contact')}</Link>
        <Link to="/profile">{t('orderHistory')}</Link>
        <a href={`mailto:${site.contact.email}`}>{site.contact.email}</a>
      </div>
      <div className="footer-note">
        <small>{site.footer.newsletter_title}</small>
        <p>{site.footer.newsletter_text}</p>
        <form>
          <input type="email" placeholder={t('emailAddress')} />
          <button>{t('join')}</button>
        </form>
      </div>
      <div className="footer-bottom">
        <span>{site.footer.legal}</span>
        <span>{site.footer.note}</span>
      </div>
    </footer>
  )
}
