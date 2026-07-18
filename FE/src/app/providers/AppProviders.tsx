import { QueryClientProvider } from '@tanstack/react-query'
import type { PropsWithChildren } from 'react'
import { AuthBootstrap } from '@/core/auth/AuthBootstrap'
import { AppErrorBoundary } from '@/core/errors/AppErrorBoundary'
import { queryClient } from '@/core/query/query-client'

export function AppProviders({ children }: PropsWithChildren) {
  return (
    <AppErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AuthBootstrap>{children}</AuthBootstrap>
      </QueryClientProvider>
    </AppErrorBoundary>
  )
}
