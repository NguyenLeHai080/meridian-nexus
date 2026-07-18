import type { ReactNode } from 'react'
import { useTranslation } from 'react-i18next'
import { useSearchParams } from 'react-router-dom'
import { ProductCard } from '../components/ProductCard'
import { useProducts, useStorefrontHome } from '../hooks/use-commerce-data'

export function ProductsPage() {
  const { t } = useTranslation('storefront')
  const [params, setParams] = useSearchParams()
  const search = params.get('search') || ''
  const category = params.get('category') || ''
  const products = useProducts({ search, category })
  const home = useStorefrontHome()
  const categories = [{ slug: '', name: t('products.all') }]

  if (home.data !== undefined) {
    categories.push(...home.data.categories)
  }

  let productContent: ReactNode = <p className="catalog-loading">{t('products.loading')}</p>
  if (!products.isLoading) {
    productContent = (
      <div className="product-grid product-grid--catalog">
        {products.data?.data.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    )
  }

  let productCount = 0
  if (products.data !== undefined) {
    productCount = products.data.meta.pagination.total
  }

  return (
    <section className="catalog-page">
      <header>
        <span className="store-kicker">{t('products.eyebrow')}</span>
        <h1>{t('products.title')}</h1>
        <p>{t('products.count', { count: productCount })}</p>
      </header>
      <div className="catalog-toolbar">
        <input
          aria-label={t('products.searchLabel')}
          placeholder={t('products.search')}
          defaultValue={search}
          onKeyDown={(event) => {
            if (event.key === 'Enter')
              setParams({ ...(category && { category }), search: event.currentTarget.value })
          }}
        />
        <div>
          {categories.map((item) => {
            let buttonClassName = ''
            if (category === item.slug) {
              buttonClassName = 'active'
            }
            return (
              <button
                className={buttonClassName}
                key={item.slug || 'all'}
                onClick={() =>
                  setParams({
                    ...(search && { search }),
                    ...(item.slug && { category: item.slug }),
                  })
                }
              >
                {item.name}
              </button>
            )
          })}
        </div>
      </div>
      {productContent}
    </section>
  )
}
