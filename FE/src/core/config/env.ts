import { z } from 'zod'

const endpointSchema = z.string().refine((value) => {
  if (value.startsWith('/')) {
    return true
  }
  return z.url().safeParse(value).success
}, 'Must be an absolute URL or a same-origin path')

const environmentSchema = z.object({
  VITE_API_URL: endpointSchema,
  VITE_BACKEND_URL: endpointSchema,
  VITE_APP_NAME: z.string().trim().min(1).default('Northstar'),
})

const result = environmentSchema.safeParse(import.meta.env)

if (!result.success) {
  const invalidKeys = result.error.issues.map((issue) => issue.path.join('.')).join(', ')
  throw new Error(`Invalid application environment: ${invalidKeys}`)
}

export const env = Object.freeze({
  apiUrl: result.data.VITE_API_URL.replace(/\/$/, ''),
  backendUrl: result.data.VITE_BACKEND_URL.replace(/\/$/, ''),
  appName: result.data.VITE_APP_NAME,
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
})
