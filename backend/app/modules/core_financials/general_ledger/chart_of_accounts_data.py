"""
Chart of Accounts data for Paksa Financial System
E-commerce and International Business focused structure
"""

from typing import List, Dict, Any

CHART_OF_ACCOUNTS_DATA: List[Dict[str, Any]] = [
    # 1. ASSETS
    # Current Assets
    {
        "account_code": "1000",
        "account_name": "ASSETS",
        "account_type": "asset",
        "parent_code": None,
        "is_active": True,
        "description": "All company assets"
    },
    {
        "account_code": "1010",
        "account_name": "Cash in Hand",
        "account_type": "asset",
        "parent_code": "1000",
        "is_active": True,
        "description": "Physical cash on premises"
    },
    {
        "account_code": "1020",
        "account_name": "Cash in Bank - Local (PKR)",
        "account_type": "asset",
        "parent_code": "1000",
        "is_active": True,
        "description": "Pakistani Rupee bank accounts"
    },
    {
        "account_code": "1021",
        "account_name": "Cash in Bank - USD (International)",
        "account_type": "asset",
        "parent_code": "1000",
        "is_active": True,
        "description": "US Dollar bank accounts for international operations"
    },
    {
        "account_code": "1022",
        "account_name": "Cash in Bank - SAR (KSA)",
        "account_type": "asset",
        "parent_code": "1000",
        "is_active": True,
        "description": "Saudi Riyal bank accounts for KSA operations"
    },
    {
        "account_code": "1030",
        "account_name": "Accounts Receivable (COD Payments Pending)",
        "account_type": "asset",
        "parent_code": "1000",
        "is_active": True,
        "description": "Cash on Delivery payments pending collection"
    },
    {
        "account_code": "1031",
        "account_name": "COD Receivable - FedEx",
        "account_type": "asset",
        "parent_code": "1030",
        "is_active": True,
        "description": "COD collections pending from FedEx"
    },
    {
        "account_code": "1032",
        "account_name": "COD Receivable - DHL",
        "account_type": "asset",
        "parent_code": "1030",
        "is_active": True,
        "description": "COD collections pending from DHL"
    },
    {
        "account_code": "1033",
        "account_name": "COD Receivable - TCS",
        "account_type": "asset",
        "parent_code": "1030",
        "is_active": True,
        "description": "COD collections pending from TCS"
    },
    {
        "account_code": "1034",
        "account_name": "COD Receivable - LCS",
        "account_type": "asset",
        "parent_code": "1030",
        "is_active": True,
        "description": "COD collections pending from LCS"
    },
    {
        "account_code": "1040",
        "account_name": "Inventory - Raw Materials (Fabric, Accessories)",
        "account_type": "asset",
        "parent_code": "1000",
        "is_active": True,
        "description": "Raw materials inventory for production"
    },
    {
        "account_code": "1045",
        "account_name": "Inventory - Finished Goods (Products Ready for Sale)",
        "account_type": "asset",
        "parent_code": "1000",
        "is_active": True,
        "description": "Finished products ready for sale"
    },
    {
        "account_code": "1050",
        "account_name": "Prepaid Expenses (Logistics, Marketing Prepayments)",
        "account_type": "asset",
        "parent_code": "1000",
        "is_active": True,
        "description": "Prepaid logistics and marketing expenses"
    },
    {
        "account_code": "1060",
        "account_name": "Deposits and Advances (Security, Vendor Deposits)",
        "account_type": "asset",
        "parent_code": "1000",
        "is_active": True,
        "description": "Security deposits and vendor advances"
    },
    
    # Non-Current Assets
    {
        "account_code": "1200",
        "account_name": "Office Equipment",
        "account_type": "asset",
        "parent_code": "1000",
        "is_active": True,
        "description": "Office equipment and machinery"
    },
    {
        "account_code": "1210",
        "account_name": "Furniture and Fixtures",
        "account_type": "asset",
        "parent_code": "1000",
        "is_active": True,
        "description": "Office furniture and fixtures"
    },
    {
        "account_code": "1220",
        "account_name": "Software Development Costs",
        "account_type": "asset",
        "parent_code": "1000",
        "is_active": True,
        "description": "Capitalized software development expenses"
    },
    {
        "account_code": "1230",
        "account_name": "Vehicles (Logistics)",
        "account_type": "asset",
        "parent_code": "1000",
        "is_active": True,
        "description": "Vehicles used for logistics and delivery"
    },

    # 2. LIABILITIES
    {
        "account_code": "2000",
        "account_name": "LIABILITIES",
        "account_type": "liability",
        "parent_code": None,
        "is_active": True,
        "description": "All company liabilities"
    },
    
    # Current Liabilities
    {
        "account_code": "2010",
        "account_name": "Accounts Payable - Local Vendors",
        "account_type": "liability",
        "parent_code": "2000",
        "is_active": True,
        "description": "Amounts owed to local Pakistani vendors"
    },
    {
        "account_code": "2020",
        "account_name": "Accounts Payable - International Vendors",
        "account_type": "liability",
        "parent_code": "2000",
        "is_active": True,
        "description": "Amounts owed to international vendors"
    },
    {
        "account_code": "2030",
        "account_name": "Salaries Payable",
        "account_type": "liability",
        "parent_code": "2000",
        "is_active": True,
        "description": "Accrued salaries and wages payable"
    },
    {
        "account_code": "2040",
        "account_name": "Tax Payable (Income Tax, VAT, Zakat)",
        "account_type": "liability",
        "parent_code": "2000",
        "is_active": True,
        "description": "All tax obligations"
    },
    {
        "account_code": "2050",
        "account_name": "Logistics Payable (Courier Partner Fees)",
        "account_type": "liability",
        "parent_code": "2000",
        "is_active": True,
        "description": "Amounts owed to logistics and courier partners"
    },
    {
        "account_code": "2060",
        "account_name": "Customer Refunds Payable",
        "account_type": "liability",
        "parent_code": "2000",
        "is_active": True,
        "description": "Customer refunds pending processing"
    },
    
    # Non-Current Liabilities
    {
        "account_code": "2200",
        "account_name": "Loans Payable",
        "account_type": "liability",
        "parent_code": "2000",
        "is_active": True,
        "description": "Long-term loans and financing"
    },
    {
        "account_code": "2210",
        "account_name": "Lease Obligations (Office, Warehouse)",
        "account_type": "liability",
        "parent_code": "2000",
        "is_active": True,
        "description": "Lease obligations for office and warehouse"
    },

    # 3. EQUITY
    {
        "account_code": "3000",
        "account_name": "EQUITY",
        "account_type": "equity",
        "parent_code": None,
        "is_active": True,
        "description": "Owner's equity and retained earnings"
    },
    {
        "account_code": "3010",
        "account_name": "Owner's Equity - Partner(s)",
        "account_type": "equity",
        "parent_code": "3000",
        "is_active": True,
        "description": "Partners' equity contributions"
    },
    {
        "account_code": "3020",
        "account_name": "Investor's Equity - Investor(s)",
        "account_type": "equity",
        "parent_code": "3000",
        "is_active": True,
        "description": "External investors' equity"
    },
    {
        "account_code": "3030",
        "account_name": "Retained Earnings",
        "account_type": "equity",
        "parent_code": "3000",
        "is_active": True,
        "description": "Accumulated retained earnings"
    },

    # 4. REVENUE
    {
        "account_code": "4000",
        "account_name": "REVENUE",
        "account_type": "revenue",
        "parent_code": None,
        "is_active": True,
        "description": "All revenue streams"
    },
    
    # Sales Revenue
    {
        "account_code": "4010",
        "account_name": "Sales - Local (Pakistan)",
        "account_type": "revenue",
        "parent_code": "4000",
        "is_active": True,
        "description": "Sales revenue from Pakistani market"
    },
    {
        "account_code": "4020",
        "account_name": "Sales - International (USA)",
        "account_type": "revenue",
        "parent_code": "4000",
        "is_active": True,
        "description": "Sales revenue from USA market"
    },
    {
        "account_code": "4030",
        "account_name": "Sales - Middle East (KSA, UAE)",
        "account_type": "revenue",
        "parent_code": "4000",
        "is_active": True,
        "description": "Sales revenue from Middle East markets"
    },
    {
        "account_code": "4040",
        "account_name": "Sales - Southeast Asia (India, Bangladesh)",
        "account_type": "revenue",
        "parent_code": "4000",
        "is_active": True,
        "description": "Sales revenue from Southeast Asian markets"
    },
    
    # Other Income
    {
        "account_code": "4110",
        "account_name": "Interest Income",
        "account_type": "revenue",
        "parent_code": "4000",
        "is_active": True,
        "description": "Interest earned on bank deposits and investments"
    },
    {
        "account_code": "4120",
        "account_name": "Discounts Received",
        "account_type": "revenue",
        "parent_code": "4000",
        "is_active": True,
        "description": "Discounts received from vendors"
    },
    {
        "account_code": "4130",
        "account_name": "Other Miscellaneous Income",
        "account_type": "revenue",
        "parent_code": "4000",
        "is_active": True,
        "description": "Other miscellaneous income sources"
    },

    # 5. COST OF GOODS SOLD (COGS)
    {
        "account_code": "5000",
        "account_name": "COST OF GOODS SOLD",
        "account_type": "expense",
        "parent_code": None,
        "is_active": True,
        "description": "Direct costs of goods sold"
    },
    {
        "account_code": "5010",
        "account_name": "Raw Material Costs (Fabric, Thread, Accessories)",
        "account_type": "expense",
        "parent_code": "5000",
        "is_active": True,
        "description": "Cost of raw materials for production"
    },
    {
        "account_code": "5020",
        "account_name": "Manufacturing Labor (Pattern Makers, Designers)",
        "account_type": "expense",
        "parent_code": "5000",
        "is_active": True,
        "description": "Direct labor costs for manufacturing"
    },
    {
        "account_code": "5030",
        "account_name": "Direct Overheads (Production Utilities)",
        "account_type": "expense",
        "parent_code": "5000",
        "is_active": True,
        "description": "Direct production overhead costs"
    },
    {
        "account_code": "5040",
        "account_name": "Freight Inwards (Import Costs for Raw Materials)",
        "account_type": "expense",
        "parent_code": "5000",
        "is_active": True,
        "description": "Import and freight costs for raw materials"
    },

    # 6. OPERATING EXPENSES
    {
        "account_code": "6000",
        "account_name": "OPERATING EXPENSES",
        "account_type": "expense",
        "parent_code": None,
        "is_active": True,
        "description": "All operating expenses"
    },
    
    # Marketing and Sales Expenses
    {
        "account_code": "6010",
        "account_name": "Digital Advertising (Google, Meta, TikTok Ads)",
        "account_type": "expense",
        "parent_code": "6000",
        "is_active": True,
        "description": "Digital advertising and social media marketing"
    },
    {
        "account_code": "6020",
        "account_name": "Marketplace Fees (Amazon, Noon, eBay)",
        "account_type": "expense",
        "parent_code": "6000",
        "is_active": True,
        "description": "E-commerce marketplace fees and commissions"
    },
    {
        "account_code": "6030",
        "account_name": "Discounts and Promotions",
        "account_type": "expense",
        "parent_code": "6000",
        "is_active": True,
        "description": "Customer discounts and promotional expenses"
    },
    {
        "account_code": "6040",
        "account_name": "Influencer and Affiliate Marketing Costs",
        "account_type": "expense",
        "parent_code": "6000",
        "is_active": True,
        "description": "Influencer partnerships and affiliate marketing"
    },
    
    # General and Administrative Expenses
    {
        "account_code": "6110",
        "account_name": "Salaries and Wages",
        "account_type": "expense",
        "parent_code": "6000",
        "is_active": True,
        "description": "Employee salaries and wages"
    },
    {
        "account_code": "6120",
        "account_name": "Rent and Utilities (Office and Warehouse)",
        "account_type": "expense",
        "parent_code": "6000",
        "is_active": True,
        "description": "Rent and utilities for office and warehouse"
    },
    {
        "account_code": "6130",
        "account_name": "Software Subscriptions (Shopify, ERP, SMM Tools)",
        "account_type": "expense",
        "parent_code": "6000",
        "is_active": True,
        "description": "Software subscriptions and SaaS tools"
    },
    {
        "account_code": "6140",
        "account_name": "Legal and Professional Fees",
        "account_type": "expense",
        "parent_code": "6000",
        "is_active": True,
        "description": "Legal, accounting, and professional services"
    },
    {
        "account_code": "6150",
        "account_name": "Travel Expenses",
        "account_type": "expense",
        "parent_code": "6000",
        "is_active": True,
        "description": "Business travel and transportation"
    },
    
    # Logistics and Delivery Expenses
    {
        "account_code": "6210",
        "account_name": "Local Delivery Charges (Pakistan)",
        "account_type": "expense",
        "parent_code": "6000",
        "is_active": True,
        "description": "Local delivery and shipping costs in Pakistan"
    },
    {
        "account_code": "6220",
        "account_name": "International Shipping Costs (FedEx, DHL)",
        "account_type": "expense",
        "parent_code": "6000",
        "is_active": True,
        "description": "International shipping and courier costs"
    },
    
    # Other Operating Expenses
    {
        "account_code": "6310",
        "account_name": "Repairs and Maintenance",
        "account_type": "expense",
        "parent_code": "6000",
        "is_active": True,
        "description": "Equipment and facility maintenance"
    },
    {
        "account_code": "6320",
        "account_name": "Depreciation",
        "account_type": "expense",
        "parent_code": "6000",
        "is_active": True,
        "description": "Depreciation of fixed assets"
    },

    # 7. TAXES
    {
        "account_code": "7000",
        "account_name": "TAXES",
        "account_type": "expense",
        "parent_code": None,
        "is_active": True,
        "description": "All tax expenses"
    },
    {
        "account_code": "7010",
        "account_name": "Income Tax (Corporate Tax)",
        "account_type": "expense",
        "parent_code": "7000",
        "is_active": True,
        "description": "Corporate income tax expenses"
    },
    {
        "account_code": "7020",
        "account_name": "Sales Tax Payable (USA, PK, KSA)",
        "account_type": "expense",
        "parent_code": "7000",
        "is_active": True,
        "description": "Sales tax obligations across markets"
    },
    {
        "account_code": "7030",
        "account_name": "VAT Payable (KSA)",
        "account_type": "expense",
        "parent_code": "7000",
        "is_active": True,
        "description": "Value Added Tax for KSA operations"
    },
    {
        "account_code": "7040",
        "account_name": "Zakat Payable (KSA)",
        "account_type": "expense",
        "parent_code": "7000",
        "is_active": True,
        "description": "Zakat obligations for KSA operations"
    },

    # Additional Currency Exchange Accounts
    {
        "account_code": "4140",
        "account_name": "Foreign Exchange Gains",
        "account_type": "revenue",
        "parent_code": "4000",
        "is_active": True,
        "description": "Gains from foreign currency transactions"
    },
    {
        "account_code": "6330",
        "account_name": "Foreign Exchange Losses",
        "account_type": "expense",
        "parent_code": "6000",
        "is_active": True,
        "description": "Losses from foreign currency transactions"
    }
]