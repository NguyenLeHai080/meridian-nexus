import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import type { Product } from '../types/commerce.types'
import { formatMoney } from '../utils/format'

export function ProductCard({ product }: { product: Product }) {
  const { t } = useTranslation('storefront')

  return (
    <article className="product-card">
      <Link className="product-card__image" to={`/products/${product.slug}`}>
        <img src={product.images[0]} alt={product.name} loading="lazy" />
        {product.sale_price && <span>{t('product.sale')}</span>}
      </Link>
      <div className="product-card__meta">
        <small>{product.category?.name || t('product.collection')}</small>
        <h3>
          <Link to={`/products/${product.slug}`}>{product.name}</Link>
        </h3>
        <div className="product-card__price">
          <strong>{formatMoney(product.sale_price ?? product.price)}</strong>
          {product.sale_price && <del>{formatMoney(product.price)}</del>}
        </div>
      </div>
    </article>
  )
}
