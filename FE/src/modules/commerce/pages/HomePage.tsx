import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import { ProductCard } from '../components/ProductCard'
import { useStorefrontHome } from '../hooks/use-commerce-data'
import { formatDate } from '../utils/format'

export function HomePage() {
  const { t } = useTranslation('storefront')
  const { data } = useStorefrontHome()

  if (data === undefined) {
    return null
  }

  const hero = data.site.home_hero
  let promotion = null
  if (data.promotions.length > 0) {
    promotion = data.promotions[0]
  }

  return (
    <>
      <section className="hero-store">
        <div className="hero-store__copy">
          <span className="store-kicker">{hero.eyebrow}</span>
          <h1>
            {hero.title}
            <br />
            <em>{hero.accent}</em>
          </h1>
          <p>{hero.description}</p>
          <Link className="store-button" to={hero.cta_path}>
            {hero.cta_label}
            <span>→</span>
          </Link>
        </div>
        <div className="hero-store__visual">
          <img src={hero.image} alt={hero.image_alt} />
          <div className="hero-tag">
            <span>01</span>
            <p>{t('home.featuredTitle')}</p>
          </div>
        </div>
      </section>
      <section className="store-section">
        <header className="section-heading">
          <div>
            <span className="store-kicker">{t('home.featuredEyebrow')}</span>
            <h2>{t('home.featuredTitle')}</h2>
          </div>
          <Link to="/products">{t('home.shopAll')}</Link>
        </header>
        <div className="product-grid">
          {data.featured_products.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      </section>
      <section className="manifesto">
        <span>{t('home.manifestoEyebrow')}</span>
        <p>{t('home.manifesto')}</p>
        <Link to="/about">{t('home.readStory')}</Link>
      </section>
      <section className="category-strip">
        {data.categories.map((category, index) => (
          <Link to={`/products?category=${category.slug}`} key={category.id}>
            <span>0{index + 1}</span>
            <h3>{category.name}</h3>
            <p>{category.description}</p>
            <strong>
              {category.products_count} {t('home.pieces')}
            </strong>
          </Link>
        ))}
      </section>
      {promotion && (
        <section className="promotion-banner">
          <span>{t('home.offer')}</span>
          <h2>{promotion.name}</h2>
          <p>
            <strong>{promotion.code}</strong> / {promotion.minimum_order}
          </p>
          <Link to="/products">{t('home.shopCollection')}</Link>
        </section>
      )}
      <section className="store-section journal-preview">
        <header className="section-heading">
          <div>
            <span className="store-kicker">{t('home.journalEyebrow')}</span>
            <h2>{t('home.journalTitle')}</h2>
          </div>
          <Link to="/journal">{t('home.readAll')}</Link>
        </header>
        <div className="journal-grid">
          {data.latest_posts.map((post) => (
            <article key={post.id}>
              <Link to={`/journal/${post.slug}`}>
                <img src={post.cover_image || ''} alt="" />
              </Link>
              <small>{formatDate(post.published_at)}</small>
              <h3>
                <Link to={`/journal/${post.slug}`}>{post.title}</Link>
              </h3>
              <p>{post.excerpt}</p>
            </article>
          ))}
        </div>
      </section>
    </>
  )
}
