import axios from 'axios'
import { env } from '@/core/config/env'

let csrfRequest: Promise<void> | null = null

export function initializeCsrfProtection(): Promise<void> {
  if (!csrfRequest) {
    csrfRequest = axios
      .get(`${env.backendUrl}/sanctum/csrf-cookie`, {
        headers: { Accept: 'application/json' },
        withCredentials: true,
      })
      .then(() => undefined)
      .catch((error: unknown) => {
        csrfRequest = null
        throw error
      })
  }

  return csrfRequest
}

export function resetCsrfProtection(): void {
  csrfRequest = null
}
