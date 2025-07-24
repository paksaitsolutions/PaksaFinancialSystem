"""
Analytics API Endpoints

This module provides REST API endpoints for analytics, reporting, and BI features.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.services.analytics.data_aggregation_service import DataAggregationService
from app.services.analytics.reporting_engine import ReportingEngine, ReportType, ReportFormat
from app.services.analytics.dashboard_service import DashboardService
from app.services.analytics.query_optimizer import QueryOptimizer
from app.services.analytics.scheduled_reports import ScheduledReportsService, ScheduleFrequency
from app.services.analytics.data_warehouse import DataWarehouseService


router = APIRouter()


# Request/Response Models
class DateRangeRequest(BaseModel):
    start_date: datetime
    end_date: datetime


class ReportRequest(BaseModel):
    report_type: ReportType
    parameters: Dict[str, Any]
    format: ReportFormat = ReportFormat.JSON


class ScheduledReportRequest(BaseModel):
    report_type: ReportType
    report_name: str
    parameters: Dict[str, Any]
    format: ReportFormat
    frequency: ScheduleFrequency
    recipients: List[str]
    cron_expression: Optional[str] = None


class DashboardConfigRequest(BaseModel):
    dashboard_type: str
    widgets: List[Dict[str, Any]] = []


# Data Aggregation Endpoints
@router.get("/financial-summary")
async def get_financial_summary(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive financial summary."""
    
    service = DataAggregationService(db, current_user.company_id)
    
    date_range = None
    if start_date and end_date:
        date_range = {'start': start_date, 'end': end_date}
    
    summary = await service.get_financial_summary(date_range)
    
    return {
        'status': 'success',
        'data': summary
    }


@router.get("/trend-analysis/{metric}")
async def get_trend_analysis(
    metric: str,
    period: str = Query("monthly", regex="^(daily|weekly|monthly)$"),
    months: int = Query(12, ge=1, le=60),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get trend analysis for specific metrics."""
    
    service = DataAggregationService(db, current_user.company_id)
    
    try:
        trend_data = await service.get_trend_analysis(metric, period, months)
        return {
            'status': 'success',
            'data': trend_data
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/kpi-dashboard")
async def get_kpi_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive KPI dashboard data."""
    
    service = DataAggregationService(db, current_user.company_id)
    kpi_data = await service.get_kpi_dashboard()
    
    return {
        'status': 'success',
        'data': kpi_data
    }


# Reporting Endpoints
@router.post("/reports/generate")
async def generate_report(
    request: ReportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a report based on type and parameters."""
    
    service = ReportingEngine(db, current_user.company_id)
    
    report = await service.generate_report(
        request.report_type,
        request.parameters,
        request.format
    )
    
    return {
        'status': 'success',
        'data': report
    }


@router.get("/reports/types")
async def get_report_types():
    """Get available report types."""
    
    return {
        'status': 'success',
        'data': [
            {
                'type': ReportType.INCOME_STATEMENT,
                'name': 'Income Statement',
                'description': 'Profit and loss statement'
            },
            {
                'type': ReportType.BALANCE_SHEET,
                'name': 'Balance Sheet',
                'description': 'Assets, liabilities, and equity'
            },
            {
                'type': ReportType.CASH_FLOW,
                'name': 'Cash Flow Statement',
                'description': 'Cash inflows and outflows'
            },
            {
                'type': ReportType.TRIAL_BALANCE,
                'name': 'Trial Balance',
                'description': 'Account balances verification'
            },
            {
                'type': ReportType.AGING_REPORT,
                'name': 'Aging Report',
                'description': 'Accounts receivable/payable aging'
            },
            {
                'type': ReportType.CUSTOM,
                'name': 'Custom Report',
                'description': 'Custom SQL-based report'
            }
        ]
    }


# Dashboard Endpoints
@router.get("/dashboards/executive")
async def get_executive_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get executive dashboard with high-level KPIs."""
    
    service = DashboardService(db, current_user.company_id)
    dashboard = await service.get_executive_dashboard()
    
    return {
        'status': 'success',
        'data': dashboard
    }


@router.get("/dashboards/financial")
async def get_financial_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed financial dashboard."""
    
    service = DashboardService(db, current_user.company_id)
    dashboard = await service.get_financial_dashboard()
    
    return {
        'status': 'success',
        'data': dashboard
    }


@router.get("/dashboards/operational")
async def get_operational_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get operational metrics dashboard."""
    
    service = DashboardService(db, current_user.company_id)
    dashboard = await service.get_operational_dashboard()
    
    return {
        'status': 'success',
        'data': dashboard
    }


@router.post("/dashboards/custom")
async def create_custom_dashboard(
    request: DashboardConfigRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create custom dashboard based on configuration."""
    
    service = DashboardService(db, current_user.company_id)
    
    dashboard_config = {
        'id': f"custom_{request.dashboard_type}",
        'title': f"Custom {request.dashboard_type.title()} Dashboard",
        'widgets': request.widgets
    }
    
    dashboard = await service.get_custom_dashboard(dashboard_config)
    
    return {
        'status': 'success',
        'data': dashboard
    }


# Scheduled Reports Endpoints
@router.post("/scheduled-reports")
async def create_scheduled_report(
    request: ScheduledReportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new scheduled report."""
    
    service = ScheduledReportsService(db)
    
    scheduled_report = await service.create_scheduled_report(
        company_id=current_user.company_id,
        report_type=request.report_type,
        report_name=request.report_name,
        parameters=request.parameters,
        format=request.format,
        frequency=request.frequency,
        recipients=request.recipients,
        created_by=current_user.id,
        cron_expression=request.cron_expression
    )
    
    return {
        'status': 'success',
        'data': {
            'id': scheduled_report.id,
            'report_name': scheduled_report.report_name,
            'frequency': scheduled_report.frequency,
            'next_run': scheduled_report.next_run.isoformat() if scheduled_report.next_run else None
        }
    }


@router.get("/scheduled-reports")
async def list_scheduled_reports(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List scheduled reports for the current company."""
    
    service = ScheduledReportsService(db)
    reports = await service.list_scheduled_reports(company_id=current_user.company_id)
    
    return {
        'status': 'success',
        'data': [
            {
                'id': report.id,
                'report_name': report.report_name,
                'report_type': report.report_type,
                'frequency': report.frequency,
                'is_active': report.is_active,
                'last_run': report.last_run.isoformat() if report.last_run else None,
                'next_run': report.next_run.isoformat() if report.next_run else None,
                'recipients': report.recipients
            }
            for report in reports
        ]
    }


@router.post("/scheduled-reports/{report_id}/execute")
async def execute_scheduled_report(
    report_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Execute a scheduled report immediately."""
    
    service = ScheduledReportsService(db)
    
    # Add to background tasks
    background_tasks.add_task(service.execute_scheduled_report, report_id)
    
    return {
        'status': 'success',
        'message': 'Report execution started'
    }


@router.get("/scheduled-reports/{report_id}/history")
async def get_execution_history(
    report_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get execution history for a scheduled report."""
    
    service = ScheduledReportsService(db)
    history = await service.get_execution_history(report_id, limit)
    
    return {
        'status': 'success',
        'data': [
            {
                'id': execution.id,
                'status': execution.status,
                'started_at': execution.started_at.isoformat(),
                'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
                'error_message': execution.error_message
            }
            for execution in history
        ]
    }


# Query Optimization Endpoints
@router.get("/performance/query-metrics")
async def get_query_performance_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get query performance metrics."""
    
    optimizer = QueryOptimizer(db, current_user.company_id)
    metrics = await optimizer.analyze_query_performance()
    
    return {
        'status': 'success',
        'data': metrics
    }


@router.post("/performance/warm-cache")
async def warm_cache(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Warm up the query cache with commonly used queries."""
    
    optimizer = QueryOptimizer(db, current_user.company_id)
    background_tasks.add_task(optimizer.warm_cache)
    
    return {
        'status': 'success',
        'message': 'Cache warming started'
    }


@router.post("/performance/invalidate-cache")
async def invalidate_cache(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Invalidate cached queries for the current company."""
    
    optimizer = QueryOptimizer(db, current_user.company_id)
    await optimizer.invalidate_cache_for_company()
    
    return {
        'status': 'success',
        'message': 'Cache invalidated'
    }


# Data Warehouse Endpoints
@router.post("/data-warehouse/etl")
async def run_etl_process(
    full_refresh: bool = Query(False),
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Run the ETL process to update the data warehouse."""
    
    service = DataWarehouseService(db, current_user.company_id)
    
    # Run ETL in background
    background_tasks.add_task(service.run_etl_process, full_refresh)
    
    return {
        'status': 'success',
        'message': 'ETL process started'
    }


@router.get("/data-warehouse/statistics")
async def get_warehouse_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get data warehouse statistics."""
    
    service = DataWarehouseService(db, current_user.company_id)
    stats = await service.get_warehouse_statistics()
    
    return {
        'status': 'success',
        'data': stats
    }


@router.post("/data-warehouse/initialize")
async def initialize_data_warehouse(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Initialize the data warehouse schema."""
    
    service = DataWarehouseService(db, current_user.company_id)
    background_tasks.add_task(service.create_data_warehouse_schema)
    
    return {
        'status': 'success',
        'message': 'Data warehouse initialization started'
    }