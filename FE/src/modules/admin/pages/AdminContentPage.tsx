import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { usePermissions } from '@/core/auth/use-permission'
import { formatDate } from '@/modules/commerce/utils/format'
import { AdminHeader } from '../components/AdminHeader'
import { AdminStatusSelect } from '../components/AdminStatusSelect'
import { PostCreateForm } from '../components/forms/PostCreateForm'
import {
  useAdminContacts,
  useAdminMetadata,
  useAdminPosts,
  useCreatePost,
  useDeletePost,
  useUpdateContact,
} from '../hooks/use-admin-data'
import { useAdminLabel } from '../hooks/use-admin-label'

export function AdminContentPage() {
  const { t } = useTranslation('admin')
  const label = useAdminLabel()
  const permissions = usePermissions()
  const canManageContent = permissions.includes('content.manage')
  const canViewContacts = permissions.includes('contacts.view')
  const [creating, setCreating] = useState(false)
  const metadata = useAdminMetadata(creating || canViewContacts)
  const posts = useAdminPosts(canManageContent)
  const contacts = useAdminContacts(canViewContacts)
  const createPost = useCreatePost(() => setCreating(false))
  const deletePost = useDeletePost()
  const updateContact = useUpdateContact()

  return (
    <>
      <AdminHeader
        eyebrow={t('content.eyebrow')}
        title={t('content.title')}
        action={
          canManageContent && (
            <button className="admin-button" onClick={() => setCreating((open) => !open)}>
              {t('content.new')}
            </button>
          )
        }
      />
      {creating && metadata.data && (
        <PostCreateForm
          metadata={metadata.data}
          pending={createPost.isPending}
          onSubmit={createPost.mutate}
        />
      )}
      {canManageContent && (
        <section className="admin-panel">
          <header>
            <div>
              <span>{t('content.journal')}</span>
              <h2>{t('content.articles')}</h2>
            </div>
            <span>{t('content.entries', { count: posts.data?.length ?? 0 })}</span>
          </header>
          <div className="admin-content-list">
            {posts.data?.map((post) => (
              <article key={post.id}>
                <div>
                  <span className={`status status--${post.status}`}>
                    {label('status', post.status)}
                  </span>
                  <h3>{post.title}</h3>
                  <p>{post.excerpt || t('content.noExcerpt')}</p>
                </div>
                <div>
                  <small>{post.author || t('content.editorial')}</small>
                  <small>{formatDate(post.published_at)}</small>
                  <button
                    className="admin-text-button admin-text-button--danger"
                    onClick={() => {
                      if (window.confirm(t('content.confirmDelete', { title: post.title }))) {
                        deletePost.mutate(post.id)
                      }
                    }}
                  >
                    {t('content.delete')}
                  </button>
                </div>
              </article>
            ))}
          </div>
        </section>
      )}
      {canViewContacts && (
        <section className="admin-panel">
          <header>
            <div>
              <span>{t('content.inbox')}</span>
              <h2>{t('content.enquiries')}</h2>
            </div>
            <span>{t('content.messages', { count: contacts.data?.length ?? 0 })}</span>
          </header>
          <div className="admin-contact-list">
            {contacts.data?.map((contact) => (
              <article key={contact.id}>
                <div>
                  <strong>{contact.subject}</strong>
                  <span>
                    {contact.name} / {contact.email}
                  </span>
                  <p>{contact.message}</p>
                </div>
                {metadata.data && (
                  <AdminStatusSelect
                    options={metadata.data.options.contact_statuses}
                    value={contact.status}
                    disabled={updateContact.isPending}
                    onChange={(status) => updateContact.mutate({ id: contact.id, status })}
                  />
                )}
              </article>
            ))}
          </div>
        </section>
      )}
    </>
  )
}
