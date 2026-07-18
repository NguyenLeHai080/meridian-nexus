import { z } from 'zod'

const environmentSchema = z.object({
  VITE_API_URL: z.url(),
  VITE_BACKEND_URL: z.url(),
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
