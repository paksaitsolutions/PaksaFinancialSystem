"""
Database optimization utilities for tax reporting.

This module provides optimized database access patterns and query building
for tax reporting operations.
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_, select, text, desc, asc
from sqlalchemy.sql.expression import case, literal_column

from app import models
from app.core.config import settings

class TaxQueryOptimizer:
    """Optimized query builder for tax reporting operations."""
    
    def __init__(self, db: Session):
        self.db = db
        
    async def get_liability_report_data(
        self,
        company_id: str,
        start_date: date,
        end_date: date,
        tax_types: Optional[List[str]] = None,
        jurisdiction_codes: Optional[List[str]] = None,
        group_by: str = "month",
        page: int = 1,
        page_size: int = 1000
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Fetch optimized tax liability report data with pagination.
        
        Args:
            company_id: ID of the company
            start_date: Start date of the reporting period
            end_date: End date of the reporting period
            tax_types: Optional list of tax types to include
            jurisdiction_codes: Optional list of jurisdiction codes
            group_by: Time period to group by (day, week, month, quarter, year)
            page: Page number (1-based)
            page_size: Number of items per page
            
        Returns:
            Tuple of (results, total_count)
        """
        # Determine the date truncation function based on group_by
        trunc_expr = self._get_date_trunc_expr(group_by)
        date_format = self._get_date_format(group_by)
        
        # Build base query with only necessary columns
        base_query = select(
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
            base_query = base_query.where(
                models.TaxTransaction.tax_type.in_(tax_types)
            )
            
        if jurisdiction_codes:
            base_query = base_query.where(
                models.TaxTransaction.jurisdiction_code.in_(jurisdiction_codes)
            )
        
        # Group by period, tax_type, and jurisdiction_code
        base_query = base_query.group_by(
            trunc_expr,
            models.TaxTransaction.tax_type,
            models.TaxTransaction.jurisdiction_code
        )
        
        # Get total count (optimized subquery)
        count_query = select(func.count()).select_from(base_query.subquery())
        total_count = self.db.execute(count_query).scalar() or 0
        
        # Apply pagination
        offset = (page - 1) * page_size
        paginated_query = base_query.offset(offset).limit(page_size)
        
        # Execute the query
        results = self.db.execute(paginated_query).all()
        
        # Format results
        formatted_results = []
        for row in results:
            formatted_results.append({
                'period': row.period.strftime(date_format) if row.period else None,
                'tax_type': row.tax_type,
                'jurisdiction_code': row.jurisdiction_code,
                'taxable_amount': row.taxable_amount or Decimal('0.00'),
                'tax_amount': row.tax_amount or Decimal('0.00'),
                'transaction_count': row.transaction_count or 0
            })
        
        return formatted_results, total_count
    
    def _get_date_trunc_expr(self, group_by: str):
        """Get the appropriate date truncation expression based on group_by."""
        if group_by == "day":
            return func.date_trunc('day', models.TaxTransaction.transaction_date)
        elif group_by == "week":
            # Adjust to start on Monday
            return func.date_trunc('week', models.TaxTransaction.transaction_date)
        elif group_by == "quarter":
            return func.date_trunc('quarter', models.TaxTransaction.transaction_date)
        elif group_by == "year":
            return func.date_trunc('year', models.TaxTransaction.transaction_date)
        else:  # month (default)
            return func.date_trunc('month', models.TaxTransaction.transaction_date)
    
    def _get_date_format(self, group_by: str) -> str:
        """Get the appropriate date format string based on group_by."""
        formats = {
            'day': '%Y-%m-%d',
            'week': '%Y-W%W',
            'month': '%Y-%m',
            'quarter': '%Y-Q%q',
            'year': '%Y'
        }
        return formats.get(group_by, '%Y-%m')  # Default to month format
