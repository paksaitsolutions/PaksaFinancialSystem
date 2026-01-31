import { test, expect } from '@playwright/test'

test.describe('Accounts Payable Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login')
    await page.fill('[data-testid="email-input"]', 'admin@paksa.com')
    await page.fill('[data-testid="password-input"]', 'admin123')
    await page.click('[data-testid="login-button"]')
    await expect(page).toHaveURL('/dashboard')
  })

  test('should navigate to AP dashboard', async ({ page }) => {
    await page.click('[data-testid="ap-menu"]')
    await page.click('[data-testid="ap-dashboard"]')
    
    await expect(page).toHaveURL('/ap/dashboard')
    await expect(page.locator('h1')).toContainText('Accounts Payable')
  })

  test('should create new vendor', async ({ page }) => {
    await page.goto('/ap/vendors')
    
    await page.click('[data-testid="add-vendor-button"]')
    await page.fill('[data-testid="vendor-name"]', 'Test Vendor')
    await page.fill('[data-testid="vendor-email"]', 'vendor@test.com')
    await page.fill('[data-testid="vendor-phone"]', '123-456-7890')
    await page.click('[data-testid="save-vendor"]')
    
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible()
    await expect(page.locator('[data-testid="vendor-list"]')).toContainText('Test Vendor')
  })

  test('should create and process bill', async ({ page }) => {
    await page.goto('/ap/bills')
    
    await page.click('[data-testid="add-bill-button"]')
    await page.selectOption('[data-testid="vendor-select"]', { label: 'Test Vendor' })
    await page.fill('[data-testid="bill-number"]', 'BILL-001')
    await page.fill('[data-testid="bill-amount"]', '1000.00')
    await page.fill('[data-testid="due-date"]', '2024-12-31')
    await page.click('[data-testid="save-bill"]')
    
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible()
    
    // Process payment
    await page.click('[data-testid="pay-bill-button"]')
    await page.fill('[data-testid="payment-amount"]', '1000.00')
    await page.selectOption('[data-testid="payment-method"]', 'bank_transfer')
    await page.click('[data-testid="process-payment"]')
    
    await expect(page.locator('[data-testid="bill-status"]')).toContainText('Paid')
  })
})