import { useEffect, type PropsWithChildren } from 'react'
import { useAuthStore } from './auth-store'
import { PageLoader } from '@/shared/components/PageLoader'
import { getAuthSession } from './session-api'

export function AuthBootstrap({ children }: PropsWithChildren) {
  const initialized = useAuthStore((state) => state.initialized)
  const setUser = useAuthStore((state) => state.setUser)
  const markInitialized = useAuthStore((state) => state.markInitialized)
  const clearSession = useAuthStore((state) => state.clearSession)

  useEffect(() => {
    getAuthSession()
      .then((session) => setUser(session.user))
      .catch(clearSession)
      .finally(markInitialized)
  }, [clearSession, markInitialized, setUser])

  if (!initialized) {
    return <PageLoader label="Restoring your workspace" />
  }

  return children
}
