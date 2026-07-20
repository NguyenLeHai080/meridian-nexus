import { expect, test } from '@playwright/test'

test('loads the storefront and navigates to the catalog', async ({ page }) => {
  await page.goto('/')

  await expect(page.getByRole('heading', { name: 'Services Built for Growth' })).toBeVisible()
  await page.getByRole('link', { name: 'Read More' }).first().click({ force: true })

  await expect(page).toHaveURL(/\/products$/)
  await expect(page.getByRole('heading', { name: 'Objects for everyday rituals.' })).toBeVisible()
})

test('registers a customer through the real API', async ({ page }) => {
  const email = `e2e-${Date.now()}-${test.info().workerIndex}@example.com`

  await page.goto('/register')
  await page.getByLabel('Full name').fill('E2E Customer')
  await page.getByLabel('Work email').fill(email)
  await page.getByLabel('Password', { exact: true }).fill('SecurePassword123!')
  await page.getByLabel('Confirm password').fill('SecurePassword123!')
  await page.getByRole('button', { name: 'Create account' }).click()

  await expect(page).toHaveURL(/\/profile$/)
  await expect(page.getByRole('heading', { name: /Welcome back,/ })).toBeVisible()
  await expect(page.getByText(email)).toBeVisible()
})
