import { test, expect } from '@playwright/test'

test.describe('Smoke Suite', () => {
  test('login, posting access, and reporting access', async ({ page }) => {
    await page.goto('/login')
    await page.fill('[data-testid="email-input"]', 'admin@paksa.com')
    await page.fill('[data-testid="password-input"]', 'admin123')
    await page.click('[data-testid="login-button"]')

    await expect(page).toHaveURL('/dashboard')

    await page.goto('/ap/bills')
    await expect(page.locator('[data-testid="add-bill-button"]')).toBeVisible()

    await page.goto('/reports')
    await expect(page.getByRole('heading', { name: 'All Reports' })).toBeVisible()
  })
})
