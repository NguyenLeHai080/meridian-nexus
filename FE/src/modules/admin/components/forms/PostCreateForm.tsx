import type { Post } from '@/modules/commerce/types/commerce.types'
import { useTranslation } from 'react-i18next'
import type { AdminMetadata, CreatePostInput } from '../../types/admin.types'

interface PostCreateFormProps {
  metadata: AdminMetadata
  pending: boolean
  onSubmit: (input: CreatePostInput) => void
}

export function PostCreateForm({ metadata, pending, onSubmit }: PostCreateFormProps) {
  const { t } = useTranslation('admin')
  return (
    <form
      className="admin-create-form admin-create-form--post"
      onSubmit={(event) => {
        event.preventDefault()
        const values = new FormData(event.currentTarget)
        const status = String(values.get('status')) as Post['status']
        let publishedAt: string | null = null

        if (status === metadata.publishing.post_status) {
          publishedAt = new Date().toISOString()
        }

        onSubmit({
          title: String(values.get('title')),
          slug: null,
          excerpt: String(values.get('excerpt') || '') || null,
          content: String(values.get('content')),
          cover_image: String(values.get('cover_image') || '') || null,
          status,
          published_at: publishedAt,
        })
      }}
    >
      <input name="title" placeholder={t('form.articleTitle')} required />
      <input name="excerpt" placeholder={t('form.shortIntroduction')} />
      <input name="cover_image" type="url" placeholder={t('form.coverImage')} />
      <select name="status" defaultValue={metadata.defaults.post_status}>
        {metadata.options.post_statuses.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      <textarea
        className="admin-field--wide"
        name="content"
        placeholder={t('form.articleContent')}
        required
      />
      <button disabled={pending}>{t('form.saveArticle')}</button>
    </form>
  )
}
