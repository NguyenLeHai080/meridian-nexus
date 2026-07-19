import { useState } from 'react'
import { usePermission } from '@/core/auth/use-permission'
import { useTranslation } from 'react-i18next'
import { formatDate, formatMoney } from '@/modules/commerce/utils/format'
import { AdminHeader } from '../components/AdminHeader'
import { AdminPagination } from '../components/AdminPagination'
import { AdminStatusSelect } from '../components/AdminStatusSelect'
import { useAdminMetadata, useAdminOrders, useUpdateOrder } from '../hooks/use-admin-data'
import { useAdminLabel } from '../hooks/use-admin-label'

export function AdminOrdersPage() {
  const { t } = useTranslation('admin')
  const label = useAdminLabel()
  const canManage = usePermission('orders.manage')
  const [page, setPage] = useState(1)
  const orders = useAdminOrders(page)
  const metadata = useAdminMetadata()
  const updateOrder = useUpdateOrder()

  return (
    <>
      <AdminHeader eyebrow={t('orders.eyebrow')} title={t('orders.title')} />
      <section className="admin-panel">
        <div className="admin-table admin-table--orders">
          <div className="admin-table__head">
            <span>{t('table.order')}</span>
            <span>{t('table.customer')}</span>
            <span>{t('table.placed')}</span>
            <span>{t('table.payment')}</span>
            <span>{t('table.total')}</span>
            <span>{t('table.status')}</span>
          </div>
          {orders.data?.items.map((order) => {
            let statusControl = <span>{label('status', order.status)}</span>

            if (canManage && metadata.data !== undefined) {
              statusControl = (
                <AdminStatusSelect
                  options={metadata.data.options.order_statuses}
                  value={order.status}
                  disabled={updateOrder.isPending}
                  onChange={(status) =>
                    updateOrder.mutate({
                      id: order.id,
                      input: { status, payment_status: order.payment_status },
                    })
                  }
                />
              )
            }

            return (
              <div className="admin-table__row" key={order.id}>
                <strong>{order.number}</strong>
                <span>
                  {order.customer_name}
                  <small>{order.customer_email}</small>
                </span>
                <span>{formatDate(order.created_at)}</span>
                <span className={`status status--${order.payment_status}`}>
                  {label('status', order.payment_status)}
                </span>
                <strong>{formatMoney(order.total)}</strong>
                {statusControl}
              </div>
            )
          })}
        </div>
        <AdminPagination pagination={orders.data?.pagination} onPageChange={setPage} />
      </section>
    </>
  )
}
