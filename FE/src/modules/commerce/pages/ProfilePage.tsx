import type { ReactNode } from 'react'
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useAuthStore } from '@/core/auth/auth-store'
import { useLogout } from '@/modules/auth/hooks/use-auth-mutations'
import { useConfirmMfa, useSetupMfa } from '@/modules/auth/hooks/use-auth-mutations'
import type { MfaSetupPayload } from '@/modules/auth/types/auth.types'
import { PageLoader } from '@/shared/components/PageLoader'
import { useCustomerOrders } from '../hooks/use-commerce-data'
import { formatDate, formatMoney } from '../utils/format'

export function ProfilePage() {
  const { t } = useTranslation('storefront')
  const user = useAuthStore((state) => state.user)
  const logout = useLogout()
  const [page, setPage] = useState(1)
  const [mfaPassword, setMfaPassword] = useState('')
  const [mfaCode, setMfaCode] = useState('')
  const [mfaSetup, setMfaSetup] = useState<MfaSetupPayload | null>(null)
  const [recoveryCodes, setRecoveryCodes] = useState<string[]>([])
  const { data: orders } = useCustomerOrders(page)
  const setupMfa = useSetupMfa()
  const confirmMfa = useConfirmMfa()

  if (user === null) {
    return <PageLoader />
  }

  let memberSince = t('profile.today')
  if (user.created_at) {
    memberSince = formatDate(user.created_at)
  }

  let orderCount = 0
  let orderContent: ReactNode = (
    <div className="empty-state">
      <span>○</span>
      <h3>{t('profile.empty')}</h3>
      <p>{t('profile.emptyText')}</p>
    </div>
  )

  if (orders !== undefined && orders.items.length > 0) {
    orderCount = orders.pagination.total
    orderContent = orders.items.map((order) => (
      <article key={order.id}>
        <div>
          <strong>{order.number}</strong>
          <small>{formatDate(order.created_at)}</small>
        </div>
        <div>
          <span className={`status status--${order.status}`}>
            {t(`status.${order.status}`, { defaultValue: order.status })}
          </span>
          <strong>{formatMoney(order.total)}</strong>
        </div>
        <details>
          <summary>{t('profile.viewItems', { count: order.items.length })}</summary>
          {order.items.map((item) => (
            <p key={item.id}>
              {item.quantity} x {item.product_name} <span>{formatMoney(item.total)}</span>
            </p>
          ))}
        </details>
      </article>
    ))
  }

  return (
    <section className="profile-page">
      <header>
        <span className="store-kicker">{t('profile.eyebrow')}</span>
        <h1>
          {t('profile.welcome')}
          <br />
          <em>{user.name.split(' ')[0]}.</em>
        </h1>
        <button onClick={() => logout.mutate()}>{t('profile.signOut')}</button>
      </header>
      <div className="profile-grid">
        <aside>
          <div className="profile-avatar">{user.name.charAt(0)}</div>
          <h2>{user.name}</h2>
          <p>{user.email}</p>
          <dl>
            <dt>{t('profile.memberSince')}</dt>
            <dd>{memberSince}</dd>
            <dt>{t('profile.accountType')}</dt>
            <dd>{t('profile.member')}</dd>
          </dl>
          {!user.mfa_enabled && (
            <div className="profile-mfa">
              <h3>{t('profile.mfaTitle')}</h3>
              <p>{t('profile.mfaText')}</p>
              {mfaSetup === null && (
                <form
                  onSubmit={(event) => {
                    event.preventDefault()
                    setupMfa.mutate(mfaPassword, { onSuccess: setMfaSetup })
                  }}
                >
                  <input
                    type="password"
                    autoComplete="current-password"
                    placeholder={t('profile.currentPassword')}
                    value={mfaPassword}
                    onChange={(event) => setMfaPassword(event.target.value)}
                    required
                  />
                  <button disabled={setupMfa.isPending}>{t('profile.startMfa')}</button>
                </form>
              )}
              {mfaSetup !== null && recoveryCodes.length === 0 && (
                <form
                  onSubmit={(event) => {
                    event.preventDefault()
                    confirmMfa.mutate(mfaCode, {
                      onSuccess: (data) => setRecoveryCodes(data.recovery_codes),
                    })
                  }}
                >
                  <p>
                    {t('profile.mfaSecret')} <code>{mfaSetup.secret}</code>
                  </p>
                  <input
                    inputMode="numeric"
                    autoComplete="one-time-code"
                    placeholder={t('profile.mfaCode')}
                    value={mfaCode}
                    onChange={(event) => setMfaCode(event.target.value)}
                    required
                  />
                  <button disabled={confirmMfa.isPending}>{t('profile.confirmMfa')}</button>
                </form>
              )}
              {recoveryCodes.length > 0 && (
                <div>
                  <strong>{t('profile.recoveryCodes')}</strong>
                  <p>{t('profile.recoveryWarning')}</p>
                  <code>{recoveryCodes.join('\n')}</code>
                </div>
              )}
            </div>
          )}
        </aside>
        <div className="order-history">
          <div className="profile-section-title">
            <h2>{t('profile.history')}</h2>
            <span>{t('profile.orders', { count: orderCount })}</span>
          </div>
          {orderContent}
          {orders !== undefined && orders.pagination.last_page > 1 && (
            <nav className="store-pagination" aria-label={t('pagination.label')}>
              <button
                type="button"
                aria-label={t('pagination.previous')}
                disabled={orders.pagination.current_page === 1}
                onClick={() => setPage(orders.pagination.current_page - 1)}
              >
                &larr;
              </button>
              <span>
                {orders.pagination.current_page} / {orders.pagination.last_page}
              </span>
              <button
                type="button"
                aria-label={t('pagination.next')}
                disabled={orders.pagination.current_page === orders.pagination.last_page}
                onClick={() => setPage(orders.pagination.current_page + 1)}
              >
                &rarr;
              </button>
            </nav>
          )}
        </div>
      </div>
    </section>
  )
}
