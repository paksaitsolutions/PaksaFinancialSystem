import { test, expect } from '@playwright/test'

test.describe('Accounts Receivable Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
    await page.fill('[data-testid="email-input"]', 'admin@paksa.com')
    await page.fill('[data-testid="password-input"]', 'admin123')
    await page.click('[data-testid="login-button"]')
    await expect(page).toHaveURL('/dashboard')
  })

  test('should create customer and invoice', async ({ page }) => {
    // Create customer
    await page.goto('/ar/customers')
    await page.click('[data-testid="add-customer-button"]')
    await page.fill('[data-testid="customer-name"]', 'Test Customer')
    await page.fill('[data-testid="customer-email"]', 'customer@test.com')
    await page.click('[data-testid="save-customer"]')
    
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible()
    
    // Create invoice
    await page.goto('/ar/invoices')
    await page.click('[data-testid="add-invoice-button"]')
    await page.selectOption('[data-testid="customer-select"]', { label: 'Test Customer' })
    await page.fill('[data-testid="invoice-amount"]', '2000.00')
    await page.fill('[data-testid="due-date"]', '2024-12-31')
    await page.click('[data-testid="save-invoice"]')
    
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible()
    await expect(page.locator('[data-testid="invoice-list"]')).toContainText('Test Customer')
  })

  test('should record payment for invoice', async ({ page }) => {
    await page.goto('/ar/invoices')
    
    // Find and click on first invoice
    await page.click('[data-testid="invoice-row"]:first-child [data-testid="record-payment"]')
    
    await page.fill('[data-testid="payment-amount"]', '2000.00')
    await page.selectOption('[data-testid="payment-method"]', 'bank_transfer')
    await page.click('[data-testid="record-payment-button"]')
    
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible()
    await expect(page.locator('[data-testid="invoice-status"]')).toContainText('Paid')
  })

  test('should generate aging report', async ({ page }) => {
    await page.goto('/ar/reports')
    
    await page.click('[data-testid="aging-report-button"]')
    await page.selectOption('[data-testid="aging-period"]', '30')
    await page.click('[data-testid="generate-report"]')
    
    await expect(page.locator('[data-testid="report-table"]')).toBeVisible()
    await expect(page.locator('[data-testid="export-button"]')).toBeVisible()
  })
})