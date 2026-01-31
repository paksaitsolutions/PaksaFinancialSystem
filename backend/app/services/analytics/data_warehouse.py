"""
Data Warehouse Service

This service provides data warehouse functionality with ETL processes
for comprehensive business intelligence and analytics.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import asyncio

from dataclasses import dataclass
from enum import Enum
from sqlalchemy import select, func, and_, or_, text, create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from uuid import UUID, uuid4
import pandas as pd

from app.models.accounts_payable import Vendor, Invoice as APInvoice, Payment
from app.models.accounts_receivable import Customer, Invoice as ARInvoice, Receipt
from app.models.general_ledger import Transaction, Account, JournalEntry
from app.models.inventory import InventoryItem, InventoryTransaction
from app.models.payroll import Employee, Payroll, PayrollItem





class ETLStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ETLJob:
    """ETL job configuration and status."""
    id: str
    name: str
    source_table: str
    target_table: str
    status: ETLStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    records_processed: int = 0
    error_message: Optional[str] = None


class DataWarehouseService:
    """Service for data warehouse operations and ETL processes."""

    def __init__(self, db: AsyncSession, company_id: UUID):
        self.db = db
        self.company_id = company_id
        self.etl_jobs: Dict[str, ETLJob] = {}

    async def create_data_warehouse_schema(self) -> None:
        
        # Create dimension tables
        await self._create_dimension_tables()
        
        # Create fact tables
        await self._create_fact_tables()
        
        # Create aggregated tables
        await self._create_aggregated_tables()

    async def _create_dimension_tables(self) -> None:
        
        dimension_tables = [
            # Date dimension
            """
            CREATE TABLE IF NOT EXISTS dim_date (
                date_key INTEGER PRIMARY KEY,
                full_date DATE,
                year INTEGER,
                quarter INTEGER,
                month INTEGER,
                month_name VARCHAR(20),
                day INTEGER,
                day_of_week INTEGER,
                day_name VARCHAR(20),
                week_of_year INTEGER,
                is_weekend BOOLEAN,
                is_holiday BOOLEAN
            )
            """,
            
            # Account dimension
            """
            CREATE TABLE IF NOT EXISTS dim_account (
                account_key SERIAL PRIMARY KEY,
                account_id UUID,
                company_id UUID,
                account_code VARCHAR(20),
                account_name VARCHAR(255),
                account_type VARCHAR(50),
                account_subtype VARCHAR(50),
                parent_account_id UUID,
                is_active BOOLEAN,
                created_date DATE,
                updated_date DATE
            )
            """,
            
            # Customer dimension
            """
            CREATE TABLE IF NOT EXISTS dim_customer (
                customer_key SERIAL PRIMARY KEY,
                customer_id UUID,
                company_id UUID,
                customer_name VARCHAR(255),
                customer_type VARCHAR(50),
                industry VARCHAR(100),
                credit_limit DECIMAL(15,2),
                payment_terms INTEGER,
                status VARCHAR(20),
                created_date DATE,
                updated_date DATE
            )
            """,
            
            # Vendor dimension
            """
            CREATE TABLE IF NOT EXISTS dim_vendor (
                vendor_key SERIAL PRIMARY KEY,
                vendor_id UUID,
                company_id UUID,
                vendor_name VARCHAR(255),
                vendor_type VARCHAR(50),
                category VARCHAR(100),
                payment_terms INTEGER,
                status VARCHAR(20),
                created_date DATE,
                updated_date DATE
            )
            """,
            
            # Employee dimension
            """
            CREATE TABLE IF NOT EXISTS dim_employee (
                employee_key SERIAL PRIMARY KEY,
                employee_id UUID,
                company_id UUID,
                employee_name VARCHAR(255),
                department VARCHAR(100),
                position VARCHAR(100),
                employment_type VARCHAR(50),
                hire_date DATE,
                status VARCHAR(20),
                created_date DATE,
                updated_date DATE
            )
            """
        ]
        
        for table_sql in dimension_tables:
            await self.db.execute(text(table_sql))
        
        await self.db.commit()

    async def _create_fact_tables(self) -> None:
        
        fact_tables = [
            # Financial transactions fact
            """
            CREATE TABLE IF NOT EXISTS fact_financial_transaction (
                transaction_key SERIAL PRIMARY KEY,
                transaction_id UUID,
                company_id UUID,
                date_key INTEGER,
                account_key INTEGER,
                customer_key INTEGER,
                vendor_key INTEGER,
                transaction_type VARCHAR(20),
                amount DECIMAL(15,2),
                description TEXT,
                reference_number VARCHAR(100),
                created_date DATE,
                FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
                FOREIGN KEY (account_key) REFERENCES dim_account(account_key),
                FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
                FOREIGN KEY (vendor_key) REFERENCES dim_vendor(vendor_key)
            )
            """,
            
            # Sales fact
            """
            CREATE TABLE IF NOT EXISTS fact_sales (
                sales_key SERIAL PRIMARY KEY,
                invoice_id UUID,
                company_id UUID,
                date_key INTEGER,
                customer_key INTEGER,
                invoice_amount DECIMAL(15,2),
                paid_amount DECIMAL(15,2),
                outstanding_amount DECIMAL(15,2),
                days_to_payment INTEGER,
                payment_status VARCHAR(20),
                created_date DATE,
                FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
                FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key)
            )
            """,
            
            # Purchases fact
            """
            CREATE TABLE IF NOT EXISTS fact_purchases (
                purchase_key SERIAL PRIMARY KEY,
                invoice_id UUID,
                company_id UUID,
                date_key INTEGER,
                vendor_key INTEGER,
                invoice_amount DECIMAL(15,2),
                paid_amount DECIMAL(15,2),
                outstanding_amount DECIMAL(15,2),
                days_to_payment INTEGER,
                payment_status VARCHAR(20),
                created_date DATE,
                FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
                FOREIGN KEY (vendor_key) REFERENCES dim_vendor(vendor_key)
            )
            """,
            
            # Payroll fact
            """
            CREATE TABLE IF NOT EXISTS fact_payroll (
                payroll_key SERIAL PRIMARY KEY,
                payroll_id UUID,
                company_id UUID,
                date_key INTEGER,
                employee_key INTEGER,
                gross_pay DECIMAL(15,2),
                net_pay DECIMAL(15,2),
                total_deductions DECIMAL(15,2),
                total_taxes DECIMAL(15,2),
                overtime_hours DECIMAL(8,2),
                regular_hours DECIMAL(8,2),
                created_date DATE,
                FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
                FOREIGN KEY (employee_key) REFERENCES dim_employee(employee_key)
            )
            """
        ]
        
        for table_sql in fact_tables:
            await self.db.execute(text(table_sql))
        
        await self.db.commit()

    async def _create_aggregated_tables(self) -> None:
        
        aggregated_tables = [
            # Monthly financial summary
            """
            CREATE TABLE IF NOT EXISTS agg_monthly_financial (
                company_id UUID,
                year INTEGER,
                month INTEGER,
                total_revenue DECIMAL(15,2),
                total_expenses DECIMAL(15,2),
                net_profit DECIMAL(15,2),
                total_assets DECIMAL(15,2),
                total_liabilities DECIMAL(15,2),
                cash_flow DECIMAL(15,2),
                created_date DATE,
                updated_date DATE,
                PRIMARY KEY (company_id, year, month)
            )
            """,
            
            # Customer performance summary
            """
            CREATE TABLE IF NOT EXISTS agg_customer_performance (
                company_id UUID,
                customer_key INTEGER,
                year INTEGER,
                month INTEGER,
                total_sales DECIMAL(15,2),
                total_payments DECIMAL(15,2),
                outstanding_amount DECIMAL(15,2),
                invoice_count INTEGER,
                avg_days_to_payment DECIMAL(8,2),
                created_date DATE,
                updated_date DATE,
                PRIMARY KEY (company_id, customer_key, year, month),
                FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key)
            )
            """,
            
            # Vendor performance summary
            """
            CREATE TABLE IF NOT EXISTS agg_vendor_performance (
                company_id UUID,
                vendor_key INTEGER,
                year INTEGER,
                month INTEGER,
                total_purchases DECIMAL(15,2),
                total_payments DECIMAL(15,2),
                outstanding_amount DECIMAL(15,2),
                invoice_count INTEGER,
                avg_days_to_payment DECIMAL(8,2),
                created_date DATE,
                updated_date DATE,
                PRIMARY KEY (company_id, vendor_key, year, month),
                FOREIGN KEY (vendor_key) REFERENCES dim_vendor(vendor_key)
            )
            """
        ]
        
        for table_sql in aggregated_tables:
            await self.db.execute(text(table_sql))
        
        await self.db.commit()

    async def run_etl_process(self, full_refresh: bool = False) -> Dict[str, Any]:
        
        etl_start_time = datetime.now()
        results = {}
        
        try:
            # Step 1: Populate date dimension
            results['date_dimension'] = await self._populate_date_dimension()
            
            # Step 2: Populate dimension tables
            results['account_dimension'] = await self._populate_account_dimension(full_refresh)
            results['customer_dimension'] = await self._populate_customer_dimension(full_refresh)
            results['vendor_dimension'] = await self._populate_vendor_dimension(full_refresh)
            results['employee_dimension'] = await self._populate_employee_dimension(full_refresh)
            
            # Step 3: Populate fact tables
            results['financial_transactions'] = await self._populate_financial_transactions_fact(full_refresh)
            results['sales_fact'] = await self._populate_sales_fact(full_refresh)
            results['purchases_fact'] = await self._populate_purchases_fact(full_refresh)
            results['payroll_fact'] = await self._populate_payroll_fact(full_refresh)
            
            # Step 4: Update aggregated tables
            results['monthly_financial'] = await self._update_monthly_financial_aggregates()
            results['customer_performance'] = await self._update_customer_performance_aggregates()
            results['vendor_performance'] = await self._update_vendor_performance_aggregates()
            
            etl_end_time = datetime.now()
            execution_time = (etl_end_time - etl_start_time).total_seconds()
            
            return {
                'status': 'completed',
                'started_at': etl_start_time.isoformat(),
                'completed_at': etl_end_time.isoformat(),
                'execution_time_seconds': execution_time,
                'results': results
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'started_at': etl_start_time.isoformat(),
                'error': str(e),
                'results': results
            }

    async def _populate_date_dimension(self) -> Dict[str, Any]:
        
        # Generate dates for the next 5 years
        start_date = datetime(2020, 1, 1)
        end_date = datetime(2030, 12, 31)
        
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        date_records = []
        for date in date_range:
            date_key = int(date.strftime('%Y%m%d'))
            date_records.append({
                'date_key': date_key,
                'full_date': date.date(),
                'year': date.year,
                'quarter': (date.month - 1) // 3 + 1,
                'month': date.month,
                'month_name': date.strftime('%B'),
                'day': date.day,
                'day_of_week': date.weekday() + 1,
                'day_name': date.strftime('%A'),
                'week_of_year': date.isocalendar()[1],
                'is_weekend': date.weekday() >= 5,
                'is_holiday': False  # Would need holiday logic
            })
        
        # Insert in batches
        batch_size = 1000
        inserted_count = 0
        
        for i in range(0, len(date_records), batch_size):
            batch = date_records[i:i + batch_size]
            
            # Use INSERT ON CONFLICT DO NOTHING for PostgreSQL
            insert_sql = """
                INSERT INTO dim_date (date_key, full_date, year, quarter, month, month_name, 
                                    day, day_of_week, day_name, week_of_year, is_weekend, is_holiday)
                VALUES (:date_key, :full_date, :year, :quarter, :month, :month_name,
                       :day, :day_of_week, :day_name, :week_of_year, :is_weekend, :is_holiday)
                ON CONFLICT (date_key) DO NOTHING
            """
            
            await self.db.execute(text(insert_sql), batch)
            inserted_count += len(batch)
        
        await self.db.commit()
        
        return {
            'records_processed': inserted_count,
            'status': 'completed'
        }

    async def _populate_account_dimension(self, full_refresh: bool) -> Dict[str, Any]:
        
        if full_refresh:
            await self.db.execute(text("DELETE FROM dim_account WHERE company_id = :company_id"), 
                                {'company_id': str(self.company_id)})
        
        # Get accounts from source
        query = select(Account).where(Account.company_id == self.company_id)
        result = await self.db.execute(query)
        accounts = result.scalars().all()
        
        account_records = []
        for account in accounts:
            account_records.append({
                'account_id': str(account.id),
                'company_id': str(account.company_id),
                'account_code': account.account_code,
                'account_name': account.account_name,
                'account_type': account.account_type,
                'account_subtype': account.account_subtype,
                'parent_account_id': str(account.parent_account_id) if account.parent_account_id else None,
                'is_active': account.is_active,
                'created_date': account.created_at.date(),
                'updated_date': account.updated_at.date() if account.updated_at else account.created_at.date()
            })
        
        if account_records:
            insert_sql = """
                INSERT INTO dim_account (account_id, company_id, account_code, account_name, 
                                       account_type, account_subtype, parent_account_id, 
                                       is_active, created_date, updated_date)
                VALUES (:account_id, :company_id, :account_code, :account_name,
                       :account_type, :account_subtype, :parent_account_id,
                       :is_active, :created_date, :updated_date)
                ON CONFLICT (account_id) DO UPDATE SET
                    account_name = EXCLUDED.account_name,
                    account_type = EXCLUDED.account_type,
                    account_subtype = EXCLUDED.account_subtype,
                    is_active = EXCLUDED.is_active,
                    updated_date = EXCLUDED.updated_date
            """
            
            await self.db.execute(text(insert_sql), account_records)
            await self.db.commit()
        
        return {
            'records_processed': len(account_records),
            'status': 'completed'
        }

    async def _populate_financial_transactions_fact(self, full_refresh: bool) -> Dict[str, Any]:
        
        if full_refresh:
            await self.db.execute(text("DELETE FROM fact_financial_transaction WHERE company_id = :company_id"), 
                                {'company_id': str(self.company_id)})
        
        # Get transactions with related data
        query = text("""
            SELECT 
                t.id as transaction_id,
                t.company_id,
                t.transaction_date,
                t.transaction_type,
                t.amount,
                t.description,
                t.reference_number,
                t.created_at,
                a.account_key
            FROM transactions t
            JOIN dim_account a ON t.account_id::text = a.account_id
            WHERE t.company_id = :company_id
        """)
        
        result = await self.db.execute(query, {'company_id': str(self.company_id)})
        transactions = result.fetchall()
        
        transaction_records = []
        for txn in transactions:
            date_key = int(txn.transaction_date.strftime('%Y%m%d'))
            
            transaction_records.append({
                'transaction_id': str(txn.transaction_id),
                'company_id': str(txn.company_id),
                'date_key': date_key,
                'account_key': txn.account_key,
                'customer_key': None,  # Would need to join with customer data
                'vendor_key': None,    # Would need to join with vendor data
                'transaction_type': txn.transaction_type,
                'amount': float(txn.amount),
                'description': txn.description,
                'reference_number': txn.reference_number,
                'created_date': txn.created_at.date()
            })
        
        if transaction_records:
            insert_sql = """
                INSERT INTO fact_financial_transaction (transaction_id, company_id, date_key, 
                                                      account_key, customer_key, vendor_key,
                                                      transaction_type, amount, description,
                                                      reference_number, created_date)
                VALUES (:transaction_id, :company_id, :date_key, :account_key, :customer_key,
                       :vendor_key, :transaction_type, :amount, :description,
                       :reference_number, :created_date)
                ON CONFLICT (transaction_id) DO NOTHING
            """
            
            await self.db.execute(text(insert_sql), transaction_records)
            await self.db.commit()
        
        return {
            'records_processed': len(transaction_records),
            'status': 'completed'
        }

    async def _update_monthly_financial_aggregates(self) -> Dict[str, Any]:
        
        # Calculate monthly aggregates
        aggregate_sql = text("""
            INSERT INTO agg_monthly_financial (company_id, year, month, total_revenue, 
                                             total_expenses, net_profit, created_date, updated_date)
            SELECT 
                company_id,
                EXTRACT(YEAR FROM d.full_date) as year,
                EXTRACT(MONTH FROM d.full_date) as month,
                COALESCE(SUM(CASE WHEN a.account_type = 'revenue' THEN ft.amount ELSE 0 END), 0) as total_revenue,
                COALESCE(SUM(CASE WHEN a.account_type = 'expense' THEN ft.amount ELSE 0 END), 0) as total_expenses,
                COALESCE(SUM(CASE WHEN a.account_type = 'revenue' THEN ft.amount ELSE 0 END), 0) - 
                COALESCE(SUM(CASE WHEN a.account_type = 'expense' THEN ft.amount ELSE 0 END), 0) as net_profit,
                CURRENT_DATE as created_date,
                CURRENT_DATE as updated_date
            FROM fact_financial_transaction ft
            JOIN dim_date d ON ft.date_key = d.date_key
            JOIN dim_account a ON ft.account_key = a.account_key
            WHERE ft.company_id = :company_id
            GROUP BY company_id, EXTRACT(YEAR FROM d.full_date), EXTRACT(MONTH FROM d.full_date)
            ON CONFLICT (company_id, year, month) DO UPDATE SET
                total_revenue = EXCLUDED.total_revenue,
                total_expenses = EXCLUDED.total_expenses,
                net_profit = EXCLUDED.net_profit,
                updated_date = EXCLUDED.updated_date
        """)
        
        await self.db.execute(aggregate_sql, {'company_id': str(self.company_id)})
        await self.db.commit()
        
        return {
            'status': 'completed'
        }

    async def get_warehouse_statistics(self) -> Dict[str, Any]:
        
        stats_queries = {
            'dim_date': "SELECT COUNT(*) FROM dim_date",
            'dim_account': f"SELECT COUNT(*) FROM dim_account WHERE company_id = '{self.company_id}'",
            'dim_customer': f"SELECT COUNT(*) FROM dim_customer WHERE company_id = '{self.company_id}'",
            'dim_vendor': f"SELECT COUNT(*) FROM dim_vendor WHERE company_id = '{self.company_id}'",
            'fact_financial_transaction': f"SELECT COUNT(*) FROM fact_financial_transaction WHERE company_id = '{self.company_id}'",
            'agg_monthly_financial': f"SELECT COUNT(*) FROM agg_monthly_financial WHERE company_id = '{self.company_id}'"
        }
        
        statistics = {}
        for table_name, query in stats_queries.items():
            try:
                result = await self.db.execute(text(query))
                count = result.scalar()
                statistics[table_name] = count
            except Exception as e:
                statistics[table_name] = f"Error: {str(e)}"
        
        return {
            'company_id': str(self.company_id),
            'table_counts': statistics,
            'last_updated': datetime.now().isoformat()
        }