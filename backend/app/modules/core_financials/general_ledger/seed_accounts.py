"""
Seed script to populate Chart of Accounts with business-specific structure
"""

from sqlalchemy.orm import Session
from app.core.db.base import get_db
from app.modules.core_financials.general_ledger.models import GLAccount
from .chart_of_accounts_data import CHART_OF_ACCOUNTS_DATA
import logging

logger = logging.getLogger(__name__)

def seed_chart_of_accounts(db: Session) -> bool:
    """
    Seed the database with the comprehensive Chart of Accounts
    """
    try:
        # Check if accounts already exist
        existing_count = db.query(GLAccount).count()
        if existing_count > 0:
            logger.info(f"Chart of Accounts already exists with {existing_count} accounts")
            return True

        # Create accounts in order (parent accounts first)
        created_accounts = {}
        
        for account_data in CHART_OF_ACCOUNTS_DATA:
            # Find parent account if specified
            parent_id = None
            if account_data.get('parent_code'):
                parent_account = created_accounts.get(account_data['parent_code'])
                if parent_account:
                    parent_id = parent_account.id
                else:
                    # Find existing parent account
                    parent_account = db.query(GLAccount).filter(
                        GLAccount.account_code == account_data['parent_code']
                    ).first()
                    if parent_account:
                        parent_id = parent_account.id

            # Create the account
            account = GLAccount(
                account_code=account_data['account_code'],
                account_name=account_data['account_name'],
                account_type=account_data['account_type'],
                parent_id=parent_id,
                is_active=account_data.get('is_active', True),
                description=account_data.get('description', ''),
                balance=0.00,
                currency_code='PKR'  # Default currency
            )
            
            db.add(account)
            db.flush()  # Get the ID without committing
            
            # Store for parent reference
            created_accounts[account_data['account_code']] = account
            
            logger.info(f"Created account: {account.account_code} - {account.account_name}")

        # Commit all accounts
        db.commit()
        
        total_created = len(created_accounts)
        logger.info(f"Successfully created {total_created} accounts in Chart of Accounts")
        
        return True
        
    except Exception as e:
        logger.error(f"Error seeding Chart of Accounts: {str(e)}")
        db.rollback()
        return False

def update_account_balances(db: Session) -> bool:
    """
    Update account balances with sample data for demonstration
    """
    try:
        sample_balances = {
            '1010': 50000.00,      # Cash in Hand
            '1020': 2500000.00,    # Cash in Bank - PKR
            '1021': 150000.00,     # Cash in Bank - USD
            '1022': 75000.00,      # Cash in Bank - SAR
            '1030': 125000.00,     # Accounts Receivable
            '1040': 300000.00,     # Raw Materials Inventory
            '1045': 450000.00,     # Finished Goods Inventory
            '2010': 180000.00,     # Accounts Payable - Local
            '2020': 95000.00,      # Accounts Payable - International
            '2030': 85000.00,      # Salaries Payable
            '3030': 1500000.00,    # Retained Earnings
            '4010': 2800000.00,    # Sales - Local
            '4020': 1200000.00,    # Sales - USA
            '4030': 800000.00,     # Sales - Middle East
            '5010': 800000.00,     # Raw Material Costs
            '6010': 150000.00,     # Digital Advertising
            '6020': 95000.00,      # Marketplace Fees
            '6110': 450000.00,     # Salaries and Wages
            '6120': 120000.00,     # Rent and Utilities
        }
        
        for account_code, balance in sample_balances.items():
            account = db.query(GLAccount).filter(
                GLAccount.account_code == account_code
            ).first()
            
            if account:
                account.balance = balance
                logger.info(f"Updated balance for {account_code}: {balance}")
        
        db.commit()
        logger.info("Successfully updated sample account balances")
        return True
        
    except Exception as e:
        logger.error(f"Error updating account balances: {str(e)}")
        db.rollback()
        return False

def get_account_hierarchy(db: Session) -> dict:
    """
    Get the complete account hierarchy for display
    """
    try:
        accounts = db.query(GLAccount).order_by(GLAccount.account_code).all()
        
        # Build hierarchy
        hierarchy = {}
        account_map = {acc.id: acc for acc in accounts}
        
        for account in accounts:
            if account.parent_id is None:
                # Root account
                hierarchy[account.account_code] = {
                    'account': account,
                    'children': []
                }
            else:
                # Find parent in hierarchy and add as child
                parent = account_map.get(account.parent_id)
                if parent:
                    parent_entry = hierarchy.get(parent.account_code)
                    if parent_entry:
                        parent_entry['children'].append({
                            'account': account,
                            'children': []
                        })
        
        return hierarchy
        
    except Exception as e:
        logger.error(f"Error building account hierarchy: {str(e)}")
        return {}

# CLI function for manual seeding
def main():
    """
    Main function to seed accounts from command line
    """
    db = next(get_db())
    
    print("Seeding Chart of Accounts...")
    success = seed_chart_of_accounts(db)
    
    if success:
        print("Chart of Accounts seeded successfully!")
        
        print("Updating sample balances...")
        balance_success = update_account_balances(db)
        
        if balance_success:
            print("Sample balances updated successfully!")
        else:
            print("Failed to update sample balances")
    else:
        print("Failed to seed Chart of Accounts")
    
    db.close()

if __name__ == "__main__":
    main()