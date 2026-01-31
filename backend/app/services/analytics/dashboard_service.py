"""
Dashboard Service

This service provides functional dashboard capabilities, replacing UI-only dashboards
with real data-driven functionality.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import asyncio

from .data_aggregation_service import DataAggregationService
from .reporting_engine import ReportingEngine
from enum import Enum
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4

from app.ai.services.anomaly_detection import AnomalyDetectionService
from app.ai.services.predictive_analytics import PredictiveAnalyticsService





class WidgetType(str, Enum):
    KPI_CARD = "kpi_card"
    CHART = "chart"
    TABLE = "table"
    GAUGE = "gauge"
    TREND = "trend"
    ALERT = "alert"


class ChartType(str, Enum):
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    AREA = "area"
    DONUT = "donut"


class DashboardService:
    """Service for creating and managing functional dashboards."""

    def __init__(self, db: AsyncSession, company_id: UUID):
        self.db = db
        self.company_id = company_id
        self.data_service = DataAggregationService(db, company_id)
        self.reporting_service = ReportingEngine(db, company_id)
        self.predictive_service = PredictiveAnalyticsService()
        self.anomaly_service = AnomalyDetectionService()

    async def get_executive_dashboard(self) -> Dict[str, Any]:
        
        # Run multiple data fetches concurrently
        tasks = [
            self.data_service.get_kpi_dashboard(),
            self._get_financial_alerts(),
            self._get_performance_metrics(),
            self._get_predictive_insights()
        ]
        
        kpi_data, alerts, performance, predictions = await asyncio.gather(*tasks)

        widgets = [
            # Revenue KPI Card
            {
                'id': 'revenue_kpi',
                'type': WidgetType.KPI_CARD,
                'title': 'Total Revenue',
                'value': kpi_data['financial_summary']['revenue'],
                'change': kpi_data['growth_metrics']['revenue_growth'],
                'format': 'currency',
                'trend': 'up' if kpi_data['growth_metrics']['revenue_growth'] > 0 else 'down'
            },
            
            # Profit KPI Card
            {
                'id': 'profit_kpi',
                'type': WidgetType.KPI_CARD,
                'title': 'Net Profit',
                'value': kpi_data['financial_summary']['profit'],
                'change': kpi_data['growth_metrics']['profit_growth'],
                'format': 'currency',
                'trend': 'up' if kpi_data['growth_metrics']['profit_growth'] > 0 else 'down'
            },
            
            # Cash Flow KPI Card
            {
                'id': 'cashflow_kpi',
                'type': WidgetType.KPI_CARD,
                'title': 'Cash Flow',
                'value': kpi_data['financial_summary']['cash_flow']['net_cash_flow'],
                'format': 'currency',
                'trend': 'up' if kpi_data['financial_summary']['cash_flow']['net_cash_flow'] > 0 else 'down'
            },
            
            # Revenue Trend Chart
            {
                'id': 'revenue_trend',
                'type': WidgetType.CHART,
                'chart_type': ChartType.LINE,
                'title': 'Revenue Trend (6 Months)',
                'data': kpi_data['trends']['revenue'],
                'x_axis': 'period',
                'y_axis': 'value'
            },
            
            # Profit Trend Chart
            {
                'id': 'profit_trend',
                'type': WidgetType.CHART,
                'chart_type': ChartType.AREA,
                'title': 'Profit Trend (6 Months)',
                'data': kpi_data['trends']['profit'],
                'x_axis': 'period',
                'y_axis': 'value'
            },
            
            # Alerts Widget
            {
                'id': 'financial_alerts',
                'type': WidgetType.ALERT,
                'title': 'Financial Alerts',
                'alerts': alerts
            },
            
            # Performance Metrics Table
            {
                'id': 'performance_metrics',
                'type': WidgetType.TABLE,
                'title': 'Key Performance Metrics',
                'data': performance,
                'columns': ['metric', 'current_value', 'target', 'variance']
            }
        ]

        return {
            'dashboard_id': 'executive_dashboard',
            'title': 'Executive Dashboard',
            'widgets': widgets,
            'last_updated': datetime.now().isoformat(),
            'refresh_interval': 300  # 5 minutes
        }

    async def get_financial_dashboard(self) -> Dict[str, Any]:
        
        # Get comprehensive financial data
        financial_summary = await self.data_service.get_financial_summary()
        ar_aging = await self.reporting_service.generate_report(
            'aging_report', 
            {'type': 'ar', 'as_of_date': datetime.now().isoformat()}
        )
        ap_aging = await self.reporting_service.generate_report(
            'aging_report', 
            {'type': 'ap', 'as_of_date': datetime.now().isoformat()}
        )

        widgets = [
            # P&L Summary
            {
                'id': 'pl_summary',
                'type': WidgetType.CHART,
                'chart_type': ChartType.BAR,
                'title': 'Profit & Loss Summary',
                'data': [
                    {'category': 'Revenue', 'amount': financial_summary['revenue']},
                    {'category': 'Expenses', 'amount': financial_summary['expenses']},
                    {'category': 'Profit', 'amount': financial_summary['profit']}
                ],
                'x_axis': 'category',
                'y_axis': 'amount'
            },
            
            # AR Aging Donut Chart
            {
                'id': 'ar_aging_chart',
                'type': WidgetType.CHART,
                'chart_type': ChartType.DONUT,
                'title': 'Accounts Receivable Aging',
                'data': [
                    {'label': 'Current', 'value': ar_aging['data']['totals']['current']},
                    {'label': '1-30 Days', 'value': ar_aging['data']['totals']['1_30_days']},
                    {'label': '31-60 Days', 'value': ar_aging['data']['totals']['31_60_days']},
                    {'label': '61-90 Days', 'value': ar_aging['data']['totals']['61_90_days']},
                    {'label': 'Over 90 Days', 'value': ar_aging['data']['totals']['over_90_days']}
                ]
            },
            
            # Cash Flow Gauge
            {
                'id': 'cash_flow_gauge',
                'type': WidgetType.GAUGE,
                'title': 'Cash Flow Health',
                'value': financial_summary['cash_flow']['net_cash_flow'],
                'min_value': -100000,
                'max_value': 100000,
                'thresholds': [
                    {'value': -50000, 'color': 'red', 'label': 'Critical'},
                    {'value': 0, 'color': 'yellow', 'label': 'Warning'},
                    {'value': 50000, 'color': 'green', 'label': 'Healthy'}
                ]
            }
        ]

        return {
            'dashboard_id': 'financial_dashboard',
            'title': 'Financial Dashboard',
            'widgets': widgets,
            'last_updated': datetime.now().isoformat(),
            'refresh_interval': 600  # 10 minutes
        }

    async def get_operational_dashboard(self) -> Dict[str, Any]:
        
        kpi_data = await self.data_service.get_kpi_dashboard()
        
        widgets = [
            # Active Customers
            {
                'id': 'active_customers',
                'type': WidgetType.KPI_CARD,
                'title': 'Active Customers',
                'value': kpi_data['operational_metrics']['active_customers'],
                'format': 'number'
            },
            
            # Active Vendors
            {
                'id': 'active_vendors',
                'type': WidgetType.KPI_CARD,
                'title': 'Active Vendors',
                'value': kpi_data['operational_metrics']['active_vendors'],
                'format': 'number'
            },
            
            # Inventory Value
            {
                'id': 'inventory_value',
                'type': WidgetType.KPI_CARD,
                'title': 'Inventory Value',
                'value': kpi_data['operational_metrics']['inventory_value'],
                'format': 'currency'
            }
        ]

        return {
            'dashboard_id': 'operational_dashboard',
            'title': 'Operational Dashboard',
            'widgets': widgets,
            'last_updated': datetime.now().isoformat(),
            'refresh_interval': 900  # 15 minutes
        }

    async def get_custom_dashboard(self, dashboard_config: Dict[str, Any]) -> Dict[str, Any]:
        
        widgets = []
        
        for widget_config in dashboard_config.get('widgets', []):
            widget = await self._create_widget(widget_config)
            widgets.append(widget)

        return {
            'dashboard_id': dashboard_config.get('id', str(uuid4())),
            'title': dashboard_config.get('title', 'Custom Dashboard'),
            'widgets': widgets,
            'last_updated': datetime.now().isoformat(),
            'refresh_interval': dashboard_config.get('refresh_interval', 300)
        }

    async def _create_widget(self, config: Dict[str, Any]) -> Dict[str, Any]:
        
        widget_type = config.get('type')
        
        if widget_type == WidgetType.KPI_CARD:
            return await self._create_kpi_widget(config)
        elif widget_type == WidgetType.CHART:
            return await self._create_chart_widget(config)
        elif widget_type == WidgetType.TABLE:
            return await self._create_table_widget(config)
        elif widget_type == WidgetType.GAUGE:
            return await self._create_gauge_widget(config)
        else:
            raise ValueError(f"Unsupported widget type: {widget_type}")

    async def _create_kpi_widget(self, config: Dict[str, Any]) -> Dict[str, Any]:
        
        # Get data based on metric
        metric = config.get('metric')
        if metric == 'revenue':
            summary = await self.data_service.get_financial_summary()
            value = summary['revenue']
        elif metric == 'profit':
            summary = await self.data_service.get_financial_summary()
            value = summary['profit']
        else:
            value = 0

        return {
            'id': config.get('id', str(uuid4())),
            'type': WidgetType.KPI_CARD,
            'title': config.get('title', 'KPI'),
            'value': value,
            'format': config.get('format', 'number')
        }

    async def _create_chart_widget(self, config: Dict[str, Any]) -> Dict[str, Any]:
        
        # Get data based on data source
        data_source = config.get('data_source')
        if data_source == 'revenue_trend':
            data = await self.data_service.get_trend_analysis('revenue')
        elif data_source == 'expense_trend':
            data = await self.data_service.get_trend_analysis('expenses')
        else:
            data = []

        return {
            'id': config.get('id', str(uuid4())),
            'type': WidgetType.CHART,
            'chart_type': config.get('chart_type', ChartType.LINE),
            'title': config.get('title', 'Chart'),
            'data': data,
            'x_axis': config.get('x_axis', 'period'),
            'y_axis': config.get('y_axis', 'value')
        }

    async def _get_financial_alerts(self) -> List[Dict[str, Any]]:
        alerts = []
        
        # Get current financial data
        summary = await self.data_service.get_financial_summary()
        
        # Cash flow alert
        if summary['cash_flow']['net_cash_flow'] < 0:
            alerts.append({
                'type': 'warning',
                'title': 'Negative Cash Flow',
                'message': f"Net cash flow is ${summary['cash_flow']['net_cash_flow']:,.2f}",
                'severity': 'high'
            })
        
        # Low profit margin alert
        if summary['profit_margin'] < 10:
            alerts.append({
                'type': 'warning',
                'title': 'Low Profit Margin',
                'message': f"Profit margin is {summary['profit_margin']:.1f}%",
                'severity': 'medium'
            })
        
        # High AR alert
        if summary['accounts_receivable']['overdue_amount'] > 10000:
            alerts.append({
                'type': 'alert',
                'title': 'High Overdue Receivables',
                'message': f"${summary['accounts_receivable']['overdue_amount']:,.2f} in overdue receivables",
                'severity': 'high'
            })

        return alerts

    async def _get_performance_metrics(self) -> List[Dict[str, Any]]:
        summary = await self.data_service.get_financial_summary()
        
        return [
            {
                'metric': 'Profit Margin',
                'current_value': f"{summary['profit_margin']:.1f}%",
                'target': '15.0%',
                'variance': f"{summary['profit_margin'] - 15:.1f}%"
            },
            {
                'metric': 'Cash Flow',
                'current_value': f"${summary['cash_flow']['net_cash_flow']:,.2f}",
                'target': '$50,000',
                'variance': f"${summary['cash_flow']['net_cash_flow'] - 50000:,.2f}"
            }
        ]

    async def _get_predictive_insights(self) -> Dict[str, Any]:
        # This would integrate with the AI services
        return {
            'cash_flow_prediction': 'Positive trend expected',
            'revenue_forecast': 'Growth projected for next quarter',
            'risk_assessment': 'Low financial risk'
        }