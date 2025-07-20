# Tax Module User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Managing Tax Transactions](#managing-tax-transactions)
4. [Tax Rates Management](#tax-rates-management)
5. [Reports](#reports)
6. [Troubleshooting](#troubleshooting)

## Introduction
The Tax Module helps you manage all tax-related transactions, calculations, and reporting in one place. It supports various tax types, including VAT, GST, and sales tax, with multi-jurisdiction support.

## Getting Started

### Prerequisites
- Access to the Paksa Financial System
- Appropriate user permissions for tax management
- Company tax information set up

### Accessing the Tax Module
1. Log in to your Paksa Financial System account
2. Navigate to the main menu
3. Select "Tax" from the navigation panel

## Managing Tax Transactions

### Creating a Tax Transaction
1. Go to **Tax** > **Transactions**
2. Click **New Transaction**
3. Fill in the transaction details:
   - Transaction Date
   - Document Number
   - Transaction Type (Sale/Purchase/Refund)
   - Tax Type (VAT/GST/Sales Tax)
4. Add line items with amounts and tax rates
5. Review the calculated tax amounts
6. Click **Save as Draft** or **Post**

### Posting a Draft Transaction
1. Go to **Tax** > **Transactions**
2. Find your draft transaction
3. Click **Post**
4. Confirm the action

### Voiding a Transaction
1. Go to **Tax** > **Transactions**
2. Find the posted transaction
3. Click **Void**
4. Enter a reason for voiding
5. Confirm the action

## Tax Rates Management

### Viewing Tax Rates
1. Go to **Tax** > **Tax Rates**
2. View the list of available tax rates
3. Use filters to find specific rates

### Adding a New Tax Rate
1. Go to **Tax** > **Tax Rates**
2. Click **Add New Rate**
3. Fill in the details:
   - Rate Name
   - Tax Rate (percentage or fixed amount)
   - Effective Date Range
   - Status (Active/Inactive)
4. Click **Save**

## Reports

### Tax Liability Report
1. Go to **Reports** > **Tax** > **Tax Liability**
2. Select the date range
3. Choose tax type (optional)
4. Click **Generate Report**
5. Export as needed (PDF/Excel/CSV)

### Tax Transaction Report
1. Go to **Reports** > **Tax** > **Transaction Report**
2. Set your filters:
   - Date Range
   - Status
   - Tax Type
   - Document Number
3. Click **Generate**

## Troubleshooting

### Common Issues

#### Tax Calculation is Incorrect
- Verify the tax rate is correctly set
- Check if the amount is inclusive/exclusive of tax
- Ensure the correct tax type is selected

#### Can't Post a Transaction
- Check if all required fields are filled
- Verify you have the necessary permissions
- Ensure the transaction date is within an open period

#### Tax Rate Not Available
- Check if the tax rate is active
- Verify the effective date range
- Contact your system administrator if needed

### Getting Help
For additional assistance:
- Check the [API Documentation](API_REFERENCE.md)
- Contact Support: support@paksa.com
- Visit our [Help Center](https://help.paksa.com)

## Best Practices
1. Always review tax calculations before posting
2. Keep tax rates up to date with current regulations
3. Run tax reports periodically for reconciliation
4. Maintain proper documentation for tax audits
5. Regularly back up your tax data

## Security
- All tax data is encrypted at rest and in transit
- Access to tax functions is controlled by role-based permissions
- All changes are logged for audit purposes
