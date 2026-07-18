import { useTranslation } from 'react-i18next'
import { Link, useParams } from 'react-router-dom'
import { useProduct } from '../hooks/use-commerce-data'
import { useCartStore } from '../store/cart-store'
import { formatMoney } from '../utils/format'

export function ProductDetailPage() {
  const { t } = useTranslation('storefront')
  const { slug = '' } = useParams()
  const { data: product } = useProduct(slug)
  const add = useCartStore((state) => state.add)

  if (product === undefined) {
    return <div className="catalog-loading">{t('product.loading')}</div>
  }

  let buttonLabel = t('product.outOfStock')
  let price = product.price
  if (product.stock > 0) {
    buttonLabel = t('product.add')
  }
  if (product.sale_price !== null) {
    price = product.sale_price
  }

  return (
    <section className="product-detail">
      <div className="product-gallery">
        <img src={product.images[0]} alt={product.name} />
      </div>
      <div className="product-info">
        <Link to="/products">{t('product.back')}</Link>
        <span className="store-kicker">
          {product.category?.name} / {product.sku}
        </span>
        <h1>{product.name}</h1>
        <p className="product-info__price">
          {formatMoney(price)} {product.sale_price && <del>{formatMoney(product.price)}</del>}
        </p>
        <p className="product-info__lead">{product.excerpt}</p>
        <button
          className="store-button store-button--wide"
          disabled={!product.stock}
          onClick={() => add(product)}
        >
          {buttonLabel}
          <span>+</span>
        </button>
        <div className="product-facts">
          <div>
            <strong>{t('product.materialTitle')}</strong>
            <p>{t('product.materialText')}</p>
          </div>
          <div>
            <strong>{t('product.shippingTitle')}</strong>
            <p>{t('product.shippingText')}</p>
          </div>
        </div>
      </div>
      <div className="product-description">
        <span>{t('product.materialTitle')}</span>
        {product.description?.split('\n').map((text) => (
          <p key={text}>{text}</p>
        ))}
      </div>
    </section>
  )
}
