import { describe, expect, it } from 'vitest'
import { ApiError, getApiErrorMessage, normalizeApiError } from './errors'

describe('normalizeApiError', () => {
  it('normalizes the backend error contract', () => {
    const error = normalizeApiError({
      isAxiosError: true,
      response: {
        status: 422,
        headers: { 'x-request-id': 'header-request-id' },
        data: {
          data: null,
          message: 'The given data was invalid.',
          error: { code: 'VALIDATION_FAILED' },
          errors: { email: ['Email is invalid.'] },
          request_id: 'body-request-id',
        },
      },
    })

    expect(error).toBeInstanceOf(ApiError)
    expect(error.status).toBe(422)
    expect(error.code).toBe('VALIDATION_FAILED')
    expect(error.requestId).toBe('body-request-id')
    expect(error.fields.email).toEqual(['Email is invalid.'])
  })

  it('normalizes network failures without exposing implementation details', () => {
    const error = normalizeApiError({ isAxiosError: true, code: 'ERR_NETWORK' })

    expect(error.status).toBeNull()
    expect(error.code).toBe('NETWORK_ERROR')
    expect(error.message).toBe('The request could not be completed.')
  })

  it('preserves normalized errors', () => {
    const original = new ApiError('Already normalized', 409, 'CONFLICT')

    expect(normalizeApiError(original)).toBe(original)
  })

  it('normalizes timeouts and HTTP responses without an API payload', () => {
    const timeout = normalizeApiError({ isAxiosError: true, code: 'ECONNABORTED' })
    const responseError = normalizeApiError({
      isAxiosError: true,
      response: { status: 503, headers: {}, data: null },
    })

    expect(timeout.message).toBe('The request timed out.')
    expect(responseError.code).toBe('HTTP_ERROR')
    expect(responseError.status).toBe(503)
  })

  it('normalizes client errors and exposes their safe message', () => {
    expect(getApiErrorMessage(new Error('Invalid client state'))).toBe('Invalid client state')
    expect(normalizeApiError('unexpected').message).toBe('An unexpected error occurred.')
  })
})
