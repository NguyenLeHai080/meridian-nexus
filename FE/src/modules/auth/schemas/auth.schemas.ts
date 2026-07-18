import { z } from 'zod'

type Translate = (key: string) => string

const englishMessages: Record<string, string> = {
  'validation.email': 'Enter a valid email address.',
  'validation.passwordRequired': 'Password is required.',
  'validation.nameMin': 'Name must contain at least 2 characters.',
  'validation.passwordMin': 'Use at least 12 characters.',
  'validation.passwordLowercase': 'Add at least one lowercase letter.',
  'validation.passwordUppercase': 'Add at least one uppercase letter.',
  'validation.passwordNumber': 'Add at least one number.',
  'validation.passwordSymbol': 'Add at least one symbol.',
  'validation.passwordMismatch': 'Passwords do not match.',
}

function translateEnglish(key: string): string {
  return englishMessages[key] || key
}

export function createLoginSchema(t: Translate) {
  return z.object({
    email: z.email(t('validation.email')),
    password: z.string().min(1, t('validation.passwordRequired')),
  })
}

export function createRegisterSchema(t: Translate) {
  return z
    .object({
      name: z.string().trim().min(2, t('validation.nameMin')).max(100),
      email: z.email(t('validation.email')),
      password: z
        .string()
        .min(12, t('validation.passwordMin'))
        .regex(/[a-z]/, t('validation.passwordLowercase'))
        .regex(/[A-Z]/, t('validation.passwordUppercase'))
        .regex(/\d/, t('validation.passwordNumber'))
        .regex(/[^A-Za-z0-9]/, t('validation.passwordSymbol')),
      password_confirmation: z.string(),
    })
    .refine((input) => input.password === input.password_confirmation, {
      path: ['password_confirmation'],
      message: t('validation.passwordMismatch'),
    })
}

export const loginSchema = createLoginSchema(translateEnglish)
export const registerSchema = createRegisterSchema(translateEnglish)

export type LoginFormValues = z.infer<typeof loginSchema>
export type RegisterFormValues = z.infer<typeof registerSchema>
