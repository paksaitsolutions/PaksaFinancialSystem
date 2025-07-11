from datetime import date
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ...models.gl.account import GLAccount
from ...models.gl.journal_entry import JournalEntry, JournalEntryLine
from ...schemas.gl.trial_balance import TrialBalance, TrialBalanceEntry

class TrialBalanceService:
    @staticmethod
    def get_trial_balance(
        db: Session, 
        start_date: date, 
        end_date: date, 
        include_zeros: bool = False
    ) -> TrialBalance:
        """
        Generate a trial balance for the given date range
        """
        # Get all active GL accounts
        accounts = db.query(GLAccount).filter(GLAccount.is_active == True).all()
        
        # Initialize trial balance entries
        entries: List[TrialBalanceEntry] = []
        total_debit = 0.0
        total_credit = 0.0
        
        for account in accounts:
            # Get opening balance (before start_date)
            opening_balance = account.get_balance_as_of(db, start_date)
            
            # Get period activity (between start_date and end_date)
            period_activity = account.get_period_activity(db, start_date, end_date)
            
            # Calculate ending balance
            ending_balance = opening_balance + period_activity
            
            # Skip zero balance accounts if requested
            if not include_zeros and ending_balance == 0:
                continue
                
            # Determine debit/credit amounts based on account type
            if account.account_type.normal_balance == 'debit':
                debit_amount = ending_balance if ending_balance > 0 else 0
                credit_amount = -ending_balance if ending_balance < 0 else 0
            else:
                debit_amount = -ending_balance if ending_balance < 0 else 0
                credit_amount = ending_balance if ending_balance > 0 else 0
                
            # Add to totals
            total_debit += debit_amount
            total_credit += credit_amount
            
            # Create trial balance entry
            entries.append(TrialBalanceEntry(
                account_code=account.code,
                account_name=account.name,
                account_type=account.account_type.name,
                opening_balance=opening_balance,
                period_activity=period_activity,
                ending_balance=ending_balance,
                debit_amount=debit_amount,
                credit_amount=credit_amount
            ))
            
        return TrialBalance(
            start_date=start_date,
            end_date=end_date,
            entries=entries,
            total_debit=total_debit,
            total_credit=total_credit,
            difference=total_debit - total_credit
        )
        
    @staticmethod
    def export_trial_balance(
        trial_balance: TrialBalance,
        format: str = 'csv'  # 'csv' or 'excel'
    ) -> bytes:
        """
        Export trial balance to the specified format
        """
        # Implementation for exporting to different formats
        # This is a placeholder - actual implementation would use a library like pandas
        # or openpyxl for Excel export
        pass
