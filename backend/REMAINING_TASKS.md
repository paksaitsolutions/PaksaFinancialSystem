# Remaining Critical Tasks

## High Priority (Must Complete)
1. ❌ Delete duplicate model directories: `accounts_payable/` and `accounts_receivable/`
2. ❌ Implement AP invoice → GL journal entry auto-posting
3. ❌ Implement AR invoice → GL journal entry auto-posting
4. ❌ Implement cash transaction → GL journal entry auto-posting
5. ❌ Update all API endpoints to use unified models
6. ❌ Update all database migrations to use unified table names

## Medium Priority
7. ❌ Add GL integration service layer
8. ❌ Implement cross-module financial reporting
9. ❌ Add bank reconciliation GL integration
10. ❌ Update all test files to use unified models

## Low Priority
11. ❌ Clean up unused model files
12. ❌ Update documentation to reflect unified architecture
13. ❌ Add data migration scripts for existing deployments

## Completed Tasks ✅
- Updated `ar_service.py` to use unified models
- Updated `ap_service.py` to use unified models  
- Updated `cash_service.py` to use BankAccount/BankTransaction
- Fixed AP invoice line items foreign key references
- Added cash management models to unified imports
- GL models integrated with unified chart of accounts
- All services now import from unified `app.models`