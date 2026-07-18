import type { Category } from '@/modules/commerce/types/commerce.types'
import { useTranslation } from 'react-i18next'
import type { AdminMetadata, CreateProductInput } from '../../types/admin.types'

interface ProductCreateFormProps {
  categories: Category[]
  metadata: AdminMetadata
  pending: boolean
  onSubmit: (input: CreateProductInput) => void
}

export function ProductCreateForm({
  categories,
  metadata,
  pending,
  onSubmit,
}: ProductCreateFormProps) {
  const { t } = useTranslation('admin')
  return (
    <form
      className="admin-create-form"
      onSubmit={(event) => {
        event.preventDefault()
        const values = new FormData(event.currentTarget)
        const status = String(values.get('status'))
        const image = String(values.get('image') || '')
        let categoryId: number | null = null
        let salePrice: number | null = null
        let images: string[] = []
        let publishedAt: string | null = null

        if (values.get('category_id')) {
          categoryId = Number(values.get('category_id'))
        }
        if (values.get('sale_price')) {
          salePrice = Number(values.get('sale_price'))
        }
        if (image) {
          images = [image]
        }
        if (status === metadata.publishing.product_status) {
          publishedAt = new Date().toISOString()
        }

        onSubmit({
          name: String(values.get('name')),
          sku: String(values.get('sku')),
          category_id: categoryId,
          price: Number(values.get('price')),
          sale_price: salePrice,
          stock: Number(values.get('stock')),
          images,
          excerpt: String(values.get('excerpt') || '') || null,
          description: String(values.get('description') || '') || null,
          is_featured: values.get('is_featured') === 'on',
          status,
          published_at: publishedAt,
        })
      }}
    >
      <input name="name" placeholder={t('form.productName')} required />
      <input name="sku" placeholder="SKU" required />
      <select name="category_id" defaultValue="">
        <option value="">{t('form.noCategory')}</option>
        {categories.map((category) => (
          <option key={category.id} value={category.id}>
            {category.name}
          </option>
        ))}
      </select>
      <select name="status" defaultValue={metadata.defaults.product_status}>
        {metadata.options.product_statuses.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      <input
        name="price"
        type="number"
        min="0"
        step="0.01"
        placeholder={t('form.price')}
        required
      />
      <input
        name="sale_price"
        type="number"
        min="0"
        step="0.01"
        placeholder={t('form.salePrice')}
      />
      <input name="stock" type="number" min="0" placeholder={t('form.stock')} required />
      <input name="image" type="url" placeholder={t('form.image')} />
      <input name="excerpt" placeholder={t('form.shortDescription')} />
      <textarea name="description" placeholder={t('form.fullDescription')} />
      <label className="admin-checkbox">
        <input name="is_featured" type="checkbox" /> {t('form.featured')}
      </label>
      <button disabled={pending}>{t('form.createProduct')}</button>
    </form>
  )
}
