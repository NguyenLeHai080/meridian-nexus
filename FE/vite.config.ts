import { loadEnv, type Plugin } from 'vite'
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'node:path'

function securityPolicyPlugin(policy: string): Plugin {
  return {
    name: 'northstar-security-policy',
    transformIndexHtml() {
      return [
        {
          tag: 'meta',
          injectTo: 'head-prepend',
          attrs: {
            'http-equiv': 'Content-Security-Policy',
            content: policy,
          },
        },
      ]
    },
  }
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), 'VITE_')
  let backendOrigin = ''
  if (!env.VITE_BACKEND_URL.startsWith('/')) {
    backendOrigin = new URL(env.VITE_BACKEND_URL).origin
  }
  let developmentScriptSource = ''
  let developmentConnectSource = ''
  if (mode !== 'production') {
    developmentScriptSource = " 'unsafe-inline'"
    developmentConnectSource = ' ws://localhost:*'
  }
  const contentSecurityPolicy = [
    "default-src 'self'",
    "base-uri 'self'",
    "object-src 'none'",
    "frame-ancestors 'none'",
    "form-action 'self'",
    `script-src 'self'${developmentScriptSource}`,
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' data: https://fonts.gstatic.com",
    "img-src 'self' data: https:",
    `connect-src 'self' ${backendOrigin}${developmentConnectSource}`,
    "manifest-src 'self'",
    "worker-src 'self'",
  ].join('; ')

  return {
    plugins: [react(), securityPolicyPlugin(contentSecurityPolicy)],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      headers: {
        'Cross-Origin-Opener-Policy': 'same-origin',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
      },
    },
    test: {
      environment: 'jsdom',
      setupFiles: './src/test/setup.ts',
    },
  }
})
