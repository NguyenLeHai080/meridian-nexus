import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { usePermission } from '@/core/auth/use-permission'
import { formatMoney } from '@/modules/commerce/utils/format'
import { AdminHeader } from '../components/AdminHeader'
import { PromotionCreateForm } from '../components/forms/PromotionCreateForm'
import { useAdminMetadata, useAdminPromotions, useCreatePromotion } from '../hooks/use-admin-data'

export function AdminPromotionsPage() {
  const { t } = useTranslation('admin')
  const canManage = usePermission('promotions.manage')
  const [creating, setCreating] = useState(false)
  const promotions = useAdminPromotions()
  const metadata = useAdminMetadata(creating)
  const createPromotion = useCreatePromotion(() => setCreating(false))

  return (
    <>
      <AdminHeader
        eyebrow={t('promotions.eyebrow')}
        title={t('promotions.title')}
        action={
          canManage && (
            <button className="admin-button" onClick={() => setCreating((open) => !open)}>
              {t('promotions.new')}
            </button>
          )
        }
      />
      {creating && metadata.data && (
        <PromotionCreateForm
          metadata={metadata.data}
          pending={createPromotion.isPending}
          onSubmit={createPromotion.mutate}
        />
      )}
      <div className="promotion-admin-grid">
        {promotions.data?.map((promotion) => {
          let activityLabel = t('promotions.inactive')
          let promotionValue = formatMoney(Number(promotion.value))
          if (promotion.is_active) {
            activityLabel = t('promotions.active')
          }
          if (promotion.type === 'percent') {
            promotionValue = `${promotion.value}%`
          }

          return (
            <article key={promotion.id}>
              <span>{activityLabel}</span>
              <h2>{promotion.name}</h2>
              <code>{promotion.code || t('promotions.automatic')}</code>
              <strong>{t('promotions.off', { value: promotionValue })}</strong>
              <p>
                {t('promotions.minimum', { value: formatMoney(Number(promotion.minimum_order)) })}
              </p>
            </article>
          )
        })}
      </div>
    </>
  )
}
