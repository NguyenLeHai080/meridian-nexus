interface CategoryCreateFormProps {
  pending: boolean
  onSubmit: (input: { name: string; description?: string }) => void
}

export function CategoryCreateForm({ pending, onSubmit }: CategoryCreateFormProps) {
  const { t } = useTranslation('admin')
  return (
    <form
      className="admin-create-form admin-create-form--compact"
      onSubmit={(event) => {
        event.preventDefault()
        const values = new FormData(event.currentTarget)
        onSubmit({
          name: String(values.get('name')),
          description: String(values.get('description') || ''),
        })
      }}
    >
      <input name="name" placeholder={t('form.categoryName')} required />
      <input name="description" placeholder={t('form.categoryDescription')} />
      <button disabled={pending}>{t('form.createCategory')}</button>
    </form>
  )
}
import { useTranslation } from 'react-i18next'
