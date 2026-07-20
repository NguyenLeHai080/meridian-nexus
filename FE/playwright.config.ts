import { defineConfig, devices } from '@playwright/test'

const backendCommand =
  process.env.E2E_BACKEND_COMMAND ??
  '.\\.venv\\Scripts\\python.exe -m uvicorn northstar.main:app --host 127.0.0.1 --port 8010 --no-server-header'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? [['html', { open: 'never' }], ['github']] : 'list',
  use: {
    baseURL: 'http://127.0.0.1:5174',
    locale: 'en-US',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: [
    {
      command: backendCommand,
      cwd: '../BE',
      url: 'http://127.0.0.1:8010/health',
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      env: {
        ...process.env,
        APP_ENV: 'local',
        APP_KEY: 'e2e-only-key-with-at-least-32-characters',
        DATABASE_URL: 'sqlite:///./data/e2e.sqlite',
        FRONTEND_ORIGINS: 'http://127.0.0.1:5174',
        FRONTEND_URL: 'http://127.0.0.1:5174',
        TRUSTED_HOSTS: 'localhost,127.0.0.1',
      },
    },
    {
      command: 'npm run dev -- --host 127.0.0.1 --port 5174',
      url: 'http://127.0.0.1:5174',
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      env: {
        ...process.env,
        VITE_API_URL: 'http://127.0.0.1:8010/api/v1',
        VITE_BACKEND_URL: 'http://127.0.0.1:8010',
        VITE_APP_NAME: 'Meridian Nexus E2E',
      },
    },
  ],
})
