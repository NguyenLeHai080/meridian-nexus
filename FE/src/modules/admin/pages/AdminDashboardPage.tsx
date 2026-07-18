import { useTranslation } from 'react-i18next'
import { formatDate, formatMoney } from '@/modules/commerce/utils/format'
import { AdminHeader } from '../components/AdminHeader'
import { useAdminDashboard } from '../hooks/use-admin-data'
import { useAdminLabel } from '../hooks/use-admin-label'

export function AdminDashboardPage() {
  const { t } = useTranslation('admin')
  const label = useAdminLabel()
  const { data } = useAdminDashboard()
  let stats: Array<[string, string | number, string]> = [
    [t('dashboard.revenue'), '—', t('loading')],
    [t('dashboard.orders'), '—', t('loading')],
    [t('dashboard.products'), '—', t('loading')],
    [t('dashboard.customers'), '—', t('loading')],
  ]

  if (data !== undefined) {
    stats = [
      [t('dashboard.revenue'), formatMoney(data.revenue), t('dashboard.paidOrders')],
      [t('dashboard.orders'), data.orders, t('dashboard.pending', { count: data.pending_orders })],
      [
        t('dashboard.products'),
        data.products,
        t('dashboard.lowStock', { count: data.low_stock_products }),
      ],
      [
        t('dashboard.customers'),
        data.customers,
        t('dashboard.openChats', { count: data.open_conversations }),
      ],
    ]
  }

  return (
    <>
      <AdminHeader eyebrow={t('dashboard.eyebrow')} title={t('dashboard.title')} />
      <section className="admin-stats">
        {stats.map(([label, value, note], index) => (
          <article key={label}>
            <span>0{index + 1}</span>
            <small>{label}</small>
            <strong>{value}</strong>
            <p>{note}</p>
          </article>
        ))}
      </section>
      <section className="admin-panel">
        <header>
          <div>
            <span>{t('dashboard.latest')}</span>
            <h2>{t('dashboard.recentOrders')}</h2>
          </div>
          <a href="/admin/orders">{t('dashboard.viewAll')}</a>
        </header>
        <div className="admin-table">
          <div className="admin-table__head">
            <span>{t('table.order')}</span>
            <span>{t('table.customer')}</span>
            <span>{t('table.status')}</span>
            <span>{t('table.total')}</span>
            <span>{t('table.date')}</span>
          </div>
          {data?.recent_orders.map((order) => (
            <div className="admin-table__row" key={order.id}>
              <strong>{order.number}</strong>
              <span>{order.customer_name}</span>
              <span className={`status status--${order.status}`}>
                {label('status', order.status)}
              </span>
              <strong>{formatMoney(order.total)}</strong>
              <span>{formatDate(order.created_at)}</span>
            </div>
          ))}
        </div>
      </section>
    </>
  )
}
