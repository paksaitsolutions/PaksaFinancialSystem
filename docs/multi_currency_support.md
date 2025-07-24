# Multi-Currency Support Implementation

## Overview

This document outlines the implementation of multi-currency support in the Paksa Financial System. The feature allows the system to handle multiple currencies, exchange rates, and currency conversions throughout the application.

## Components Implemented

### Backend

1. **Currency Model**
   - Implemented a comprehensive currency model with support for ISO 4217 currency codes
   - Added support for currency symbols, decimal places, and status
   - Implemented base currency designation

2. **Exchange Rate Model**
   - Created an exchange rate model to store rates between currencies
   - Added support for different rate types (spot, forward, historical)
   - Implemented effective dates for historical rates

3. **Currency Service**
   - Implemented a service for managing currencies and exchange rates
   - Added methods for retrieving, creating, updating, and deleting currencies
   - Implemented exchange rate calculation with support for cross-rates

4. **API Endpoints**
   - Created endpoints for currency management
   - Implemented endpoints for exchange rate management
   - Added currency conversion endpoint

### Frontend

1. **Currency Service**
   - Implemented a service to interact with the currency API endpoints
   - Added methods for currency and exchange rate management
   - Implemented currency conversion functionality

2. **Multi-Currency Input Component**
   - Created a reusable component for multi-currency input
   - Added support for displaying original and converted values
   - Implemented automatic currency conversion

3. **Currency Management View**
   - Implemented a comprehensive view for managing currencies
   - Added exchange rate management functionality
   - Implemented currency conversion tools

4. **Currency Utilities**
   - Created utility functions for currency formatting
   - Implemented currency conversion helpers
   - Added support for currency symbols and decimal places

## Features

- **Currency Management**
  - Add, edit, and delete currencies
  - Set base currency for the system
  - Manage currency status (active/inactive)

- **Exchange Rate Management**
  - Add exchange rates between currencies
  - Support for different rate types
  - Historical exchange rates with effective dates

- **Currency Conversion**
  - Convert amounts between currencies
  - Automatic cross-rate calculation
  - Support for historical rates

- **Multi-Currency UI Components**
  - Currency selector with flags and symbols
  - Multi-currency input with automatic conversion
  - Currency formatting utilities

## Database Schema

The implementation adds two main tables to the database:

1. **currencies**
   - `id`: UUID primary key
   - `code`: ISO 4217 currency code (e.g., USD, EUR)
   - `name`: Currency name (e.g., US Dollar, Euro)
   - `symbol`: Currency symbol (e.g., $, €)
   - `decimal_places`: Number of decimal places
   - `status`: Currency status (active/inactive)
   - `is_base_currency`: Whether this is the base currency

2. **exchange_rates**
   - `id`: UUID primary key
   - `source_currency_id`: Source currency ID (foreign key)
   - `target_currency_id`: Target currency ID (foreign key)
   - `rate`: Exchange rate value
   - `effective_date`: Date for which the rate is valid
   - `rate_type`: Type of rate (spot, forward, historical)
   - `is_official`: Whether this is the official rate
   - `source`: Source of the rate (e.g., ECB, Manual)

## Usage

### Managing Currencies

1. Navigate to Settings > Currency Management
2. Use the interface to add, edit, or delete currencies
3. Set the base currency for the system

### Managing Exchange Rates

1. Navigate to Settings > Currency Management
2. Use the Exchange Rates section to add new rates
3. View current rates between currencies

### Currency Conversion

1. Use the Currency Conversion section to convert amounts
2. Select source and target currencies
3. Enter the amount to convert

### Using Multi-Currency Components

The `MultiCurrencyInput` component can be used in forms:

```vue
<MultiCurrencyInput
  v-model="amount"
  v-model:currency="currency"
  :original-value="originalAmount"
  :original-currency="originalCurrency"
  :show-original-value="true"
  @currency-change="handleCurrencyChange"
/>
```

## Integration with Other Modules

The multi-currency support integrates with other modules in the following ways:

1. **General Ledger**
   - Journal entries can be recorded in multiple currencies
   - Financial statements can be generated in different currencies

2. **Accounts Payable/Receivable**
   - Invoices and payments can be processed in multiple currencies
   - Exchange rate gains/losses are automatically calculated

3. **Reporting**
   - Reports can be generated in the base currency or any other currency
   - Historical exchange rates are used for accurate reporting

## Future Enhancements

- Add support for currency revaluation
- Implement exchange rate feeds from external providers
- Add currency risk management tools
- Implement multi-currency budgeting
- Add support for cryptocurrency