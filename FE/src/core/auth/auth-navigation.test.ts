import { describe, expect, it } from 'vitest'
import type { AuthenticatedUser } from './auth.types'
import { getPostLoginPath } from './auth-navigation'

function user(permissions: string[]): AuthenticatedUser {
  return {
    id: 1,
    name: 'Test User',
    email: 'test@example.com',
    email_verified_at: null,
    mfa_enabled: true,
    created_at: '2026-07-18T00:00:00Z',
    roles: [],
    permissions,
  }
}

describe('getPostLoginPath', () => {
  it('sends back-office users to the admin route', () => {
    expect(getPostLoginPath(user(['dashboard.view']))).toBe('/admin')
  })

  it('sends customers to their storefront profile', () => {
    expect(getPostLoginPath(user([]))).toBe('/profile')
  })

  it('sends privileged users without MFA to enrollment', () => {
    const privileged = user(['dashboard.view'])
    privileged.roles = ['admin']
    privileged.mfa_enabled = false
    expect(getPostLoginPath(privileged)).toBe('/profile')
  })
})
