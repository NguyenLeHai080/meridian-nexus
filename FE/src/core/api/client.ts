import axios from 'axios'
import { useAuthStore } from '@/core/auth/auth-store'
import { env } from '@/core/config/env'
import { i18n } from '@/core/i18n/i18n'
import { initializeCsrfProtection, resetCsrfProtection } from './csrf'
import { normalizeApiError } from './errors'

interface RetryableRequestConfig {
  _csrfRetried?: boolean
}

export const apiClient = axios.create({
  baseURL: env.apiUrl,
  headers: { Accept: 'application/json' },
  timeout: 15_000,
  withCredentials: true,
  withXSRFToken: true,
})

apiClient.interceptors.request.use(async (config) => {
  const method = config.method?.toLowerCase()

  if (method && ['post', 'put', 'patch', 'delete'].includes(method)) {
    await initializeCsrfProtection()
  }

  config.headers.set('X-Request-ID', crypto.randomUUID())
  config.headers.set('Accept-Language', i18n.resolvedLanguage || i18n.language || 'en')

  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config as (typeof error.config & RetryableRequestConfig) | undefined

    if (error.response?.status === 419 && config && !config._csrfRetried) {
      config._csrfRetried = true
      resetCsrfProtection()
      await initializeCsrfProtection()

      return apiClient.request(config)
    }

    if (error.response?.status === 401) {
      useAuthStore.getState().clearSession()
    }

    return Promise.reject(normalizeApiError(error))
  },
)

export function createIdempotencyKey(): string {
  return crypto.randomUUID()
}
