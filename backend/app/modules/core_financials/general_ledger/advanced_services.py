"""
Advanced General Ledger Services
Real-time processing, automated controls, and intelligent reconciliation
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc, text
from datetime import date, datetime, timedelta
from decimal import Decimal
import json
from dataclasses import dataclass

from .advanced_models import (
    GLAccount, GLDimension, GLJournalEntry, GLJournalEntryLine, 
    GLPeriod, GLAccountBalance, GLIntegrationLog, GLRecurringTemplate,
    AccountType, JournalEntryStatus, JournalEntryType, PeriodStatus
)

@dataclass
class TrialBalanceItem:
    account_code: str
    account_name: str
    account_type: str
    debit_balance: Decimal
    credit_balance: Decimal
    net_balance: Decimal

@dataclass
class FinancialStatementItem:
    account_code: str
    account_name: str
    current_period: Decimal
    prior_period: Decimal
    variance: Decimal
    variance_percent: Decimal

@dataclass
class ReconciliationResult:
    control_account_balance: Decimal
    subsidiary_ledger_balance: Decimal
    difference: Decimal
    is_reconciled: bool
    discrepancies: List[Dict[str, Any]]

class AdvancedGLService:
    """Advanced General Ledger service with real-time processing and intelligent controls"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Multi-Dimensional Chart of Accounts Management
    def create_account_with_dimensions(self, account_data: Dict[str, Any]) -> GLAccount:
        """Create account with multi-dimensional requirements"""
        
        # Validate account code format and uniqueness
        if self.db.query(GLAccount).filter(GLAccount.account_code == account_data['account_code']).first():
            raise ValueError(f"Account code {account_data['account_code']} already exists")
        
        # Set hierarchical path
        parent_path = ""
        if account_data.get('parent_account_id'):
            parent = self.db.query(GLAccount).filter(GLAccount.id == account_data['parent_account_id']).first()
            if parent:
                parent_path = parent.path or ""
                account_data['level'] = parent.level + 1
        
        account_data['path'] = f"{parent_path}/{account_data['account_code']}" if parent_path else account_data['account_code']
        
        # Set normal balance based on account type
        normal_balance_map = {
            AccountType.ASSET: 'debit',
            AccountType.EXPENSE: 'debit',
            AccountType.LIABILITY: 'credit',
            AccountType.EQUITY: 'credit',
            AccountType.REVENUE: 'credit'
        }
        account_data['normal_balance'] = normal_balance_map.get(account_data['account_type'], 'debit')
        
        account = GLAccount(**account_data)
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        
        return account
    
    def get_account_hierarchy(self, account_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get hierarchical account structure"""
        query = self.db.query(GLAccount).filter(GLAccount.is_active == True)
        
        if account_id:
            query = query.filter(GLAccount.parent_account_id == account_id)
        else:
            query = query.filter(GLAccount.parent_account_id.is_(None))
        
        accounts = query.order_by(GLAccount.account_code).all()
        
        result = []
        for account in accounts:
            account_dict = {
                'id': account.id,
                'account_code': account.account_code,
                'account_name': account.account_name,
                'account_type': account.account_type.value,
                'level': account.level,
                'has_children': len(account.child_accounts) > 0,
                'children': self.get_account_hierarchy(account.id) if account.child_accounts else []
            }
            result.append(account_dict)
        
        return result
    
    # Real-Time Journal Entry Processing
    def create_journal_entry_realtime(self, entry_data: Dict[str, Any]) -> GLJournalEntry:
        """Create and optionally post journal entry in real-time"""
        
        # Validate entry data
        self._validate_journal_entry(entry_data)
        
        # Generate entry number
        entry_number = self._generate_entry_number(entry_data.get('entry_type', JournalEntryType.MANUAL))
        
        # Create journal entry
        journal_entry = GLJournalEntry(
            entry_number=entry_number,
            entry_type=entry_data['entry_type'],
            entry_date=entry_data['entry_date'],
            period_id=self._get_period_for_date(entry_data['entry_date']).id,
            description=entry_data['description'],
            source_module=entry_data.get('source_module'),
            source_document_type=entry_data.get('source_document_type'),
            source_document_id=entry_data.get('source_document_id'),
            reference_number=entry_data.get('reference_number'),
            currency_code=entry_data.get('currency_code', 'USD'),
            exchange_rate=entry_data.get('exchange_rate', Decimal('1.0')),
            requires_approval=entry_data.get('requires_approval', False),
            notes=entry_data.get('notes'),
            tags=entry_data.get('tags'),
            custom_fields=entry_data.get('custom_fields')
        )
        
        self.db.add(journal_entry)
        self.db.flush()
        
        # Add journal entry lines
        total_debit = Decimal('0')
        total_credit = Decimal('0')
        
        for line_data in entry_data['lines']:
            # Validate line dimensions
            self._validate_line_dimensions(line_data)
            
            line = GLJournalEntryLine(
                journal_entry_id=journal_entry.id,
                line_number=line_data['line_number'],
                account_id=line_data['account_id'],
                department_id=line_data.get('department_id'),
                cost_center_id=line_data.get('cost_center_id'),
                project_id=line_data.get('project_id'),
                location_id=line_data.get('location_id'),
                product_id=line_data.get('product_id'),
                debit_amount=line_data.get('debit_amount', Decimal('0')),
                credit_amount=line_data.get('credit_amount', Decimal('0')),
                currency_code=line_data.get('currency_code', 'USD'),
                exchange_rate=line_data.get('exchange_rate', Decimal('1.0')),
                description=line_data.get('description'),
                reference=line_data.get('reference'),
                tax_code=line_data.get('tax_code'),
                tax_amount=line_data.get('tax_amount', Decimal('0'))
            )
            
            # Calculate base currency amounts
            line.base_currency_debit = line.debit_amount * line.exchange_rate
            line.base_currency_credit = line.credit_amount * line.exchange_rate
            
            total_debit += line.base_currency_debit
            total_credit += line.base_currency_credit
            
            self.db.add(line)
        
        # Update journal entry totals
        journal_entry.total_debit = total_debit
        journal_entry.total_credit = total_credit
        
        # Validate balanced entry
        if abs(total_debit - total_credit) > Decimal('0.01'):
            raise ValueError(f"Journal entry is not balanced: Debit {total_debit}, Credit {total_credit}")
        
        # Auto-post if configured
        if entry_data.get('auto_post', False) and not journal_entry.requires_approval:
            self._post_journal_entry(journal_entry)
        
        self.db.commit()
        self.db.refresh(journal_entry)
        
        # Log integration if from external module
        if journal_entry.source_module:
            self._log_integration(journal_entry)
        
        return journal_entry
    
    def post_journal_entry(self, entry_id: int) -> bool:
        """Post journal entry and update account balances"""
        journal_entry = self.db.query(GLJournalEntry).filter(GLJournalEntry.id == entry_id).first()
        
        if not journal_entry:
            raise ValueError("Journal entry not found")
        
        if journal_entry.status != JournalEntryStatus.APPROVED:
            raise ValueError("Journal entry must be approved before posting")
        
        return self._post_journal_entry(journal_entry)
    
    def _post_journal_entry(self, journal_entry: GLJournalEntry) -> bool:
        """Internal method to post journal entry"""
        try:
            # Update account balances
            for line in journal_entry.lines:
                self._update_account_balance(
                    account_id=line.account_id,
                    period_id=journal_entry.period_id,
                    debit_amount=line.base_currency_debit,
                    credit_amount=line.base_currency_credit,
                    department_id=line.department_id,
                    cost_center_id=line.cost_center_id,
                    project_id=line.project_id
                )
            
            # Update journal entry status
            journal_entry.status = JournalEntryStatus.POSTED
            journal_entry.posting_date = date.today()
            journal_entry.posted_at = datetime.utcnow()
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to post journal entry: {str(e)}")
    
    # Advanced Trial Balance with Multi-Dimensional Support
    def generate_trial_balance(
        self, 
        period_id: int,
        department_id: Optional[int] = None,
        cost_center_id: Optional[int] = None,
        project_id: Optional[int] = None,
        include_zero_balances: bool = False
    ) -> List[TrialBalanceItem]:
        """Generate trial balance with dimensional filtering"""
        
        # Build query for account balances
        query = self.db.query(
            GLAccount.account_code,
            GLAccount.account_name,
            GLAccount.account_type,
            func.sum(GLAccountBalance.ending_balance_debit).label('total_debit'),
            func.sum(GLAccountBalance.ending_balance_credit).label('total_credit')
        ).join(GLAccountBalance).filter(
            GLAccountBalance.period_id == period_id
        )
        
        # Apply dimensional filters
        if department_id:
            query = query.filter(GLAccountBalance.department_id == department_id)
        if cost_center_id:
            query = query.filter(GLAccountBalance.cost_center_id == cost_center_id)
        if project_id:
            query = query.filter(GLAccountBalance.project_id == project_id)
        
        query = query.group_by(
            GLAccount.account_code,
            GLAccount.account_name,
            GLAccount.account_type
        ).order_by(GLAccount.account_code)
        
        results = query.all()
        
        trial_balance = []
        total_debits = Decimal('0')
        total_credits = Decimal('0')
        
        for result in results:
            debit_balance = result.total_debit or Decimal('0')
            credit_balance = result.total_credit or Decimal('0')
            net_balance = debit_balance - credit_balance
            
            # Skip zero balances if requested
            if not include_zero_balances and net_balance == 0:
                continue
            
            trial_balance.append(TrialBalanceItem(
                account_code=result.account_code,
                account_name=result.account_name,
                account_type=result.account_type.value,
                debit_balance=debit_balance,
                credit_balance=credit_balance,
                net_balance=net_balance
            ))
            
            total_debits += debit_balance
            total_credits += credit_balance
        
        # Add totals row
        trial_balance.append(TrialBalanceItem(
            account_code="TOTAL",
            account_name="Total",
            account_type="TOTAL",
            debit_balance=total_debits,
            credit_balance=total_credits,
            net_balance=total_debits - total_credits
        ))
        
        return trial_balance
    
    # Automated Reconciliation
    def reconcile_control_account(self, account_id: int, period_id: int) -> ReconciliationResult:
        """Reconcile control account with subsidiary ledger"""
        
        account = self.db.query(GLAccount).filter(GLAccount.id == account_id).first()
        if not account or not account.is_control_account:
            raise ValueError("Account is not a control account")
        
        # Get GL control account balance
        control_balance = self._get_account_balance(account_id, period_id)
        
        # Get subsidiary ledger balance based on type
        subsidiary_balance = self._get_subsidiary_ledger_balance(
            account.subsidiary_ledger_type, 
            period_id
        )
        
        difference = control_balance - subsidiary_balance
        is_reconciled = abs(difference) < Decimal('0.01')
        
        discrepancies = []
        if not is_reconciled:
            discrepancies = self._identify_reconciliation_discrepancies(
                account.subsidiary_ledger_type,
                period_id,
                difference
            )
        
        return ReconciliationResult(
            control_account_balance=control_balance,
            subsidiary_ledger_balance=subsidiary_balance,
            difference=difference,
            is_reconciled=is_reconciled,
            discrepancies=discrepancies
        )
    
    # Period-End Close Automation
    def execute_period_close(self, period_id: int) -> Dict[str, Any]:
        """Execute automated period-end close process"""
        
        period = self.db.query(GLPeriod).filter(GLPeriod.id == period_id).first()
        if not period:
            raise ValueError("Period not found")
        
        if period.status != PeriodStatus.OPEN:
            raise ValueError("Period is not open for closing")
        
        close_results = {
            'period_id': period_id,
            'close_date': datetime.utcnow(),
            'steps_completed': [],
            'errors': []
        }
        
        try:
            # Step 1: Generate recurring entries
            self._process_recurring_entries(period_id)
            close_results['steps_completed'].append('recurring_entries')
            
            # Step 2: Calculate and post depreciation
            self._process_depreciation_entries(period_id)
            close_results['steps_completed'].append('depreciation')
            
            # Step 3: Process accruals and deferrals
            self._process_accrual_entries(period_id)
            close_results['steps_completed'].append('accruals')
            
            # Step 4: Foreign currency revaluation
            self._process_fx_revaluation(period_id)
            close_results['steps_completed'].append('fx_revaluation')
            
            # Step 5: Validate all reconciliations
            reconciliation_errors = self._validate_period_reconciliations(period_id)
            if reconciliation_errors:
                close_results['errors'].extend(reconciliation_errors)
            else:
                close_results['steps_completed'].append('reconciliations')
            
            # Step 6: Close period if no errors
            if not close_results['errors']:
                period.status = PeriodStatus.CLOSED
                period.closed_at = datetime.utcnow()
                self.db.commit()
                close_results['steps_completed'].append('period_closed')
            
        except Exception as e:
            self.db.rollback()
            close_results['errors'].append(f"Period close failed: {str(e)}")
        
        return close_results
    
    # Financial Statement Generation
    def generate_balance_sheet(
        self, 
        period_id: int,
        comparative_period_id: Optional[int] = None
    ) -> Dict[str, List[FinancialStatementItem]]:
        """Generate balance sheet with comparative periods"""
        
        # Get asset accounts
        assets = self._get_financial_statement_section(
            period_id, 
            [AccountType.ASSET], 
            comparative_period_id
        )
        
        # Get liability accounts
        liabilities = self._get_financial_statement_section(
            period_id, 
            [AccountType.LIABILITY], 
            comparative_period_id
        )
        
        # Get equity accounts
        equity = self._get_financial_statement_section(
            period_id, 
            [AccountType.EQUITY], 
            comparative_period_id
        )
        
        return {
            'assets': assets,
            'liabilities': liabilities,
            'equity': equity
        }
    
    def generate_income_statement(
        self, 
        period_id: int,
        comparative_period_id: Optional[int] = None
    ) -> Dict[str, List[FinancialStatementItem]]:
        """Generate income statement with comparative periods"""
        
        # Get revenue accounts
        revenue = self._get_financial_statement_section(
            period_id, 
            [AccountType.REVENUE], 
            comparative_period_id
        )
        
        # Get expense accounts
        expenses = self._get_financial_statement_section(
            period_id, 
            [AccountType.EXPENSE], 
            comparative_period_id
        )
        
        return {
            'revenue': revenue,
            'expenses': expenses
        }
    
    # Helper Methods
    def _validate_journal_entry(self, entry_data: Dict[str, Any]):
        """Validate journal entry data"""
        required_fields = ['entry_type', 'entry_date', 'description', 'lines']
        for field in required_fields:
            if field not in entry_data:
                raise ValueError(f"Missing required field: {field}")
        
        if not entry_data['lines']:
            raise ValueError("Journal entry must have at least one line")
        
        # Validate period is open
        period = self._get_period_for_date(entry_data['entry_date'])
        if period.status != PeriodStatus.OPEN:
            raise ValueError(f"Period {period.period_name} is not open for posting")
    
    def _validate_line_dimensions(self, line_data: Dict[str, Any]):
        """Validate required dimensions for account"""
        account = self.db.query(GLAccount).filter(GLAccount.id == line_data['account_id']).first()
        if not account:
            raise ValueError("Invalid account ID")
        
        # Check required dimensions
        if account.department_required and not line_data.get('department_id'):
            raise ValueError(f"Department is required for account {account.account_code}")
        
        if account.cost_center_required and not line_data.get('cost_center_id'):
            raise ValueError(f"Cost center is required for account {account.account_code}")
        
        if account.project_required and not line_data.get('project_id'):
            raise ValueError(f"Project is required for account {account.account_code}")
    
    def _generate_entry_number(self, entry_type: JournalEntryType) -> str:
        """Generate unique journal entry number"""
        prefix_map = {
            JournalEntryType.MANUAL: 'JE',
            JournalEntryType.AUTOMATIC: 'AJE',
            JournalEntryType.RECURRING: 'RJE',
            JournalEntryType.REVERSING: 'REV',
            JournalEntryType.ACCRUAL: 'ACR',
            JournalEntryType.DEPRECIATION: 'DEP'
        }
        
        prefix = prefix_map.get(entry_type, 'JE')
        year = datetime.now().year
        
        # Get next sequence number
        last_entry = self.db.query(GLJournalEntry).filter(
            GLJournalEntry.entry_number.like(f"{prefix}-{year}-%")
        ).order_by(desc(GLJournalEntry.entry_number)).first()
        
        if last_entry:
            last_seq = int(last_entry.entry_number.split('-')[-1])
            next_seq = last_seq + 1
        else:
            next_seq = 1
        
        return f"{prefix}-{year}-{str(next_seq).zfill(6)}"
    
    def _get_period_for_date(self, entry_date: date) -> GLPeriod:
        """Get accounting period for given date"""
        period = self.db.query(GLPeriod).filter(
            and_(
                GLPeriod.start_date <= entry_date,
                GLPeriod.end_date >= entry_date
            )
        ).first()
        
        if not period:
            raise ValueError(f"No accounting period found for date {entry_date}")
        
        return period
    
    def _update_account_balance(
        self, 
        account_id: int, 
        period_id: int, 
        debit_amount: Decimal, 
        credit_amount: Decimal,
        department_id: Optional[int] = None,
        cost_center_id: Optional[int] = None,
        project_id: Optional[int] = None
    ):
        """Update account balance for posting"""
        
        # Find or create balance record
        balance = self.db.query(GLAccountBalance).filter(
            and_(
                GLAccountBalance.account_id == account_id,
                GLAccountBalance.period_id == period_id,
                GLAccountBalance.department_id == department_id,
                GLAccountBalance.cost_center_id == cost_center_id,
                GLAccountBalance.project_id == project_id
            )
        ).first()
        
        if not balance:
            balance = GLAccountBalance(
                account_id=account_id,
                period_id=period_id,
                department_id=department_id,
                cost_center_id=cost_center_id,
                project_id=project_id
            )
            self.db.add(balance)
        
        # Update balances
        balance.period_debit += debit_amount
        balance.period_credit += credit_amount
        balance.ending_balance_debit = balance.beginning_balance_debit + balance.period_debit
        balance.ending_balance_credit = balance.beginning_balance_credit + balance.period_credit
        balance.last_updated = datetime.utcnow()
    
    def _log_integration(self, journal_entry: GLJournalEntry):
        """Log integration transaction"""
        integration_log = GLIntegrationLog(
            source_module=journal_entry.source_module,
            source_transaction_type=journal_entry.source_document_type,
            source_transaction_id=journal_entry.source_document_id,
            journal_entry_id=journal_entry.id,
            status='posted' if journal_entry.status == JournalEntryStatus.POSTED else 'pending',
            processed_at=datetime.utcnow()
        )
        self.db.add(integration_log)
    
    def _get_account_balance(self, account_id: int, period_id: int) -> Decimal:
        """Get account balance for period"""
        balance = self.db.query(GLAccountBalance).filter(
            and_(
                GLAccountBalance.account_id == account_id,
                GLAccountBalance.period_id == period_id
            )
        ).first()
        
        if not balance:
            return Decimal('0')
        
        return balance.ending_balance_debit - balance.ending_balance_credit
    
    def _get_subsidiary_ledger_balance(self, ledger_type: str, period_id: int) -> Decimal:
        """Get subsidiary ledger balance"""
        # This would integrate with specific subsidiary ledgers
        # Implementation depends on the subsidiary ledger type
        if ledger_type == 'ar':
            return self._get_ar_subsidiary_balance(period_id)
        elif ledger_type == 'ap':
            return self._get_ap_subsidiary_balance(period_id)
        elif ledger_type == 'inventory':
            return self._get_inventory_subsidiary_balance(period_id)
        else:
            return Decimal('0')
    
    def _get_ar_subsidiary_balance(self, period_id: int) -> Decimal:
        """Get AR subsidiary ledger balance"""
        # This would query AR module for outstanding balances
        # Placeholder implementation
        return Decimal('0')
    
    def _get_ap_subsidiary_balance(self, period_id: int) -> Decimal:
        """Get AP subsidiary ledger balance"""
        # This would query AP module for outstanding balances
        # Placeholder implementation
        return Decimal('0')
    
    def _get_inventory_subsidiary_balance(self, period_id: int) -> Decimal:
        """Get inventory subsidiary ledger balance"""
        # This would query inventory module for current values
        # Placeholder implementation
        return Decimal('0')
    
    def _identify_reconciliation_discrepancies(
        self, 
        ledger_type: str, 
        period_id: int, 
        difference: Decimal
    ) -> List[Dict[str, Any]]:
        """Identify specific reconciliation discrepancies"""
        # Implementation would analyze specific discrepancies
        # Placeholder implementation
        return [
            {
                'type': 'timing_difference',
                'description': f'Potential timing difference of {difference}',
                'amount': difference
            }
        ]
    
    def _process_recurring_entries(self, period_id: int):
        """Process recurring journal entries for period"""
        # Implementation for recurring entries
        pass
    
    def _process_depreciation_entries(self, period_id: int):
        """Process depreciation entries for period"""
        # Implementation for depreciation
        pass
    
    def _process_accrual_entries(self, period_id: int):
        """Process accrual and deferral entries"""
        # Implementation for accruals
        pass
    
    def _process_fx_revaluation(self, period_id: int):
        """Process foreign exchange revaluation"""
        # Implementation for FX revaluation
        pass
    
    def _validate_period_reconciliations(self, period_id: int) -> List[str]:
        """Validate all reconciliations for period"""
        errors = []
        
        # Check all control accounts
        control_accounts = self.db.query(GLAccount).filter(
            GLAccount.is_control_account == True
        ).all()
        
        for account in control_accounts:
            try:
                result = self.reconcile_control_account(account.id, period_id)
                if not result.is_reconciled:
                    errors.append(f"Account {account.account_code} not reconciled: {result.difference}")
            except Exception as e:
                errors.append(f"Reconciliation error for {account.account_code}: {str(e)}")
        
        return errors
    
    def _get_financial_statement_section(
        self, 
        period_id: int, 
        account_types: List[AccountType],
        comparative_period_id: Optional[int] = None
    ) -> List[FinancialStatementItem]:
        """Get financial statement section data"""
        
        query = self.db.query(
            GLAccount.account_code,
            GLAccount.account_name,
            func.sum(GLAccountBalance.ending_balance_debit - GLAccountBalance.ending_balance_credit).label('current_balance')
        ).join(GLAccountBalance).filter(
            and_(
                GLAccount.account_type.in_(account_types),
                GLAccountBalance.period_id == period_id
            )
        ).group_by(
            GLAccount.account_code,
            GLAccount.account_name
        ).order_by(GLAccount.account_code)
        
        results = query.all()
        
        statement_items = []
        for result in results:
            current_period = result.current_balance or Decimal('0')
            prior_period = Decimal('0')
            
            # Get comparative period data if requested
            if comparative_period_id:
                prior_balance = self.db.query(
                    func.sum(GLAccountBalance.ending_balance_debit - GLAccountBalance.ending_balance_credit)
                ).join(GLAccount).filter(
                    and_(
                        GLAccount.account_code == result.account_code,
                        GLAccountBalance.period_id == comparative_period_id
                    )
                ).scalar()
                prior_period = prior_balance or Decimal('0')
            
            variance = current_period - prior_period
            variance_percent = (variance / prior_period * 100) if prior_period != 0 else Decimal('0')
            
            statement_items.append(FinancialStatementItem(
                account_code=result.account_code,
                account_name=result.account_name,
                current_period=current_period,
                prior_period=prior_period,
                variance=variance,
                variance_percent=variance_percent
            ))
        
        return statement_items