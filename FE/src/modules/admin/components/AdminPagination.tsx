import type { PaginationMeta } from '@/core/api/types'
import { useTranslation } from 'react-i18next'

interface AdminPaginationProps {
  pagination: PaginationMeta['pagination'] | undefined
  onPageChange: (page: number) => void
}

export function AdminPagination({ pagination, onPageChange }: AdminPaginationProps) {
  const { t } = useTranslation('admin')
  if (pagination === undefined || pagination.last_page <= 1) {
    return null
  }

  return (
    <nav className="admin-pagination" aria-label={t('pagination.label')}>
      <button
        type="button"
        aria-label={t('pagination.previous')}
        disabled={pagination.current_page === 1}
        onClick={() => onPageChange(pagination.current_page - 1)}
      >
        &larr;
      </button>
      <span>
        {pagination.current_page} / {pagination.last_page}
      </span>
      <button
        type="button"
        aria-label={t('pagination.next')}
        disabled={pagination.current_page === pagination.last_page}
        onClick={() => onPageChange(pagination.current_page + 1)}
      >
        &rarr;
      </button>
    </nav>
  )
}
