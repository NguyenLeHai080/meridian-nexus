import { describe, expect, it } from 'vitest'
import {
  createLoginSchema,
  createRegisterSchema,
  loginSchema,
  registerSchema,
} from './auth.schemas'

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

  it('accepts a valid registration and uses translated validation messages', () => {
    const translate = (key: string) => `translated:${key}`
    const translatedLogin = createLoginSchema(translate)
    const translatedRegister = createRegisterSchema(translate)

    expect(
      translatedRegister.safeParse({
        name: 'Ada Lovelace',
        email: 'ada@example.com',
        password: 'SecurePassword123!',
        password_confirmation: 'SecurePassword123!',
      }).success,
    ).toBe(true)

    const invalidLogin = translatedLogin.safeParse({ email: 'invalid', password: '' })
    expect(invalidLogin.error?.issues.map((issue) => issue.message)).toContain(
      'translated:validation.email',
    )
  })
})
