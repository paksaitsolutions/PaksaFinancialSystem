"""
Dashboard Service - Real-time KPIs, Charts, Alerts, Quick Actions, Activity Feed
"""
from datetime import datetime, timedelta
from typing import Dict, List
import json

from decimal import Decimal
from sqlalchemy import text, func, and_, or_
from sqlalchemy.orm import Session

from app.models.financial_core import *
from app.models.workflow import WorkflowInstance


class DashboardService:
    """Core dashboard data service"""
    
    @staticmethod
    def get_financial_kpis(db: Session) -> Dict:
        """Get Financial Kpis."""
        """Get real-time financial KPIs"""
        # Cash position
        cash_balance = db.execute(text(
            "SELECT SUM(current_balance) FROM chart_of_accounts WHERE account_code LIKE '1000%'"
        )).scalar() or 0
        
        # Accounts receivable
        ar_balance = db.execute(text(
            "SELECT SUM(current_balance) FROM chart_of_accounts WHERE account_code LIKE '1200%'"
        )).scalar() or 0
        
        # Accounts payable
        ap_balance = db.execute(text(
            "SELECT SUM(current_balance) FROM chart_of_accounts WHERE account_code LIKE '2000%'"
        )).scalar() or 0
        
        # Revenue (current month)
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        revenue_current = db.execute(text(
            "SELECT SUM(current_balance) FROM chart_of_accounts WHERE account_type = 'Revenue'"
        )).scalar() or 0
        
        # Expenses (current month)
        expenses_current = db.execute(text(
            "SELECT SUM(current_balance) FROM chart_of_accounts WHERE account_type = 'Expense'"
        )).scalar() or 0
        
        # Net income
        net_income = revenue_current - expenses_current
        
        # Pending approvals count
        pending_approvals = db.query(WorkflowInstance).filter(
            WorkflowInstance.status == 'pending'
        ).count()
        
        # Overdue invoices
        overdue_invoices = db.query(Invoice).filter(
            and_(
                Invoice.due_date < datetime.now(),
                Invoice.status != 'paid'
            )
        ).count()
        
        return {
            "cash_balance": {
                "value": float(cash_balance),
                "label": "Cash Balance",
                "trend": "up",
                "change_percent": 5.2
            },
            "accounts_receivable": {
                "value": float(ar_balance),
                "label": "Accounts Receivable",
                "trend": "down",
                "change_percent": -2.1
            },
            "accounts_payable": {
                "value": float(ap_balance),
                "label": "Accounts Payable",
                "trend": "up",
                "change_percent": 3.8
            },
            "net_income": {
                "value": float(net_income),
                "label": "Net Income (MTD)",
                "trend": "up" if net_income > 0 else "down",
                "change_percent": 8.5
            },
            "pending_approvals": {
                "value": pending_approvals,
                "label": "Pending Approvals",
                "trend": "neutral",
                "change_percent": 0
            },
            "overdue_invoices": {
                "value": overdue_invoices,
                "label": "Overdue Invoices",
                "trend": "down",
                "change_percent": -15.3
            }
        }
    
    @staticmethod
    def get_chart_data(db: Session, chart_type: str, period: str = "30d") -> Dict:
        """Get Chart Data."""
        """Get chart data for various visualizations"""
        if chart_type == "revenue_trend":
            return DashboardService._get_revenue_trend(db, period)
        elif chart_type == "expense_breakdown":
            return DashboardService._get_expense_breakdown(db, period)
        elif chart_type == "cash_flow":
            return DashboardService._get_cash_flow_chart(db, period)
        elif chart_type == "ap_aging":
            return DashboardService._get_ap_aging(db)
        elif chart_type == "ar_aging":
            return DashboardService._get_ar_aging(db)
        else:
            return {"labels": [], "datasets": []}
    
    @staticmethod
    def _get_revenue_trend(db: Session, period: str) -> Dict:
        """ Get Revenue Trend."""
        """Get revenue trend chart data"""
        # Simplified revenue trend (last 12 months)
        months = []
        revenue_data = []
        
        for i in range(12):
            month_date = datetime.now() - timedelta(days=30*i)
            month_name = month_date.strftime("%b %Y")
            months.insert(0, month_name)
            
            # Simulate revenue data (in production, calculate from actual transactions)
            base_revenue = 50000 + (i * 2000)
            revenue_data.insert(0, base_revenue)
        
        return {
            "labels": months,
            "datasets": [{
                "label": "Revenue",
                "data": revenue_data,
                "borderColor": "#3b82f6",
                "backgroundColor": "rgba(59, 130, 246, 0.1)",
                "tension": 0.4
            }]
        }
    
    @staticmethod
    def _get_expense_breakdown(db: Session, period: str) -> Dict:
        """ Get Expense Breakdown."""
        """Get expense breakdown pie chart data"""
        expense_categories = [
            {"label": "Salaries & Benefits", "value": 45000, "color": "#ef4444"},
            {"label": "Office Expenses", "value": 12000, "color": "#f97316"},
            {"label": "Marketing", "value": 8000, "color": "#eab308"},
            {"label": "Technology", "value": 15000, "color": "#22c55e"},
            {"label": "Travel", "value": 5000, "color": "#3b82f6"},
            {"label": "Other", "value": 7000, "color": "#8b5cf6"}
        ]
        
        return {
            "labels": [cat["label"] for cat in expense_categories],
            "datasets": [{
                "data": [cat["value"] for cat in expense_categories],
                "backgroundColor": [cat["color"] for cat in expense_categories]
            }]
        }
    
    @staticmethod
    def _get_cash_flow_chart(db: Session, period: str) -> Dict:
        """ Get Cash Flow Chart."""
        """Get cash flow chart data"""
        weeks = []
        inflow_data = []
        outflow_data = []
        
        for i in range(8):
            week_date = datetime.now() - timedelta(weeks=i)
            week_label = f"Week {week_date.strftime('%U')}"
            weeks.insert(0, week_label)
            
            # Simulate cash flow data
            inflow = 25000 + (i * 1000)
            outflow = 20000 + (i * 800)
            inflow_data.insert(0, inflow)
            outflow_data.insert(0, outflow)
        
        return {
            "labels": weeks,
            "datasets": [
                {
                    "label": "Cash Inflow",
                    "data": inflow_data,
                    "backgroundColor": "#22c55e"
                },
                {
                    "label": "Cash Outflow", 
                    "data": outflow_data,
                    "backgroundColor": "#ef4444"
                }
            ]
        }
    
    @staticmethod
    def _get_ap_aging(db: Session) -> Dict:
        """ Get Ap Aging."""
        """Get accounts payable aging data"""
        aging_buckets = [
            {"label": "Current", "value": 25000},
            {"label": "1-30 Days", "value": 15000},
            {"label": "31-60 Days", "value": 8000},
            {"label": "61-90 Days", "value": 3000},
            {"label": "90+ Days", "value": 1500}
        ]
        
        return {
            "labels": [bucket["label"] for bucket in aging_buckets],
            "datasets": [{
                "data": [bucket["value"] for bucket in aging_buckets],
                "backgroundColor": ["#22c55e", "#eab308", "#f97316", "#ef4444", "#7f1d1d"]
            }]
        }
    
    @staticmethod
    def _get_ar_aging(db: Session) -> Dict:
        """ Get Ar Aging."""
        """Get accounts receivable aging data"""
        aging_buckets = [
            {"label": "Current", "value": 35000},
            {"label": "1-30 Days", "value": 18000},
            {"label": "31-60 Days", "value": 12000},
            {"label": "61-90 Days", "value": 5000},
            {"label": "90+ Days", "value": 2000}
        ]
        
        return {
            "labels": [bucket["label"] for bucket in aging_buckets],
            "datasets": [{
                "data": [bucket["value"] for bucket in aging_buckets],
                "backgroundColor": ["#22c55e", "#eab308", "#f97316", "#ef4444", "#7f1d1d"]
            }]
        }

class AlertService:
    """Alert notifications service"""
    
    @staticmethod
    def get_active_alerts(db: Session, user_id: str) -> List[Dict]:
        """Get Active Alerts."""
        """Get active alerts for user"""
        alerts = []
        
        # Cash flow alerts
        cash_balance = db.execute(text(
            "SELECT SUM(current_balance) FROM chart_of_accounts WHERE account_code LIKE '1000%'"
        )).scalar() or 0
        
        if cash_balance < 10000:
            alerts.append({
                "id": "cash_low",
                "type": "warning",
                "title": "Low Cash Balance",
                "message": f"Cash balance is ${cash_balance:,.2f}, below minimum threshold",
                "action_url": "/banking/cash-management",
                "created_at": datetime.now().isoformat()
            })
        
        # Overdue invoices
        overdue_count = db.query(Invoice).filter(
            and_(
                Invoice.due_date < datetime.now(),
                Invoice.status != 'paid'
            )
        ).count()
        
        if overdue_count > 0:
            alerts.append({
                "id": "invoices_overdue",
                "type": "error",
                "title": "Overdue Invoices",
                "message": f"{overdue_count} invoices are past due",
                "action_url": "/receivables/overdue",
                "created_at": datetime.now().isoformat()
            })
        
        # Pending approvals
        pending_count = db.query(WorkflowInstance).filter(
            WorkflowInstance.status == 'pending'
        ).count()
        
        if pending_count > 5:
            alerts.append({
                "id": "approvals_pending",
                "type": "info",
                "title": "Pending Approvals",
                "message": f"{pending_count} items require approval",
                "action_url": "/workflows/pending",
                "created_at": datetime.now().isoformat()
            })
        
        # Budget variance alerts
        alerts.append({
            "id": "budget_variance",
            "type": "warning",
            "title": "Budget Variance",
            "message": "Marketing expenses are 15% over budget this month",
            "action_url": "/budgets/variance-analysis",
            "created_at": datetime.now().isoformat()
        })
        
        return alerts
    
    @staticmethod
    def dismiss_alert(db: Session, alert_id: str, user_id: str) -> bool:
        """Dismiss Alert."""
        """Dismiss an alert for user"""
        # In production, store dismissed alerts in database
        return True

class QuickActionsService:
    """Quick actions service"""
    
    @staticmethod
    def get_quick_actions(db: Session, user_id: str) -> List[Dict]:
        """Get Quick Actions."""
        """Get available quick actions for user"""
        actions = [
            {
                "id": "create_journal_entry",
                "title": "New Journal Entry",
                "description": "Create a new journal entry",
                "icon": "pi-plus",
                "url": "/accounting/journal-entries/new",
                "color": "primary"
            },
            {
                "id": "record_payment",
                "title": "Record Payment",
                "description": "Record a vendor or customer payment",
                "icon": "pi-money-bill",
                "url": "/payments/record",
                "color": "success"
            },
            {
                "id": "create_invoice",
                "title": "New Invoice",
                "description": "Create a customer invoice",
                "icon": "pi-file",
                "url": "/receivables/invoices/new",
                "color": "info"
            },
            {
                "id": "enter_bill",
                "title": "Enter Bill",
                "description": "Enter a vendor bill",
                "icon": "pi-receipt",
                "url": "/payables/bills/new",
                "color": "warning"
            },
            {
                "id": "bank_reconciliation",
                "title": "Bank Reconciliation",
                "description": "Reconcile bank statements",
                "icon": "pi-check-circle",
                "url": "/banking/reconciliation",
                "color": "secondary"
            },
            {
                "id": "generate_report",
                "title": "Generate Report",
                "description": "Create financial reports",
                "icon": "pi-chart-bar",
                "url": "/reports/generate",
                "color": "primary"
            }
        ]
        
        return actions

class ActivityFeedService:
    """Recent activity feed service"""
    
    @staticmethod
    def get_recent_activity(db: Session, user_id: str, limit: int = 20) -> List[Dict]:
        """Get Recent Activity."""
        """Get recent activity feed"""
        activities = []
        
        # Recent journal entries
        recent_entries = db.query(JournalEntry).order_by(
            JournalEntry.created_at.desc()
        ).limit(5).all()
        
        for entry in recent_entries:
            activities.append({
                "id": f"je_{entry.id}",
                "type": "journal_entry",
                "title": f"Journal Entry {entry.entry_number}",
                "description": entry.description,
                "amount": float(entry.total_debit),
                "status": entry.status,
                "created_at": entry.created_at.isoformat(),
                "created_by": entry.created_by,
                "url": f"/accounting/journal-entries/{entry.id}"
            })
        
        # Recent workflows
        recent_workflows = db.query(WorkflowInstance).order_by(
            WorkflowInstance.created_at.desc()
        ).limit(5).all()
        
        for workflow in recent_workflows:
            activities.append({
                "id": f"wf_{workflow.id}",
                "type": "workflow",
                "title": f"{workflow.workflow_type.replace('_', ' ').title()}",
                "description": f"Workflow {workflow.status}",
                "amount": float(workflow.amount) if workflow.amount else 0,
                "status": workflow.status,
                "created_at": workflow.created_at.isoformat(),
                "created_by": workflow.created_by,
                "url": f"/workflows/{workflow.id}"
            })
        
        # Recent invoices
        recent_invoices = db.query(Invoice).order_by(
            Invoice.created_at.desc()
        ).limit(3).all()
        
        for invoice in recent_invoices:
            activities.append({
                "id": f"inv_{invoice.id}",
                "type": "invoice",
                "title": f"Invoice {invoice.invoice_number}",
                "description": f"Customer invoice",
                "amount": float(invoice.total_amount),
                "status": invoice.status,
                "created_at": invoice.created_at.isoformat(),
                "created_by": "system",
                "url": f"/receivables/invoices/{invoice.id}"
            })
        
        # Recent bills
        recent_bills = db.query(Bill).order_by(
            Bill.created_at.desc()
        ).limit(3).all()
        
        for bill in recent_bills:
            activities.append({
                "id": f"bill_{bill.id}",
                "type": "bill",
                "title": f"Bill {bill.bill_number}",
                "description": f"Vendor bill",
                "amount": float(bill.total_amount),
                "status": bill.status,
                "created_at": bill.created_at.isoformat(),
                "created_by": "system",
                "url": f"/payables/bills/{bill.id}"
            })
        
        # Sort by created_at and limit
        activities.sort(key=lambda x: x['created_at'], reverse=True)
        return activities[:limit]

class DashboardMetrics:
    """Dashboard metrics and calculations"""
    
    @staticmethod
    def calculate_financial_ratios(db: Session) -> Dict:
        """Calculate Financial Ratios."""
        """Calculate key financial ratios"""
        # Get balance sheet totals
        total_assets = db.execute(text(
            "SELECT SUM(current_balance) FROM chart_of_accounts WHERE account_type = 'Asset'"
        )).scalar() or 0
        
        total_liabilities = db.execute(text(
            "SELECT SUM(current_balance) FROM chart_of_accounts WHERE account_type = 'Liability'"
        )).scalar() or 0
        
        current_assets = db.execute(text(
            "SELECT SUM(current_balance) FROM chart_of_accounts WHERE account_code LIKE '1%'"
        )).scalar() or 0
        
        current_liabilities = db.execute(text(
            "SELECT SUM(current_balance) FROM chart_of_accounts WHERE account_code LIKE '2%'"
        )).scalar() or 0
        
        # Calculate ratios
        current_ratio = current_assets / current_liabilities if current_liabilities > 0 else 0
        debt_to_equity = total_liabilities / (total_assets - total_liabilities) if (total_assets - total_liabilities) > 0 else 0
        
        return {
            "current_ratio": {
                "value": round(current_ratio, 2),
                "label": "Current Ratio",
                "benchmark": 2.0,
                "status": "good" if current_ratio >= 1.5 else "warning"
            },
            "debt_to_equity": {
                "value": round(debt_to_equity, 2),
                "label": "Debt-to-Equity",
                "benchmark": 0.5,
                "status": "good" if debt_to_equity <= 0.6 else "warning"
            },
            "working_capital": {
                "value": float(current_assets - current_liabilities),
                "label": "Working Capital",
                "benchmark": 50000,
                "status": "good"
            }
        }
    
    @staticmethod
    def get_performance_indicators(db: Session) -> Dict:
        """Get Performance Indicators."""
        """Get performance indicators"""
        # Days Sales Outstanding (DSO)
        ar_balance = db.execute(text(
            "SELECT SUM(current_balance) FROM chart_of_accounts WHERE account_code LIKE '1200%'"
        )).scalar() or 0
        
        daily_sales = 1000  # Simplified - should calculate from actual sales
        dso = ar_balance / daily_sales if daily_sales > 0 else 0
        
        # Days Payable Outstanding (DPO)
        ap_balance = db.execute(text(
            "SELECT SUM(current_balance) FROM chart_of_accounts WHERE account_code LIKE '2000%'"
        )).scalar() or 0
        
        daily_purchases = 800  # Simplified
        dpo = ap_balance / daily_purchases if daily_purchases > 0 else 0
        
        return {
            "days_sales_outstanding": {
                "value": round(dso, 1),
                "label": "Days Sales Outstanding",
                "benchmark": 30,
                "trend": "down"
            },
            "days_payable_outstanding": {
                "value": round(dpo, 1),
                "label": "Days Payable Outstanding", 
                "benchmark": 45,
                "trend": "up"
            },
            "cash_conversion_cycle": {
                "value": round(dso - dpo, 1),
                "label": "Cash Conversion Cycle",
                "benchmark": 15,
                "trend": "neutral"
            }
        }