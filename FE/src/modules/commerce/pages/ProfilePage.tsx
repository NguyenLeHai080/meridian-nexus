import type { ReactNode } from 'react'
import { useTranslation } from 'react-i18next'
import { useAuthStore } from '@/core/auth/auth-store'
import { useLogout } from '@/modules/auth/hooks/use-auth-mutations'
import { PageLoader } from '@/shared/components/PageLoader'
import { useCustomerOrders } from '../hooks/use-commerce-data'
import { formatDate, formatMoney } from '../utils/format'

export function ProfilePage() {
  const { t } = useTranslation('storefront')
  const user = useAuthStore((state) => state.user)
  const logout = useLogout()
  const { data: orders } = useCustomerOrders()

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

  if (orders !== undefined && orders.length > 0) {
    orderCount = orders.length
    orderContent = orders.map((order) => (
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
        </aside>
        <div className="order-history">
          <div className="profile-section-title">
            <h2>{t('profile.history')}</h2>
            <span>{t('profile.orders', { count: orderCount })}</span>
          </div>
          {orderContent}
        </div>
      </div>
    </section>
  )
}
