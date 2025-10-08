"""
Tax Reporting Service

This module provides comprehensive tax reporting functionality for the Paksa Financial System.
It handles generation of tax reports, filings, and compliance documentation.
"""

from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple, Union, BinaryIO, Callable, TypeVar
from decimal import Decimal
import logging
import io
import csv
import pandas as pd
import asyncio
import json
from fastapi.responses import StreamingResponse
from fastapi import HTTPException, status, Response, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine.result import ChunkedIteratorResult
import aioredis

from app import crud, models, schemas
from app.core.tax.tax_policy_service import TaxType, TaxJurisdiction, tax_policy_service
from app.core.tax.tax_calculation_service import tax_calculation_service
from app.core.config import settings
from app.core.redis_utils import redis_manager, ReportManager, cache
from app.core.db.session import async_session

# Type variable for generic function return type
T = TypeVar('T')

# Initialize logger
logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

class TaxReportingService:
    def __init__(self, db: Session = None):
        self.db = db
        self.redis = None
        self._redis_initialized = False
    
    async def initialize_redis(self):
        """Initialize Redis connection if not already initialized."""
        if not self._redis_initialized and settings.REDIS_URL and getattr(settings, 'USE_REDIS', False):
            try:
                await redis_manager.initialize()
                self.redis = await redis_manager.redis()
                self._redis_initialized = True
            except Exception as e:
                logger.warning(f"Failed to initialize Redis: {e}")
        else:
            logger.info("Redis is disabled for tax reporting service, skipping initialization")
            self._redis_initialized = True
    
    def _get_cache_key(self, func_name: str, **kwargs) -> str:
        """Generate a consistent cache key for function calls."""
        key_parts = ["tax_reporting", func_name]
        for k, v in sorted(kwargs.items()):
            if isinstance(v, (str, int, float, bool)) or v is None:
                key_parts.append(f"{k}:{v}")
            elif isinstance(v, (list, tuple, set)):
                key_parts.append(f"{k}:{':'.join(str(i) for i in sorted(v))}")
            elif isinstance(v, dict):
                key_parts.append(f"{k}:{json.dumps(v, sort_keys=True)}")
        return ":".join(str(part) for part in key_parts)
    
    async def _get_cached_result(self, key: str) -> Any:
        """Get a cached result from Redis."""
        if not self._redis_initialized:
            return None
            
        try:
            cached = await self.redis.get(f"cache:{key}")
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
        return None
    
    async def _set_cached_result(self, key: str, value: Any, ttl: int = None):
        """Cache a result in Redis."""
        if not self._redis_initialized:
            return
            
        try:
            ttl = ttl or settings.REDIS_CACHE_TTL
            await self.redis.set(
                f"cache:{key}",
                json.dumps(value, default=str),
                ex=ttl
            )
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
    
    @cache(key_prefix="tax_liability_report")
    async def generate_tax_liability_report(
        self,
        company_id: str,
        start_date: date,
        end_date: date,
        tax_types: Optional[List[str]] = None,
        jurisdiction_codes: Optional[List[str]] = None,
        group_by: str = "month",
        page: int = 1,
        page_size: int = 1000,
        force_refresh: bool = False
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
            page: Page number for pagination (1-based)
            page_size: Number of items per page
            
        Returns:
            Dict containing the tax liability report data with pagination info
        """
        # Initialize Redis if not already done
        await self.initialize_redis()
        
        # Generate cache key
        cache_key = self._get_cache_key(
            "generate_tax_liability_report",
            company_id=company_id,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            tax_types=tax_types,
            jurisdiction_codes=jurisdiction_codes,
            group_by=group_by,
            page=page,
            page_size=page_size
        )
        
        # Try to get from cache if not forcing refresh
        if not force_refresh:
            cached_result = await self._get_cached_result(cache_key)
            if cached_result:
                logger.info(f"Cache hit for tax liability report: {cache_key}")
                return cached_result
        
        # Input validation
        if end_date < start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date must be after start date"
            )
        
        # Use async session for better concurrency
        async with async_session() as session:
            # Determine the date truncation function based on group_by
            if group_by == "day":
                trunc_expr = func.date_trunc('day', models.TaxTransaction.transaction_date)
                date_format = "%Y-%m-%d"
            elif group_by == "week":
                # For week, we'll use date_trunc with 'week' and adjust to start on Monday
                trunc_expr = func.date_trunc('week', models.TaxTransaction.transaction_date)
                date_format = "%Y-W%W"
            elif group_by == "quarter":
                trunc_expr = func.date_trunc('quarter', models.TaxTransaction.transaction_date)
                date_format = "%Y-Q%q"
            elif group_by == "year":
                trunc_expr = func.date_trunc('year', models.TaxTransaction.transaction_date)
                date_format = "%Y"
            else:  # month (default)
                trunc_expr = func.date_trunc('month', models.TaxTransaction.transaction_date)
                date_format = "%Y-%m"
            
            # Build the base query with server-side aggregation
            stmt = select(
                trunc_expr.label('period'),
                models.TaxTransaction.tax_type,
                models.TaxTransaction.jurisdiction_code,
                func.sum(models.TaxTransaction.taxable_amount).label('taxable_amount'),
                func.sum(models.TaxTransaction.tax_amount).label('tax_amount'),
                func.count().label('transaction_count')
            ).where(
                models.TaxTransaction.company_id == company_id,
                models.TaxTransaction.transaction_date >= start_date,
                models.TaxTransaction.transaction_date <= end_date,
                models.TaxTransaction.is_reported == False
            )
            
            # Apply filters
            if tax_types:
                stmt = stmt.where(models.TaxTransaction.tax_type.in_(tax_types))
                
            if jurisdiction_codes:
                stmt = stmt.where(models.TaxTransaction.jurisdiction_code.in_(jurisdiction_codes))
            
            # Group by period, tax_type, and jurisdiction_code
            stmt = stmt.group_by(
                trunc_expr,
                models.TaxTransaction.tax_type,
                models.TaxTransaction.jurisdiction_code
            )
            
            # Get total count for pagination (using a subquery for better performance)
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total_count = (await session.execute(count_stmt)).scalar() or 0
            
            # Apply pagination
            stmt = stmt.offset((page - 1) * page_size).limit(page_size)
            
            # Execute the query
            result = await session.execute(stmt)
            results = result.all()
        
        # Process results into period_totals structure
        period_totals = {}
        
        # Process results using list comprehension for better performance
        for row in results:
            period_key = row.period.strftime(date_format)
            
            # Initialize period if not exists using dict.setdefault
            period = period_totals.setdefault(period_key, {
                "taxable_amount": Decimal("0.00"),
                "tax_amount": Decimal("0.00"),
                "transaction_count": 0,
                "tax_types": {},
                "jurisdictions": {}
            })
            
            # Convert None to 0 for calculations
            taxable_amount = row.taxable_amount or Decimal("0.00")
            tax_amount = row.tax_amount or Decimal("0.00")
            transaction_count = row.transaction_count or 0
            
            # Update period totals
            period["taxable_amount"] += taxable_amount
            period["tax_amount"] += tax_amount
            period["transaction_count"] += transaction_count
            
            # Update tax type breakdown
            tax_type_data = period["tax_types"].setdefault(row.tax_type, {
                "taxable_amount": Decimal("0.00"),
                "tax_amount": Decimal("0.00")
            })
            tax_type_data["taxable_amount"] += taxable_amount
            tax_type_data["tax_amount"] += tax_amount
            
            # Update jurisdiction breakdown
            jurisdiction_data = period["jurisdictions"].setdefault(row.jurisdiction_code, {
                "taxable_amount": Decimal("0.00"),
                "tax_amount": Decimal("0.00")
            })
            jurisdiction_data["taxable_amount"] += taxable_amount
            jurisdiction_data["tax_amount"] += tax_amount
        
        # Calculate grand totals using optimized sum with generator expressions
        total_taxable = sum((p["taxable_amount"] for p in period_totals.values()), Decimal("0.00"))
        total_tax = sum((p["tax_amount"] for p in period_totals.values()), Decimal("0.00"))
        total_transactions = sum((p["transaction_count"] for p in period_totals.values()), 0)
        
        # Prepare response with pagination info
        response_data = {
            "company_id": company_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_taxable_amount": str(total_taxable.quantize(Decimal('0.00'))),
            "total_tax_amount": str(total_tax.quantize(Decimal('0.00'))),
            "total_transactions": total_transactions,
            "periods": [
                {"period": period, **data} 
                for period, data in sorted(period_totals.items())
            ],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total_count,
                "total_pages": (total_count + page_size - 1) // page_size if page_size > 0 else 0
            },
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "tax_types": tax_types or "All",
                "jurisdiction_codes": jurisdiction_codes or "All",
                "group_by": group_by,
                "cache_key": cache_key,
                "cached": False
            }
        }
        
        # Cache the result
        await self._set_cached_result(cache_key, response_data)
        
        return response_data
        
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

    def export_tax_report(
        self,
        report_type: str,
        format_type: str,
        company_id: str,
        start_date: date,
        end_date: date,
        tax_types: Optional[List[str]] = None,
        jurisdiction_codes: Optional[List[str]] = None,
        **kwargs
    ) -> Union[Response, Dict[str, Any]]:
        """
        Export tax report in the specified format.
        
        Args:
            report_type: Type of report to export (liability, transactions, etc.)
            format_type: Export format (csv, excel, pdf)
            company_id: ID of the company
            start_date: Start date of the reporting period
            end_date: End date of the reporting period
            tax_types: Optional list of tax types to include
            jurisdiction_codes: Optional list of jurisdiction codes to filter by
            **kwargs: Additional format-specific parameters
            
        Returns:
            StreamingResponse or dict containing the exported data
        """
        try:
            # Get the report data based on report_type
            if report_type == 'liability':
                report_data = self.generate_tax_liability_report(
                    company_id=company_id,
                    start_date=start_date,
                    end_date=end_date,
                    tax_types=tax_types,
                    jurisdiction_codes=jurisdiction_codes,
                    **kwargs
                )
            elif report_type == 'transactions':
                report_data = self.get_tax_transactions(
                    company_id=company_id,
                    start_date=start_date,
                    end_date=end_date,
                    tax_types=tax_types,
                    jurisdiction_codes=jurisdiction_codes,
                    **kwargs
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported report type: {report_type}"
                )
            
            # Format the data based on the requested format
            if format_type == 'csv':
                return self._export_to_csv(report_data, report_type)
            elif format_type == 'excel':
                return self._export_to_excel(report_data, report_type)
            elif format_type == 'pdf':
                return self._export_to_pdf(report_data, report_type)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported export format: {format_type}"
                )
                
        except Exception as e:
            logger.error(f"Error exporting {report_type} report: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating export: {str(e)}"
            )
    
    def _export_to_csv(self, data: Dict[str, Any], report_type: str) -> Response:
        """Convert report data to CSV format."""
        if report_type == 'liability':
            # Flatten the periods data for CSV
            rows = []
            for period in data.get('periods', []):
                row = {
                    'period': period.get('period'),
                    'taxable_amount': period.get('taxable_amount', 0),
                    'tax_amount': period.get('tax_amount', 0),
                    'transactions': period.get('transaction_count', 0),
                }
                # Add tax type breakdowns if available
                for tax_type, amount in period.get('tax_types', {}).items():
                    row[f'tax_type_{tax_type}'] = amount
                rows.append(row)
            
            # Convert to DataFrame for easier CSV generation
            df = pd.DataFrame(rows)
            
            # Create a buffer to store CSV data
            buffer = io.StringIO()
            df.to_csv(buffer, index=False, encoding='utf-8')
            buffer.seek(0)
            
            # Create and return the streaming response
            response = StreamingResponse(
                iter([buffer.getvalue()]),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment;filename=tax_liability_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                }
            )
            return response
            
        # Add handling for other report types as needed
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CSV export not implemented for {report_type} report type"
        )
    
    def _export_to_excel(self, data: Dict[str, Any], report_type: str) -> Response:
        """Convert report data to Excel format."""
        try:
            if report_type == 'liability':
                # Flatten the periods data for Excel
                rows = []
                for period in data.get('periods', []):
                    row = {
                        'Period': period.get('period'),
                        'Taxable Amount': period.get('taxable_amount', 0),
                        'Tax Amount': period.get('tax_amount', 0),
                        'Transactions': period.get('transaction_count', 0),
                    }
                    # Add tax type breakdowns if available
                    for tax_type, amount in period.get('tax_types', {}).items():
                        row[f'Tax Type: {tax_type}'] = amount
                    rows.append(row)
                
                # Convert to DataFrame
                df = pd.DataFrame(rows)
                
                # Create a buffer to store Excel data
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Tax Liability')
                    
                    # Get the workbook and worksheet objects
                    workbook = writer.book
                    worksheet = writer.sheets['Tax Liability']
                    
                    # Add a header format
                    header_format = workbook.add_format({
                        'bold': True,
                        'text_wrap': True,
                        'valign': 'top',
                        'fg_color': '#4472C4',
                        'font_color': 'white',
                        'border': 1
                    })
                    
                    # Write the column headers with the defined format
                    for col_num, value in enumerate(df.columns.values):
                        worksheet.write(0, col_num, value, header_format)
                    
                    # Auto-adjust column widths
                    for i, col in enumerate(df.columns):
                        max_length = max(
                            df[col].astype(str).apply(len).max(),
                            len(str(col))
                        ) + 2  # Add a little extra space
                        worksheet.set_column(i, i, min(max_length, 30))
                
                buffer.seek(0)
                
                # Create and return the streaming response
                return StreamingResponse(
                    buffer,
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={
                        "Content-Disposition": f"attachment;filename=tax_liability_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    }
                )
            
            # Add handling for other report types as needed
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Excel export not implemented for {report_type} report type"
            )
            
        except Exception as e:
            logger.error(f"Error generating Excel export: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating Excel export: {str(e)}"
            )
    
    def _create_chart_image(self, chart_data: Dict[str, Any], chart_type: str = 'bar', size: tuple = (400, 250)) -> BytesIO:
        """
        Create a chart image using matplotlib and return it as a BytesIO object.
        
        Args:
            chart_data: Data for the chart
            chart_type: Type of chart ('bar', 'line', 'pie', 'scatter')
            size: Size of the chart in pixels (width, height)
            
        Returns:
            BytesIO object containing the chart image
        """
        import matplotlib.pyplot as plt
        from matplotlib.ticker import FuncFormatter
        import numpy as np
        
        # Set up the figure and axis
        plt.style.use('seaborn')
        fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
        
        # Format y-axis as currency
        def currency(x, pos):
            return '${:,.0f}'.format(x)
        
        formatter = FuncFormatter(currency)
        
        # Generate chart based on type
        if chart_type == 'bar' and 'categories' in chart_data and 'values' in chart_data:
            x = np.arange(len(chart_data['categories']))
            bars = ax.bar(x, chart_data['values'], color='#3498db')
            ax.set_xticks(x)
            ax.set_xticklabels(chart_data['categories'], rotation=45, ha='right')
            ax.yaxis.set_major_formatter(formatter)
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'${height:,.0f}',
                        ha='center', va='bottom')
            
        elif chart_type == 'line' and 'x' in chart_data and 'y' in chart_data:
            ax.plot(chart_data['x'], chart_data['y'], marker='o', color='#e74c3c', linewidth=2)
            ax.yaxis.set_major_formatter(formatter)
            
        elif chart_type == 'pie' and 'labels' in chart_data and 'sizes' in chart_data:
            wedges, texts, autotexts = ax.pie(
                chart_data['sizes'],
                labels=chart_data['labels'],
                autopct='%1.1f%%',
                startangle=90,
                colors=['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6']
            )
            ax.axis('equal')
            
        elif chart_type == 'scatter' and 'x' in chart_data and 'y' in chart_data:
            ax.scatter(chart_data['x'], chart_data['y'], color='#2ecc71', alpha=0.6, edgecolors='w')
            ax.yaxis.set_major_formatter(formatter)
        
        # Customize the chart
        if 'title' in chart_data:
            ax.set_title(chart_data['title'], pad=20, fontsize=12, fontweight='bold')
        if 'xlabel' in chart_data:
            ax.set_xlabel(chart_data['xlabel'], labelpad=10)
        if 'ylabel' in chart_data:
            ax.set_ylabel(chart_data['ylabel'], labelpad=10)
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        # Save the chart to a BytesIO object
        img_data = BytesIO()
        plt.savefig(img_data, format='png', dpi=100, bbox_inches='tight')
        img_data.seek(0)
        plt.close()
        
        return img_data
    
    def _add_watermark(self, canvas, doc):
        """Add a watermark to the PDF."""
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.colors import Color, lightgrey
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph
        
        # Save the graphics state
        canvas.saveState()
        
        # Set the font and size
        try:
            pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
            font_name = 'DejaVuSans'
        except:
            font_name = 'Helvetica'
        
        # Set the fill color to light grey
        canvas.setFillColor(lightgrey)
        
        # Set the font and size
        canvas.setFont(font_name, 60)
        
        # Get the page size
        width, height = letter
        
        # Draw the watermark text at 45 degrees across the page
        canvas.translate(width/2, height/2)
        canvas.rotate(45)
        
        # Add the text
        canvas.drawCentredString(0, 0, "CONFIDENTIAL")
        
        # Restore the graphics state
        canvas.restoreState()
    
    def _add_company_logo(self, elements, doc_width, logo_path: str = None):
        """Add company logo to the PDF."""
        from reportlab.platypus import Image, Spacer
        from reportlab.lib.units import inch
        
        # If no logo path is provided, use a placeholder or skip
        if not logo_path or not os.path.exists(logo_path):
            return
            
        try:
            logo = Image(logo_path, width=1.5*inch, height=0.5*inch)
            logo.hAlign = 'RIGHT'
            elements.append(logo)
            elements.append(Spacer(1, 10))
        except Exception as e:
            logger.warning(f"Could not add company logo: {str(e)}")
    
    def _export_to_pdf(self, data: Dict[str, Any], report_type: str) -> StreamingResponse:
        """
        Convert report data to PDF format using ReportLab.
        
        Args:
            data: The report data to convert to PDF
            report_type: Type of report being generated ('liability', 'compliance', 'transactions', 'trends')
            
        Returns:
            StreamingResponse containing the PDF file
        """
        try:
            from io import BytesIO
            import os
            import base64
            from datetime import datetime
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter, landscape, A4
            from reportlab.platypus import (
                SimpleDocTemplate, Table, TableStyle, 
                Paragraph, Spacer, Image, PageBreak,
                ListFlowable, ListItem, HRFlowable
            )
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch, cm
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
            from reportlab.platypus.flowables import KeepTogether, PageBreakIfTooFull
            from reportlab.lib.pagesizes import mm
            from reportlab.pdfgen import canvas
            from reportlab.platypus.doctemplate import BaseDocTemplate, PageTemplate, Frame
            from reportlab.platypus.frames import Frame
            from reportlab.lib.utils import ImageReader
            import tempfile
            import matplotlib.pyplot as plt
            import numpy as np
            from typing import List, Tuple, Dict, Any, Optional, Union
            
            # Create a buffer to store the PDF
            buffer = BytesIO()
            
            # Define page size and margins
            page_width, page_height = landscape(A4)
            
            # Define a custom canvas class for header/footer
            class NumberedCanvas(canvas.Canvas):
                def __init__(self, *args, **kwargs):
                    canvas.Canvas.__init__(self, *args, **kwargs)
                    self._saved_page_states = []
                    
                def showPage(self):
                    self._saved_page_states.append(dict(self.__dict__))
                    self._startPage()
                    
                def save(self):
                    """Add page info to each page (page x of y)"""
                    num_pages = len(self._saved_page_states)
                    for state in self._saved_page_states:
                        self.__dict__.update(state)
                        self._pageNumber += 1
                        self.draw_header()
                        self.draw_footer(num_pages)
                        self.draw_watermark()
                        canvas.Canvas.showPage(self)
                    canvas.Canvas.save(self)
                    
                def draw_header(self):
                    """Draw the header on each page"""
                    self.saveState()
                    self.setFont(font_name, 8)
                    self.setFillColor(colors.HexColor('#95a5a6'))
                    
                    # Draw a line below header
                    self.setStrokeColor(colors.HexColor('#e9ecef'))
                    self.line(30, page_height - 70, page_width - 30, page_height - 70)
                    
                    # Add page info (right-aligned)
                    self.drawRightString(page_width - 30, page_height - 65, 
                                       f"Page {self._pageNumber}")
                    
                    # Add report title (left-aligned)
                    self.drawString(30, page_height - 65, 
                                  f"{report_type.replace('_', ' ').title()} Report")
                    self.restoreState()
                    
                def draw_footer(self, num_pages):
                    """Draw the footer on each page"""
                    self.saveState()
                    self.setFont(font_name, 7)
                    self.setFillColor(colors.HexColor('#95a5a6'))
                    
                    # Draw a line above footer
                    self.setStrokeColor(colors.HexColor('#e9ecef'))
                    self.line(30, 40, page_width - 30, 40)
                    
                    # Add footer text (centered)
                    footer_text = f"© {datetime.now().year} Paksa Financial System - Confidential"
                    self.drawCentredString(page_width / 2, 30, footer_text)
                    
                    # Add page x of y
                    page_info = f"Page {self._pageNumber} of {num_pages}"
                    self.drawRightString(page_width - 30, 30, page_info)
                    
                    # Add timestamp
                    self.drawString(30, 30, 
                                  f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    self.restoreState()
                    
                def draw_watermark(self):
                    """Add a light watermark to each page"""
                    self.saveState()
                    self.setFont(font_name, 80)
                    self.setFillColor(colors.HexColor('#f5f5f5'))
                    self.setFillAlpha(0.1)
                    
                    # Rotate the canvas for diagonal watermark
                    self.translate(page_width/2, page_height/2)
                    self.rotate(45)
                    
                    # Draw the watermark text
                    self.drawCentredString(0, 0, "CONFIDENTIAL")
                    self.restoreState()
            
            # Set up the document with landscape orientation for better table display
            doc = SimpleDocTemplate(
                buffer,
                pagesize=landscape(A4),
                rightMargin=30,
                leftMargin=30,
                topMargin=100,  # Space for header
                bottomMargin=60,  # Space for footer
                title=f"Tax Report - {report_type.replace('_', ' ').title()}",
                author="Paksa Financial System",
                subject=f"Tax Report - {report_type}",
                creator="Paksa Financial System - Tax Module",
                keywords=["tax", "report", "financial", report_type]
            )
            
            # Register fonts (you might need to adjust paths based on your setup)
            try:
                # Try to register a standard font
                pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
                pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))
                font_name = 'DejaVuSans'
                bold_font_name = 'DejaVuSans-Bold'
            except:
                # Fall back to default font if custom font not available
                font_name = 'Helvetica'
                bold_font_name = 'Helvetica-Bold'
            
            # Define custom styles
            styles = getSampleStyleSheet()
            
            # Add custom styles
            styles.add(ParagraphStyle(
                name='Title',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=12,
                textColor=colors.HexColor('#2c3e50'),
                fontName=bold_font_name,
                alignment=TA_CENTER
            ))
            
            styles.add(ParagraphStyle(
                name='Subtitle',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=12,
                textColor=colors.HexColor('#7f8c8d'),
                alignment=TA_CENTER
            ))
            
            styles.add(ParagraphStyle(
                name='SectionHeader',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=10,
                textColor=colors.HexColor('#2c3e50'),
                fontName=bold_font_name,
                backColor=colors.HexColor('#f8f9fa'),
                borderWidth=1,
                borderColor=colors.HexColor('#e9ecef'),
                borderPadding=(5, 5, 5, 5)
            ))
            
            # Create the elements list to hold all content
            elements = []
            
            # Add header with logo and title
            header_table = Table([
                [
                    # Left side: Company info
                    Table([
                        [Paragraph("<b>Paksa Financial System</b>", 
                                 ParagraphStyle('CompanyName', parent=styles['Normal'], fontSize=12, textColor=colors.HexColor('#2c3e50')))],
                        [Paragraph("Tax Reporting Module", 
                                 ParagraphStyle('ModuleName', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#7f8c8d')))],
                        [Paragraph("123 Finance St, City, Country", 
                                 ParagraphStyle('Address', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#95a5a6')))],
                        [Paragraph("www.paksa.com | contact@paksa.com", 
                                 ParagraphStyle('Contact', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#95a5a6')))]
                    ], colWidths=[doc.width * 0.6]),
                    
                    # Right side: Report title
                    Table([
                        [Paragraph("TAX REPORT", 
                                 ParagraphStyle('ReportTitle', parent=styles['Title'], fontSize=16, textColor=colors.HexColor('#2c3e50'), alignment=TA_RIGHT))],
                        [Paragraph(f"{report_type.replace('_', ' ').title()}", 
                                 ParagraphStyle('ReportType', parent=styles['Normal'], fontSize=12, textColor=colors.HexColor('#7f8c8d'), alignment=TA_RIGHT))],
                        [Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                                 ParagraphStyle('Timestamp', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#95a5a6'), alignment=TA_RIGHT))]
                    ], colWidths=[doc.width * 0.4])
                ]
            ], colWidths=[doc.width * 0.6, doc.width * 0.4])
            
            # Style the header table
            header_table.setStyle(TableStyle([
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMBORDER', (0, 0), (-1, -1), 1, colors.HexColor('#e9ecef')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            elements.append(header_table)
            elements.append(Spacer(1, 15))  # Add some space after header
            
            # Add report metadata section
            metadata_table = Table([
                ["Report Period:", f"{data.get('start_date', 'N/A')} to {data.get('end_date', 'N/A')}", 
                 "Company:", data.get('company_name', 'N/A')],
                ["Prepared by:", data.get('prepared_by', 'System User'), 
                 "Report ID:", f"TAX-{datetime.now().strftime('%Y%m%d')}-{report_type.upper()[:3]}"]
            ], colWidths=[doc.width * 0.15, doc.width * 0.35, doc.width * 0.15, doc.width * 0.35])
            
            metadata_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (0, -1), bold_font_name),
                ('FONTNAME', (2, 0), (2, -1), bold_font_name),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#7f8c8d')),
                ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#7f8c8d')),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (3, 0), (3, -1), colors.HexColor('#2c3e50')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#f1f3f4')),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
            ]))
            
            elements.append(metadata_table)
            elements.append(Spacer(1, 20))  # Add space before main content
            
            # Add a page break if needed before the main content
            elements.append(PageBreakIfTooFull(0, 0))
            
            # Add executive summary section
            if report_type in ['liability', 'filing', 'payment']:
                # Add section header
                elements.append(Paragraph("Executive Summary", styles['SectionHeader']))
                elements.append(Spacer(1, 10))
                
                # Generate summary statistics based on report type
                if report_type == 'liability':
                    total_liability = sum(float(item.get('amount', 0)) for item in data.get('items', []))
                    summary_data = [
                        ["Total Tax Liability", f"{total_liability:,.2f} {data.get('currency', 'USD')}"],
                        ["Number of Tax Items", len(data.get('items', []))],
                        ["Reporting Period", f"{data.get('start_date', 'N/A')} to {data.get('end_date', 'N/A')}"],
                        ["Tax Authority", data.get('tax_authority', 'N/A')],
                        ["Filing Status", data.get('filing_status', 'Pending')]
                    ]
                elif report_type == 'filing':
                    summary_data = [
                        ["Filing Reference", data.get('filing_reference', 'N/A')],
                        ["Filing Period", f"{data.get('start_date', 'N/A')} to {data.get('end_date', 'N/A')}"],
                        ["Filing Status", data.get('status', 'Draft')],
                        ["Submission Date", data.get('submission_date', 'N/A')],
                        ["Tax Authority", data.get('tax_authority', 'N/A')],
                        ["Total Tax Amount", f"{data.get('total_amount', 0):,.2f} {data.get('currency', 'USD')}"]
                    ]
                else:  # payment
                    summary_data = [
                        ["Payment Reference", data.get('payment_reference', 'N/A')],
                        ["Payment Date", data.get('payment_date', 'N/A')],
                        ["Payment Method", data.get('payment_method', 'N/A')],
                        ["Payment Status", data.get('status', 'Pending')],
                        ["Amount Paid", f"{data.get('amount', 0):,.2f} {data.get('currency', 'USD')}"],
                        ["Tax Authority", data.get('tax_authority', 'N/A')]
                    ]
                
                # Create summary table
                summary_table = Table(summary_data, colWidths=[doc.width * 0.4, doc.width * 0.6])
                summary_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), font_name),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 0), (0, -1), bold_font_name),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#7f8c8d')),
                    ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#2c3e50')),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#f1f3f4')),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
                ]))
                
                elements.append(summary_table)
                elements.append(Spacer(1, 20))
                
                # Add visual chart if data is available
                if report_type == 'liability' and 'items' in data and len(data['items']) > 0:
                    try:
                        from matplotlib import pyplot as plt
                        from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
                        from matplotlib.figure import Figure
                        import numpy as np
                        
                        # Prepare data for chart
                        items = data['items']
                        categories = [item.get('category', 'Other') for item in items]
                        amounts = [float(item.get('amount', 0)) for item in items]
                        
                        # Sort by amount (descending)
                        sorted_data = sorted(zip(amounts, categories), reverse=True)
                        amounts, categories = zip(*sorted_data)
                        
                        # Create a horizontal bar chart
                        fig = Figure(figsize=(8, min(6, len(categories) * 0.5)))
                        ax = fig.add_subplot(111)
                        
                        y_pos = np.arange(len(categories))
                        ax.barh(y_pos, amounts, color='#3498db')
                        ax.set_yticks(y_pos)
                        ax.set_yticklabels(categories)
                        ax.invert_yaxis()  # highest values at top
                        ax.set_xlabel('Amount')
                        ax.set_title('Tax Liability by Category')
                        
                        # Save chart to buffer
                        chart_buffer = BytesIO()
                        FigureCanvas(fig).print_png(chart_buffer)
                        chart_buffer.seek(0)
                        
                        # Add chart to PDF
                        elements.append(Paragraph("Tax Liability Distribution", styles['SectionHeader']))
                        elements.append(Spacer(1, 10))
                        elements.append(Image(chart_buffer, width=doc.width * 0.8, height=200))
                        elements.append(Spacer(1, 20))
                        
                    except ImportError:
                        # Fallback if matplotlib is not available
                        logger.warning("Matplotlib not available. Skipping chart generation.")
                        pass
            
            # Add page break before detailed content
            elements.append(PageBreakIfTooFull(0, 0))
            elements.append(Spacer(1, 10))
            
            # Generate content based on report type
            if report_type == 'liability':
                # Create summary table
                summary_data = [
                    ["Total Taxable Amount", f"${data.get('total_taxable_amount', '0.00')}"],
                    ["Total Tax Amount", f"${data.get('total_tax_amount', '0.00')}"],
                    ["Total Transactions", data.get('total_transactions', 0)]
                ]
                
                summary_table = Table(summary_data, colWidths=[doc.width * 0.5, doc.width * 0.5])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e9ecef')),
                ]))
                
                elements.append(Paragraph("Summary", styles['Heading3']))
                elements.append(Spacer(1, 10))
                elements.append(summary_table)
                elements.append(Spacer(1, 20))
                
                # Add detailed data table if available
                if 'periods' in data and data['periods']:
                    periods = data['periods']
                    
                    # Prepare table data
                    table_data = [["Period", "Taxable Amount", "Tax Amount", "Transactions"]]
                    
                    # Add tax type columns if available
                    tax_types = set()
                    for period in periods:
                        if 'tax_types' in period:
                            tax_types.update(period['tax_types'].keys())
                    
                    # Sort tax types for consistent ordering
                    tax_types = sorted(list(tax_types))
                    table_data[0].extend(tax_types)
                    
                    # Add data rows
                    for period in periods:
                        row = [
                            period.get('period', 'N/A'),
                            f"${period.get('taxable_amount', 0):,.2f}",
                            f"${period.get('tax_amount', 0):,.2f}",
                            str(period.get('transaction_count', 0))
                        ]
                        
                        # Add tax type amounts
                        for tax_type in tax_types:
                            amount = period.get('tax_types', {}).get(tax_type, 0)
                            row.append(f"${amount:,.2f}")
                        
                        table_data.append(row)
                    
                    # Create and style the table
                    col_widths = [doc.width * 0.2]  # Period column
                    col_widths.extend([doc.width * 0.15] * 3)  # Amount and transaction columns
                    col_widths.extend([doc.width * 0.1] * len(tax_types))  # Tax type columns
                    
                    # Ensure we don't exceed page width
                    total_width = sum(col_widths)
                    if total_width > doc.width:
                        scale = doc.width / total_width
                        col_widths = [w * scale for w in col_widths]
                    
                    table = Table(table_data, colWidths=col_widths, repeatRows=1)
                    
                    # Apply table styles
                    table.setStyle(TableStyle([
                        # Header
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                        
                        # Data rows
                        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),  # Right-align numbers
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                        
                        # Grid
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e9ecef')),
                        
                        # Alternating row colors
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                        
                        # Highlight totals row if present
                        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                    ]))
                    
                    elements.append(Paragraph("Detailed Breakdown", styles['Heading3']))
                    elements.append(Spacer(1, 10))
                    elements.append(table)
            
            # Add footer with page numbers
            def add_page_number(canvas, doc):
                canvas.saveState()
                canvas.setFont('Helvetica', 8)
                page_num = canvas.getPageNumber()
                text = f"Page {page_num}"
                canvas.drawRightString(doc.width + doc.leftMargin, 0.4 * inch, text)
                canvas.drawString(doc.leftMargin, 0.4 * inch, f"{title} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                canvas.restoreState()
            
            # Build the PDF
            doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
            
            # Get the value of the BytesIO buffer and write it to the response
            buffer.seek(0)
            
            # Generate a filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"tax_{report_type}_report_{timestamp}.pdf"
            
            # Return the PDF as a streaming response
            return StreamingResponse(
                iter([buffer.getvalue()]),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}",
                    "Content-Length": str(len(buffer.getvalue()))
                }
            )
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating PDF: {str(e)}"
            )

    async def generate_liability_report_async(
        self,
        company_id: str,
        start_date: date,
        end_date: date,
        tax_types: Optional[List[str]] = None,
        jurisdiction_codes: Optional[List[str]] = None,
        group_by: str = "month",
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a tax liability report asynchronously and store the result in Redis.
        
        Args:
            company_id: ID of the company
            start_date: Start date of the reporting period
            end_date: End date of the reporting period
            tax_types: Optional list of tax types to include
            jurisdiction_codes: Optional list of jurisdiction codes to include
            group_by: How to group the results (day, week, month, quarter, year)
            callback_url: Optional URL to call when the report is ready
            
        Returns:
            Dict containing the report ID and status endpoint
        """
        # Generate a unique report ID
        report_id = await ReportManager.generate_report_id(
            company_id=company_id,
            report_type="tax_liability",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "tax_types": tax_types,
                "jurisdiction_codes": jurisdiction_codes,
                "group_by": group_by
            }
        )
        
        # Store initial status
        await ReportManager.store_report_status(
            report_id=report_id,
            status="pending",
            result=None
        )
        
        # Start background task
        asyncio.create_task(self._generate_report_background(
            report_id=report_id,
            company_id=company_id,
            start_date=start_date,
            end_date=end_date,
            tax_types=tax_types,
            jurisdiction_codes=jurisdiction_codes,
            group_by=group_by,
            callback_url=callback_url
        ))
        
        return {
            "report_id": report_id,
            "status": "pending",
            "status_endpoint": f"/api/v1/tax/reports/status/{report_id}",
            "download_endpoint": f"/api/v1/tax/reports/download/{report_id}",
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def _generate_report_background(
        self,
        report_id: str,
        company_id: str,
        start_date: date,
        end_date: date,
        tax_types: Optional[List[str]] = None,
        jurisdiction_codes: Optional[List[str]] = None,
        group_by: str = "month",
        callback_url: Optional[str] = None
    ) -> None:
        """Background task to generate a tax liability report."""
        try:
            # Update status to in_progress
            await ReportManager.store_report_status(
                report_id=report_id,
                status="in_progress",
                result={"progress": 0, "message": "Starting report generation..."}
            )
            
            # Generate the report
            report = await self.generate_tax_liability_report(
                company_id=company_id,
                start_date=start_date,
                end_date=end_date,
                tax_types=tax_types,
                jurisdiction_codes=jurisdiction_codes,
                group_by=group_by,
                force_refresh=True
            )
            
            # Store the result
            await ReportManager.store_report_status(
                report_id=report_id,
                status="completed",
                result={
                    "progress": 100,
                    "message": "Report generated successfully",
                    "report": report
                }
            )
            
            # Call the callback URL if provided
            if callback_url:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            callback_url,
                            json={
                                "report_id": report_id,
                                "status": "completed",
                                "download_url": f"/api/v1/tax/reports/download/{report_id}"
                            },
                            timeout=10
                        ) as response:
                            if response.status >= 400:
                                logger.error(f"Callback to {callback_url} failed with status {response.status}")
                except Exception as e:
                    logger.error(f"Error calling callback URL {callback_url}: {e}")
            
        except Exception as e:
            logger.exception(f"Error generating report {report_id}")
            await ReportManager.store_report_status(
                report_id=report_id,
                status="failed",
                error=str(e)
            )
            
            # Call the callback URL with error if provided
            if callback_url:
                try:
                    async with aiohttp.ClientSession() as session:
                        await session.post(
                            callback_url,
                            json={
                                "report_id": report_id,
                                "status": "failed",
                                "error": str(e)
                            },
                            timeout=10
                        )
                except Exception as callback_error:
                    logger.error(f"Error calling callback URL on error: {callback_error}")
    
    async def get_report_status(self, report_id: str) -> Dict[str, Any]:
        """Get the status of a report generation task."""
        status_data = await ReportManager.get_report_status(report_id)
        if not status_data or "status" not in status_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report {report_id} not found"
            )
        return status_data
    
    async def download_report(self, report_id: str, format: str = "json") -> Any:
        """
        Download a generated report in the specified format.
        
        Args:
            report_id: The ID of the report to download
            format: The format to return the report in (json, csv, xlsx)
            
        Returns:
            The report data in the requested format
        """
        # Get the report status
        status_data = await self.get_report_status(report_id)
        
        if status_data["status"] != "completed" or "report" not in status_data.get("result", {}):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report {report_id} not found or not yet complete"
            )
        
        report_data = status_data["result"]["report"]
        
        # Return in the requested format
        if format.lower() == "json":
            return report_data
        elif format.lower() == "csv":
            return await self._convert_to_csv(report_data)
        elif format.lower() in ["xlsx", "excel"]:
            return await self._convert_to_excel(report_data)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported format: {format}. Supported formats: json, csv, xlsx"
            )
    
    async def _convert_to_csv(self, report_data: Dict[str, Any]) -> StreamingResponse:
        """Convert report data to CSV format."""
        # Flatten the report data for CSV
        rows = []
        for period in report_data["periods"]:
            for tax_type, tax_data in period.get("tax_types", {}).items():
                for jurisdiction, jurisdiction_data in period.get("jurisdictions", {}).items():
                    rows.append({
                        "period": period["period"],
                        "tax_type": tax_type,
                        "jurisdiction": jurisdiction,
                        "taxable_amount": jurisdiction_data.get("taxable_amount", 0),
                        "tax_amount": jurisdiction_data.get("tax_amount", 0)
                    })
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["period", "tax_type", "jurisdiction", "taxable_amount", "tax_amount"])
        writer.writeheader()
        writer.writerows(rows)
        
        # Return as streaming response
        response = StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=tax_report_{report_data['start_date']}_to_{report_data['end_date']}.csv"
            }
        )
        return response
    
    async def _convert_to_excel(self, report_data: Dict[str, Any]) -> StreamingResponse:
        """Convert report data to Excel format."""
        # Create a DataFrame from the report data
        rows = []
        for period in report_data["periods"]:
            for tax_type, tax_data in period.get("tax_types", {}).items():
                for jurisdiction, jurisdiction_data in period.get("jurisdictions", {}).items():
                    rows.append({
                        "Period": period["period"],
                        "Tax Type": tax_type,
                        "Jurisdiction": jurisdiction,
                        "Taxable Amount": float(jurisdiction_data.get("taxable_amount", 0)),
                        "Tax Amount": float(jurisdiction_data.get("tax_amount", 0))
                    })
        
        df = pd.DataFrame(rows)
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Tax Report', index=False)
            
            # Get the workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets['Tax Report']
            
            # Add some formatting
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })
            
            # Write the column headers with the defined format
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Set column widths
            worksheet.set_column('A:A', 15)  # Period
            worksheet.set_column('B:B', 20)  # Tax Type
            worksheet.set_column('C:C', 20)  # Jurisdiction
            worksheet.set_column('D:E', 15)  # Numeric columns
        
        # Prepare the response
        output.seek(0)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=tax_report_{report_data['start_date']}_to_{report_data['end_date']}.xlsx"
            }
        )

# Singleton instance
tax_reporting_service = TaxReportingService()
