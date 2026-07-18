import { Outlet } from 'react-router-dom'
import type { ReactNode } from 'react'
import { useIsFetching } from '@tanstack/react-query'
import { queryKeys } from '@/core/query/query-keys'

export function AdminMain() {
  const activeRequests = useIsFetching({ queryKey: queryKeys.admin.root })
  let progress: ReactNode = null

  if (activeRequests > 0) {
    progress = <div className="admin-fetch-progress" aria-hidden="true" />
  }

  return (
    <main className="admin-main">
      {progress}
      <Outlet />
    </main>
  )
}
