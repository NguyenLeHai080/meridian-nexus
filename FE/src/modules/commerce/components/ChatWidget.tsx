import { useTranslation } from 'react-i18next'
import { useAuthStore } from '@/core/auth/auth-store'
import { useChatConversation, useSendChatMessage } from '../hooks/use-commerce-data'
import { useChatStore } from '../store/chat-store'

export function ChatWidget() {
  const { t } = useTranslation('storefront')
  const user = useAuthStore((state) => state.user)
  const { open, token, message, guest, setOpen, setToken, setMessage, setGuest } = useChatStore()
  const conversation = useChatConversation(token, open)
  const send = useSendChatMessage(token)
  let widgetClassName = 'chat-widget'
  let triggerLabel = t('chat.open')

  if (open) {
    widgetClassName += ' chat-widget--open'
    triggerLabel = '×'
  }

  const submitMessage = () => {
    if (!message.trim()) return
    let guestInput: { name: string; email: string } | undefined = guest
    if (user !== null) {
      guestInput = undefined
    }

    send.mutate(
      { message, guest: guestInput },
      {
        onSuccess: (data) => {
          if (data.token !== null) {
            setToken(data.token)
          }
          setMessage('')
        },
      },
    )
  }

  return (
    <div className={widgetClassName}>
      {open && (
        <section className="chat-panel">
          <header>
            <div>
              <small>{t('chat.eyebrow')}</small>
              <strong>{t('chat.title')}</strong>
            </div>
            <button type="button" aria-label={t('chat.close')} onClick={() => setOpen(false)}>
              ×
            </button>
          </header>
          <div className="chat-messages">
            {!token && <p className="chat-intro">{t('chat.intro')}</p>}
            {conversation.data?.messages.map((item) => (
              <p key={item.id} className={`chat-bubble chat-bubble--${item.sender_type}`}>
                {item.body}
              </p>
            ))}
          </div>
          <form
            onSubmit={(event) => {
              event.preventDefault()
              submitMessage()
            }}
          >
            {!user && !token && (
              <div className="chat-guest">
                <input
                  placeholder={t('chat.name')}
                  value={guest.name}
                  onChange={(event) => setGuest({ ...guest, name: event.target.value })}
                  required
                />
                <input
                  type="email"
                  placeholder={t('chat.email')}
                  value={guest.email}
                  onChange={(event) => setGuest({ ...guest, email: event.target.value })}
                  required
                />
              </div>
            )}
            <div className="chat-compose">
              <input
                placeholder={t('chat.message')}
                value={message}
                onChange={(event) => setMessage(event.target.value)}
              />
              <button disabled={send.isPending}>{t('chat.send')}</button>
            </div>
          </form>
        </section>
      )}
      <button
        className="chat-trigger"
        type="button"
        onClick={() => setOpen(!open)}
        aria-label={t('chat.open')}
      >
        {triggerLabel}
      </button>
    </div>
  )
}
