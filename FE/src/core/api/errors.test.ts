import { describe, expect, it } from 'vitest'
import { ApiError, normalizeApiError } from './errors'

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
})
