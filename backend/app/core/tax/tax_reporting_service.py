"""
Tax Reporting Service

This module provides comprehensive tax reporting functionality for the Paksa Financial System.
It handles generation of tax reports, filings, and compliance documentation.
"""

from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from decimal import Decimal
import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app import crud, models, schemas
from app.core.tax.tax_policy_service import TaxType, TaxJurisdiction
from app.core.tax.tax_calculation_service import tax_calculation_service
from app.core.config import settings

logger = logging.getLogger(__name__)

class TaxReportingService:
    def __init__(self, db: Session):
        self.db = db
        
    def generate_tax_liability_report(
        self,
        company_id: str,
        start_date: date,
        end_date: date,
        tax_types: Optional[List[str]] = None,
        jurisdiction_codes: Optional[List[str]] = None,
        group_by: str = "month"
    ) -> Dict[str, Any]:
        """
        Generate a tax liability report showing tax collected and owed for a given period.
        
        Args:
            company_id: ID of the company
            start_date: Start date of the reporting period
            end_date: End date of the reporting period
            tax_types: Optional list of tax types to include (e.g., ['sales', 'vat'])
            jurisdiction_codes: Optional list of jurisdiction codes to filter by
            group_by: How to group the results (day, week, month, quarter, year)
            
        Returns:
            Dict containing the tax liability report data
        """
        # Input validation
        if end_date < start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date must be after start date"
            )
            
        # Base query for tax transactions in the date range
        query = self.db.query(models.TaxTransaction).filter(
            models.TaxTransaction.company_id == company_id,
            models.TaxTransaction.transaction_date >= start_date,
            models.TaxTransaction.transaction_date <= end_date,
            models.TaxTransaction.is_reported == False  # Only include unreported transactions
        )
        
        # Apply filters
        if tax_types:
            query = query.filter(models.TaxTransaction.tax_type.in_(tax_types))
            
        if jurisdiction_codes:
            query = query.filter(models.TaxTransaction.jurisdiction_code.in_(jurisdiction_codes))
            
        # Execute query
        transactions = query.all()
        
        # Group transactions by period
        period_totals = {}
        
        for tx in transactions:
            # Determine the period key based on grouping
            if group_by == "day":
                period_key = tx.transaction_date.strftime("%Y-%m-%d")
            elif group_by == "week":
                # Get the start of the week (Monday)
                week_start = tx.transaction_date - timedelta(days=tx.transaction_date.weekday())
                period_key = week_start.strftime("%Y-W%W")
            elif group_by == "quarter":
                quarter = (tx.transaction_date.month - 1) // 3 + 1
                period_key = f"{tx.transaction_date.year}-Q{quarter}"
            elif group_by == "year":
                period_key = str(tx.transaction_date.year)
            else:  # month (default)
                period_key = tx.transaction_date.strftime("%Y-%m")
                
            # Initialize period if not exists
            if period_key not in period_totals:
                period_totals[period_key] = {
                    "taxable_amount": Decimal("0.00"),
                    "tax_amount": Decimal("0.00"),
                    "tax_types": {},
                    "jurisdictions": {}
                }
                
            # Update period totals
            period = period_totals[period_key]
            period["taxable_amount"] += tx.taxable_amount
            period["tax_amount"] += tx.tax_amount
            
            # Update tax type breakdown
            if tx.tax_type not in period["tax_types"]:
                period["tax_types"][tx.tax_type] = {
                    "taxable_amount": Decimal("0.00"),
                    "tax_amount": Decimal("0.00")
                }
            period["tax_types"][tx.tax_type]["taxable_amount"] += tx.taxable_amount
            period["tax_types"][tx.tax_type]["tax_amount"] += tx.tax_amount
            
            # Update jurisdiction breakdown
            if tx.jurisdiction_code not in period["jurisdictions"]:
                period["jurisdictions"][tx.jurisdiction_code] = {
                    "taxable_amount": Decimal("0.00"),
                    "tax_amount": Decimal("0.00")
                }
            period["jurisdictions"][tx.jurisdiction_code]["taxable_amount"] += tx.taxable_amount
            period["jurisdictions"][tx.jurisdiction_code]["tax_amount"] += tx.tax_amount
        
        # Calculate totals
        total_taxable = sum(p["taxable_amount"] for p in period_totals.values())
        total_tax = sum(p["tax_amount"] for p in period_totals.values())
        
        # Prepare response
        return {
            "company_id": company_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_taxable_amount": str(total_taxable),
            "total_tax_amount": str(total_tax),
            "periods": [
                {"period": period, **data} 
                for period, data in sorted(period_totals.items())
            ],
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "tax_types": tax_types or "All",
                "jurisdiction_codes": jurisdiction_codes or "All",
                "group_by": group_by
            }
        }
        
    def generate_tax_filing(
        self,
        company_id: str,
        tax_authority_id: str,
        period_start: date,
        period_end: date,
        tax_type: str,
        jurisdiction_code: str,
        include_transactions: bool = False,
        mark_as_filed: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a tax filing for submission to a tax authority.
        
        Args:
            company_id: ID of the company
            tax_authority_id: ID of the tax authority
            period_start: Start date of the filing period
            period_end: End date of the filing period
            tax_type: Type of tax (e.g., 'sales', 'vat', 'gst')
            jurisdiction_code: Jurisdiction code for the filing
            include_transactions: Whether to include detailed transactions
            mark_as_filed: Whether to mark transactions as filed
            
        Returns:
            Dict containing the tax filing data
        """
        # Get tax authority
        tax_authority = crud.tax_authority.get(self.db, id=tax_authority_id)
        if not tax_authority:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tax authority {tax_authority_id} not found"
            )
            
        # Get transactions for the period
        query = self.db.query(models.TaxTransaction).filter(
            models.TaxTransaction.company_id == company_id,
            models.TaxTransaction.tax_type == tax_type,
            models.TaxTransaction.jurisdiction_code == jurisdiction_code,
            models.TaxTransaction.transaction_date >= period_start,
            models.TaxTransaction.transaction_date <= period_end,
            models.TaxTransaction.is_reported == False
        )
        
        transactions = query.all()
        
        if not transactions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No tax transactions found for the specified criteria"
            )
            
        # Calculate totals
        total_taxable = sum(tx.taxable_amount for tx in transactions)
        total_tax = sum(tx.tax_amount for tx in transactions)
        
        # Prepare filing data
        filing_data = {
            "company_id": company_id,
            "tax_authority_id": tax_authority_id,
            "tax_authority_name": tax_authority.name,
            "tax_type": tax_type,
            "jurisdiction_code": jurisdiction_code,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "filing_date": date.today().isoformat(),
            "total_taxable_amount": str(total_taxable),
            "total_tax_amount": str(total_tax),
            "currency": settings.DEFAULT_CURRENCY,
            "transaction_count": len(transactions),
            "status": "prepared",
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "include_transactions": include_transactions
            }
        }
        
        # Add transaction details if requested
        if include_transactions:
            filing_data["transactions"] = [
                {
                    "id": str(tx.id),
                    "transaction_date": tx.transaction_date.isoformat(),
                    "transaction_id": tx.transaction_id,
                    "transaction_type": tx.transaction_type,
                    "taxable_amount": str(tx.taxable_amount),
                    "tax_amount": str(tx.tax_amount),
                    "tax_rate": str(tx.tax_rate),
                    "customer_id": tx.customer_id,
                    "customer_name": tx.customer_name,
                    "invoice_number": tx.invoice_number
                }
                for tx in transactions
            ]
        
        # Mark transactions as filed if requested
        if mark_as_filed:
            for tx in transactions:
                tx.is_reported = True
                tx.reported_at = datetime.utcnow()
                tx.reporting_period = f"{period_start.isoformat()}/{period_end.isoformat()}"
                self.db.add(tx)
            self.db.commit()
            
            filing_data["status"] = "filed"
            filing_data["filed_at"] = datetime.utcnow().isoformat()
        
        return filing_data
    
    def get_tax_compliance_status(
        self,
        company_id: str,
        tax_types: Optional[List[str]] = None,
        jurisdiction_codes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get the tax compliance status for a company.
        
        Args:
            company_id: ID of the company
            tax_types: Optional list of tax types to include
            jurisdiction_codes: Optional list of jurisdiction codes to include
            
        Returns:
            Dict containing compliance status information
        """
        # Base query for tax rules
        query = self.db.query(models.TaxRule).filter(
            models.TaxRule.company_id == company_id,
            models.TaxRule.is_active == True
        )
        
        # Apply filters
        if tax_types:
            query = query.filter(models.TaxRule.tax_type.in_(tax_types))
            
        if jurisdiction_codes:
            query = query.filter(models.TaxRule.jurisdiction_code.in_(jurisdiction_codes))
            
        # Get all active tax rules
        tax_rules = query.all()
        
        # Get filing frequencies for the company
        filing_frequencies = crud.tax_filing_frequency.get_by_company(
            self.db, company_id=company_id
        )
        
        # Prepare compliance status
        compliance_status = {
            "company_id": company_id,
            "as_of_date": date.today().isoformat(),
            "tax_types": {},
            "jurisdictions": {},
            "upcoming_filings": [],
            "overdue_filings": [],
            "compliance_score": 100,  # Start with 100% and deduct for issues
            "issues": []
        }
        
        # Check each tax rule for compliance
        for rule in tax_rules:
            tax_type = rule.tax_type
            jurisdiction = rule.jurisdiction_code
            
            # Initialize tax type and jurisdiction if not exists
            if tax_type not in compliance_status["tax_types"]:
                compliance_status["tax_types"][tax_type] = {
                    "tax_rules_count": 0,
                    "total_tax_amount": Decimal("0.00"),
                    "last_filing_date": None,
                    "next_filing_date": None,
                    "status": "compliant"
                }
                
            if jurisdiction not in compliance_status["jurisdictions"]:
                compliance_status["jurisdictions"][jurisdiction] = {
                    "tax_rules_count": 0,
                    "total_tax_amount": Decimal("0.00"),
                    "last_filing_date": None,
                    "next_filing_date": None,
                    "status": "compliant"
                }
                
            # Update counts
            compliance_status["tax_types"][tax_type]["tax_rules_count"] += 1
            compliance_status["jurisdictions"][jurisdiction]["tax_rules_count"] += 1
            
            # Get tax transactions for this rule
            transactions = self.db.query(models.TaxTransaction).filter(
                models.TaxTransaction.company_id == company_id,
                models.TaxTransaction.tax_type == tax_type,
                models.TaxTransaction.jurisdiction_code == jurisdiction,
                models.TaxTransaction.is_reported == False
            ).all()
            
            # Calculate total tax amount
            total_tax = sum(tx.tax_amount for tx in transactions)
            compliance_status["tax_types"][tax_type]["total_tax_amount"] += total_tax
            compliance_status["jurisdictions"][jurisdiction]["total_tax_amount"] += total_tax
            
            # Check for filing frequency and due dates
            for freq in filing_frequencies:
                if (freq.tax_type == tax_type and 
                    freq.jurisdiction_code == jurisdiction):
                    
                    # Update next filing date
                    last_filing = self._get_last_filing(
                        company_id, tax_type, jurisdiction
                    )
                    
                    next_due_date = self._calculate_next_due_date(
                        freq.frequency, 
                        last_filing["end_date"] if last_filing else None
                    )
                    
                    if next_due_date:
                        # Update tax type and jurisdiction with next filing date
                        if (not compliance_status["tax_types"][tax_type]["next_filing_date"] or
                            next_due_date < compliance_status["tax_types"][tax_type]["next_filing_date"]):
                            compliance_status["tax_types"][tax_type]["next_filing_date"] = next_due_date
                            
                        if (not compliance_status["jurisdictions"][jurisdiction]["next_filing_date"] or
                            next_due_date < compliance_status["jurisdictions"][jurisdiction]["next_filing_date"]):
                            compliance_status["jurisdictions"][jurisdiction]["next_filing_date"] = next_due_date
                        
                        # Check if filing is overdue
                        if next_due_date < date.today():
                            compliance_status["overdue_filings"].append({
                                "tax_type": tax_type,
                                "jurisdiction": jurisdiction,
                                "due_date": next_due_date.isoformat(),
                                "frequency": freq.frequency,
                                "estimated_tax": str(total_tax)
                            })
                            
                            # Update status to non-compliant
                            compliance_status["tax_types"][tax_type]["status"] = "non_compliant"
                            compliance_status["jurisdictions"][jurisdiction]["status"] = "non_compliant"
                            
                            # Add issue
                            issue = {
                                "type": "overdue_filing",
                                "tax_type": tax_type,
                                "jurisdiction": jurisdiction,
                                "due_date": next_due_date.isoformat(),
                                "days_overdue": (date.today() - next_due_date).days,
                                "estimated_tax": str(total_tax)
                            }
                            compliance_status["issues"].append(issue)
                            
                            # Deduct from compliance score
                            compliance_status["compliance_score"] = max(
                                0, 
                                compliance_status["compliance_score"] - 5  # Deduct 5% per overdue filing
                            )
                        else:
                            # Add to upcoming filings
                            compliance_status["upcoming_filings"].append({
                                "tax_type": tax_type,
                                "jurisdiction": jurisdiction,
                                "due_date": next_due_date.isoformat(),
                                "frequency": freq.frequency,
                                "estimated_tax": str(total_tax)
                            })
                    
                    break
        
        # Sort filings by due date
        compliance_status["upcoming_filings"].sort(key=lambda x: x["due_date"])
        compliance_status["overdue_filings"].sort(key=lambda x: x["due_date"])
        
        return compliance_status
    
    def _get_last_filing(
        self, 
        company_id: str, 
        tax_type: str, 
        jurisdiction_code: str
    ) -> Optional[Dict[str, Any]]:
        """Get the last tax filing for a company, tax type, and jurisdiction."""
        filing = self.db.query(models.TaxFiling).filter(
            models.TaxFiling.company_id == company_id,
            models.TaxFiling.tax_type == tax_type,
            models.TaxFiling.jurisdiction_code == jurisdiction_code,
            models.TaxFiling.status == "filed"
        ).order_by(models.TaxFiling.period_end.desc()).first()
        
        if filing:
            return {
                "filing_id": str(filing.id),
                "period_start": filing.period_start,
                "period_end": filing.period_end,
                "filing_date": filing.filing_date,
                "tax_amount": filing.tax_amount
            }
        return None
    
    def _calculate_next_due_date(
        self, 
        frequency: str, 
        last_period_end: Optional[date] = None
    ) -> Optional[date]:
        """Calculate the next due date based on filing frequency and last period end."""
        today = date.today()
        
        if not last_period_end:
            # If no previous filing, use the beginning of the current period
            if frequency == "monthly":
                last_period_end = date(today.year, today.month, 1) - timedelta(days=1)
            elif frequency == "quarterly":
                quarter = (today.month - 1) // 3
                last_period_end = date(today.year, quarter * 3 + 1, 1) - timedelta(days=1)
            elif frequency == "annually":
                last_period_end = date(today.year - 1, 12, 31)
            else:
                return None
        
        # Calculate next period end and due date
        if frequency == "monthly":
            next_period_end = (last_period_end + timedelta(days=1)).replace(day=1)
            next_period_end = (next_period_end + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            due_date = next_period_end + timedelta(days=20)  # Example: 20 days after period end
        elif frequency == "quarterly":
            next_period_end = last_period_end + timedelta(days=1)
            month = ((next_period_end.month - 1) // 3 + 1) * 3 + 1
            year = next_period_end.year
            if month > 12:
                month = 1
                year += 1
            next_period_end = date(year, month, 1) - timedelta(days=1)
            due_date = next_period_end + timedelta(days=30)  # Example: 30 days after quarter end
        elif frequency == "annually":
            next_period_end = date(last_period_end.year + 1, 12, 31)
            due_date = date(next_period_end.year + 1, 3, 15)  # Example: March 15 of next year
        else:
            return None
            
        return due_date

# Singleton instance
tax_reporting_service = TaxReportingService(next(settings.get_db()))
