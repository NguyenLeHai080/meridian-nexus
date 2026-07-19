import type { ReactNode } from 'react'
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { AdminHeader } from '../components/AdminHeader'
import { AdminPagination } from '../components/AdminPagination'
import {
  useAdminConversation,
  useAdminConversations,
  useReplyToConversation,
} from '../hooks/use-admin-data'
import { useAdminLabel } from '../hooks/use-admin-label'

export function AdminChatPage() {
  const { t } = useTranslation('admin')
  const label = useAdminLabel()
  const [selected, setSelected] = useState<number | null>(null)
  const [page, setPage] = useState(1)
  const conversations = useAdminConversations(page)
  const conversation = useAdminConversation(selected)
  const reply = useReplyToConversation(selected)
  let threadContent: ReactNode = (
    <div className="empty-state">
      <span>○</span>
      <h3>{t('chat.select')}</h3>
    </div>
  )

  if (conversation.data !== undefined) {
    threadContent = (
      <>
        <header>
          <h2>{conversation.data.customer}</h2>
          <span>{label('status', conversation.data.status)}</span>
        </header>
        <div>
          {conversation.data.messages.map((message) => (
            <p className={`chat-bubble chat-bubble--${message.sender_type}`} key={message.id}>
              {message.body}
            </p>
          ))}
        </div>
        <form
          onSubmit={(event) => {
            event.preventDefault()
            const form = new FormData(event.currentTarget)
            reply.mutate(String(form.get('message')))
            event.currentTarget.reset()
          }}
        >
          <input name="message" placeholder={t('chat.reply')} required />
          <button disabled={reply.isPending}>{t('chat.send')}</button>
        </form>
      </>
    )
  }

  return (
    <>
      <AdminHeader eyebrow={t('chat.eyebrow')} title={t('chat.title')} />
      <section className="admin-chat">
        <aside>
          {conversations.data?.items.map((item) => {
            let buttonClassName = ''
            if (selected === item.id) {
              buttonClassName = 'active'
            }

            return (
              <button
                className={buttonClassName}
                key={item.id}
                onClick={() => setSelected(item.id)}
              >
                <span>{item.customer?.charAt(0)}</span>
                <div>
                  <strong>{item.customer || t('chat.guest')}</strong>
                  <small>
                    {label('status', item.status)} / {item.assigned_to || t('chat.unassigned')}
                  </small>
                </div>
              </button>
            )
          })}
          <AdminPagination pagination={conversations.data?.pagination} onPageChange={setPage} />
        </aside>
        <div className="admin-chat-thread">{threadContent}</div>
      </section>
    </>
  )
}
