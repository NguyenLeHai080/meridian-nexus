import axios from 'axios'
import type { ApiErrorResponse } from './types'

export class ApiError extends Error {
  public readonly status: number | null
  public readonly code: string
  public readonly requestId: string | null
  public readonly fields: Record<string, string[]>
  public readonly details: Record<string, unknown>

  constructor(
    message: string,
    status: number | null,
    code: string,
    requestId: string | null = null,
    fields: Record<string, string[]> = {},
    details: Record<string, unknown> = {},
  ) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.requestId = requestId
    this.fields = fields
    this.details = details
  }
}

export function normalizeApiError(error: unknown): ApiError {
  if (error instanceof ApiError) {
    return error
  }

  if (axios.isAxiosError<ApiErrorResponse>(error)) {
    const payload = error.response?.data
    let message = payload?.message
    let code = payload?.error?.code

    if (!message) {
      if (error.code === 'ECONNABORTED') {
        message = 'The request timed out.'
      } else {
        message = 'The request could not be completed.'
      }
    }

    if (!code) {
      if (error.response) {
        code = 'HTTP_ERROR'
      } else {
        code = 'NETWORK_ERROR'
      }
    }

    return new ApiError(
      message,
      error.response?.status ?? null,
      code,
      payload?.request_id || error.response?.headers['x-request-id'] || null,
      payload?.errors ?? {},
      payload?.error?.details ?? {},
    )
  }

  let message = 'An unexpected error occurred.'

  if (error instanceof Error) {
    message = error.message
  }

  return new ApiError(message, null, 'CLIENT_ERROR')
}

export function getApiErrorMessage(error: unknown): string {
  return normalizeApiError(error).message
}
