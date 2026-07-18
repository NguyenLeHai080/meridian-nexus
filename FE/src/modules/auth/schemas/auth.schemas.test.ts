import { describe, expect, it } from 'vitest'
import { loginSchema, registerSchema } from './auth.schemas'

describe('auth schemas', () => {
  it('accepts valid login credentials', () => {
    expect(loginSchema.safeParse({ email: 'ada@example.com', password: 'secret' }).success).toBe(
      true,
    )
  })

  it('rejects mismatched registration passwords', () => {
    const result = registerSchema.safeParse({
      name: 'Ada Lovelace',
      email: 'ada@example.com',
      password: 'SecurePassword123!',
      password_confirmation: 'DifferentPassword123!',
    })

    expect(result.success).toBe(false)
  })
})
