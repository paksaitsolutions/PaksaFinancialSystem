"""
Payroll GL Integration Service
"""
from decimal import Decimal
from uuid import UUID
from sqlalchemy.orm import Session
from app.models import PayrollRun, JournalEntry, JournalEntryLine, ChartOfAccounts
from app.services.base import BaseService

class PayrollGLService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db, PayrollRun)
    
    def post_payroll_to_gl(self, payroll_run: PayrollRun) -> JournalEntry:
        """Post payroll run to GL with automatic journal entries"""
        
        # Create journal entry
        journal_entry = JournalEntry(
            company_id=payroll_run.company_id,
            entry_number=f"PR-{payroll_run.run_number}",
            entry_date=payroll_run.pay_date,
            description=f"Payroll Run {payroll_run.run_number}",
            source_module="PAYROLL",
            status="posted"
        )
        self.db.add(journal_entry)
        self.db.flush()
        
        # Get accounts
        salary_expense = self._get_account(payroll_run.company_id, "6100", "Salary Expense")
        payroll_liability = self._get_account(payroll_run.company_id, "2100", "Payroll Liabilities")
        
        # Dr. Salary Expense
        self.db.add(JournalEntryLine(
            journal_entry_id=journal_entry.id,
            account_id=salary_expense.id,
            description="Payroll Expense",
            debit_amount=payroll_run.total_gross,
            credit_amount=Decimal('0'),
            line_number=1
        ))
        
        # Cr. Payroll Liabilities
        self.db.add(JournalEntryLine(
            journal_entry_id=journal_entry.id,
            account_id=payroll_liability.id,
            description="Payroll Liabilities",
            debit_amount=Decimal('0'),
            credit_amount=payroll_run.total_net,
            line_number=2
        ))
        
        journal_entry.total_debit = payroll_run.total_gross
        journal_entry.total_credit = payroll_run.total_net
        
        return journal_entry
    
    def post_tax_withholdings_to_gl(self, payroll_run: PayrollRun, federal_tax: Decimal, state_tax: Decimal, fica_tax: Decimal) -> JournalEntry:
        """Post tax withholdings to liability accounts"""
        
        journal_entry = JournalEntry(
            company_id=payroll_run.company_id,
            entry_number=f"TAX-{payroll_run.run_number}",
            entry_date=payroll_run.pay_date,
            description=f"Tax Withholdings - {payroll_run.run_number}",
            source_module="PAYROLL",
            status="posted"
        )
        self.db.add(journal_entry)
        self.db.flush()
        
        # Get liability accounts
        federal_tax_payable = self._get_account(payroll_run.company_id, "2110", "Federal Tax Payable")
        state_tax_payable = self._get_account(payroll_run.company_id, "2120", "State Tax Payable")
        fica_tax_payable = self._get_account(payroll_run.company_id, "2130", "FICA Tax Payable")
        payroll_liability = self._get_account(payroll_run.company_id, "2100", "Payroll Liabilities")
        
        line_number = 1
        total_withholdings = federal_tax + state_tax + fica_tax
        
        # Dr. Payroll Liabilities (reduce net pay liability)
        self.db.add(JournalEntryLine(
            journal_entry_id=journal_entry.id,
            account_id=payroll_liability.id,
            description="Reduce Net Pay Liability",
            debit_amount=total_withholdings,
            credit_amount=Decimal('0'),
            line_number=line_number
        ))
        line_number += 1
        
        # Cr. Federal Tax Payable
        if federal_tax > 0:
            self.db.add(JournalEntryLine(
                journal_entry_id=journal_entry.id,
                account_id=federal_tax_payable.id,
                description="Federal Tax Withholding",
                debit_amount=Decimal('0'),
                credit_amount=federal_tax,
                line_number=line_number
            ))
            line_number += 1
        
        # Cr. State Tax Payable
        if state_tax > 0:
            self.db.add(JournalEntryLine(
                journal_entry_id=journal_entry.id,
                account_id=state_tax_payable.id,
                description="State Tax Withholding",
                debit_amount=Decimal('0'),
                credit_amount=state_tax,
                line_number=line_number
            ))
            line_number += 1
        
        # Cr. FICA Tax Payable
        if fica_tax > 0:
            self.db.add(JournalEntryLine(
                journal_entry_id=journal_entry.id,
                account_id=fica_tax_payable.id,
                description="FICA Tax Withholding",
                debit_amount=Decimal('0'),
                credit_amount=fica_tax,
                line_number=line_number
            ))
        
        journal_entry.total_debit = total_withholdings
        journal_entry.total_credit = total_withholdings
        
        return journal_entry
    
    def post_benefits_deductions_to_gl(self, payroll_run: PayrollRun, health_insurance: Decimal, retirement_401k: Decimal, other_deductions: Decimal) -> JournalEntry:
        """Post benefits deductions to GL accounts"""
        
        journal_entry = JournalEntry(
            company_id=payroll_run.company_id,
            entry_number=f"BEN-{payroll_run.run_number}",
            entry_date=payroll_run.pay_date,
            description=f"Benefits Deductions - {payroll_run.run_number}",
            source_module="PAYROLL",
            status="posted"
        )
        self.db.add(journal_entry)
        self.db.flush()
        
        # Get accounts
        health_insurance_payable = self._get_account(payroll_run.company_id, "2140", "Health Insurance Payable")
        retirement_401k_payable = self._get_account(payroll_run.company_id, "2150", "401k Contributions Payable")
        other_deductions_payable = self._get_account(payroll_run.company_id, "2160", "Other Deductions Payable")
        payroll_liability = self._get_account(payroll_run.company_id, "2100", "Payroll Liabilities")
        
        line_number = 1
        total_deductions = health_insurance + retirement_401k + other_deductions
        
        # Dr. Payroll Liabilities (reduce net pay liability)
        self.db.add(JournalEntryLine(
            journal_entry_id=journal_entry.id,
            account_id=payroll_liability.id,
            description="Reduce Net Pay for Benefits",
            debit_amount=total_deductions,
            credit_amount=Decimal('0'),
            line_number=line_number
        ))
        line_number += 1
        
        # Cr. Health Insurance Payable
        if health_insurance > 0:
            self.db.add(JournalEntryLine(
                journal_entry_id=journal_entry.id,
                account_id=health_insurance_payable.id,
                description="Health Insurance Deduction",
                debit_amount=Decimal('0'),
                credit_amount=health_insurance,
                line_number=line_number
            ))
            line_number += 1
        
        # Cr. 401k Contributions Payable
        if retirement_401k > 0:
            self.db.add(JournalEntryLine(
                journal_entry_id=journal_entry.id,
                account_id=retirement_401k_payable.id,
                description="401k Contribution Deduction",
                debit_amount=Decimal('0'),
                credit_amount=retirement_401k,
                line_number=line_number
            ))
            line_number += 1
        
        # Cr. Other Deductions Payable
        if other_deductions > 0:
            self.db.add(JournalEntryLine(
                journal_entry_id=journal_entry.id,
                account_id=other_deductions_payable.id,
                description="Other Deductions",
                debit_amount=Decimal('0'),
                credit_amount=other_deductions,
                line_number=line_number
            ))
        
        journal_entry.total_debit = total_deductions
        journal_entry.total_credit = total_deductions
        
        return journal_entry
    
    def _get_account(self, company_id: UUID, code: str, name: str) -> ChartOfAccounts:
        """Get or create chart of accounts"""
        account = self.db.query(ChartOfAccounts).filter(
            ChartOfAccounts.company_id == company_id,
            ChartOfAccounts.account_code == code
        ).first()
        
        if not account:
            account = ChartOfAccounts(
                company_id=company_id,
                account_code=code,
                account_name=name,
                account_type="Expense" if code.startswith("6") else "Liability",
                normal_balance="Debit" if code.startswith("6") else "Credit"
            )
            self.db.add(account)
            self.db.flush()
        
        return account