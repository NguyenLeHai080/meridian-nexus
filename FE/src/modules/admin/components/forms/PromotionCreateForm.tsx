import type { AdminMetadata, CreatePromotionInput } from '../../types/admin.types'

interface PromotionCreateFormProps {
  metadata: AdminMetadata
  pending: boolean
  onSubmit: (input: CreatePromotionInput) => void
}

export function PromotionCreateForm({ metadata, pending, onSubmit }: PromotionCreateFormProps) {
  const { t } = useTranslation('admin')
  return (
    <form
      className="admin-create-form"
      onSubmit={(event) => {
        event.preventDefault()
        const values = new FormData(event.currentTarget)
        onSubmit({
          name: String(values.get('name')),
          code: String(values.get('code') || '') || null,
          type: String(values.get('type')),
          value: Number(values.get('value')),
          minimum_order: Number(values.get('minimum_order')),
          starts_at: String(values.get('starts_at') || '') || null,
          ends_at: String(values.get('ends_at') || '') || null,
          is_active: values.get('is_active') === 'on',
        })
      }}
    >
      <input name="name" placeholder={t('form.offerName')} required />
      <input name="code" placeholder={t('form.optionalCode')} />
      <select name="type" defaultValue={metadata.defaults.promotion_type}>
        {metadata.options.promotion_types.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      <input
        name="value"
        type="number"
        min="0"
        step="0.01"
        placeholder={t('form.value')}
        required
      />
      <input
        name="minimum_order"
        type="number"
        min="0"
        placeholder={t('form.minimumOrder')}
        defaultValue="0"
      />
      <input name="starts_at" type="datetime-local" />
      <input name="ends_at" type="datetime-local" />
      <label className="admin-checkbox">
        <input
          name="is_active"
          type="checkbox"
          defaultChecked={metadata.defaults.promotion_is_active}
        />{' '}
        {t('form.active')}
      </label>
      <button disabled={pending}>{t('form.createOffer')}</button>
    </form>
  )
}
import { useTranslation } from 'react-i18next'
