import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { usePermission } from '@/core/auth/use-permission'
import { formatMoney } from '@/modules/commerce/utils/format'
import { AdminHeader } from '../components/AdminHeader'
import { AdminPagination } from '../components/AdminPagination'
import { CategoryCreateForm } from '../components/forms/CategoryCreateForm'
import { ProductCreateForm } from '../components/forms/ProductCreateForm'
import {
  useAdminCategories,
  useAdminMetadata,
  useAdminProducts,
  useCreateCategory,
  useCreateProduct,
} from '../hooks/use-admin-data'

export function AdminProductsPage() {
  const { t } = useTranslation('admin')
  const canManage = usePermission('products.manage')
  const [creatingProduct, setCreatingProduct] = useState(false)
  const [creatingCategory, setCreatingCategory] = useState(false)
  const [page, setPage] = useState(1)
  const products = useAdminProducts(page)
  const categories = useAdminCategories(creatingProduct)
  const metadata = useAdminMetadata(creatingProduct)
  const createProduct = useCreateProduct(() => setCreatingProduct(false))
  const createCategory = useCreateCategory(() => setCreatingCategory(false))

  return (
    <>
      <AdminHeader
        eyebrow={t('products.eyebrow')}
        title={t('products.title')}
        action={
          canManage && (
            <div className="admin-actions">
              <button
                className="admin-button admin-button--secondary"
                onClick={() => setCreatingCategory((open) => !open)}
              >
                {t('products.category')}
              </button>
              <button className="admin-button" onClick={() => setCreatingProduct((open) => !open)}>
                {t('products.new')}
              </button>
            </div>
          )
        }
      />
      {creatingCategory && (
        <CategoryCreateForm pending={createCategory.isPending} onSubmit={createCategory.mutate} />
      )}
      {creatingProduct && metadata.data && (
        <ProductCreateForm
          categories={categories.data ?? []}
          metadata={metadata.data}
          pending={createProduct.isPending}
          onSubmit={createProduct.mutate}
        />
      )}
      <section className="admin-panel">
        <div className="admin-table admin-table--products">
          <div className="admin-table__head">
            <span>{t('table.product')}</span>
            <span>SKU</span>
            <span>{t('table.price')}</span>
            <span>{t('table.stock')}</span>
            <span>{t('table.collection')}</span>
          </div>
          {products.data?.items.map((product) => {
            let stockClassName = ''
            if (product.stock <= 5) {
              stockClassName = 'stock-low'
            }

            return (
              <div className="admin-table__row" key={product.id}>
                <span className="admin-product">
                  <img src={product.images[0]} alt="" />
                  <strong>{product.name}</strong>
                </span>
                <span>{product.sku}</span>
                <strong>{formatMoney(product.sale_price ?? product.price)}</strong>
                <span className={stockClassName}>{product.stock}</span>
                <span>{product.category?.name || '-'}</span>
              </div>
            )
          })}
        </div>
        <AdminPagination pagination={products.data?.pagination} onPageChange={setPage} />
      </section>
    </>
  )
}
