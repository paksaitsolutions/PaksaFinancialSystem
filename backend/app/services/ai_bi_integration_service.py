"""
AI/BI Integration Service - Real-time Financial Intelligence
===========================================================
Comprehensive AI/BI service that integrates with all financial modules
to provide real-time insights, anomaly detection, and predictive analytics.
"""
from decimal import Decimal
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.models import (
    # Core Financial
    JournalEntry, JournalEntryLine, ChartOfAccounts,
    # AP/AR
    APInvoice, ARInvoice, APPayment, ARPayment,
    # Cash & Banking
    BankTransaction, BankAccount,
    # Payroll & HRM
    PayrollRun, Employee, Department,
    # Inventory & Assets
    InventoryItem, FixedAsset,
    # AI/BI Models
    AIInsight, AIRecommendation, AIAnomaly, AIPrediction, AIAnalyticsReport
)
from app.services.base import BaseService

class AIBIIntegrationService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db, AIInsight)
    
    # ========================================================================
    # REAL-TIME ANOMALY DETECTION
    # ========================================================================
    
    def detect_financial_anomalies(self, company_id: UUID) -> List[AIAnomaly]:
        """Detect anomalies across all financial modules"""
        anomalies = []
        
        # AP Invoice Anomalies
        anomalies.extend(self._detect_ap_anomalies(company_id))
        
        # AR Invoice Anomalies  
        anomalies.extend(self._detect_ar_anomalies(company_id))
        
        # Cash Flow Anomalies
        anomalies.extend(self._detect_cash_anomalies(company_id))
        
        # Payroll Anomalies
        anomalies.extend(self._detect_payroll_anomalies(company_id))
        
        # Inventory Anomalies
        anomalies.extend(self._detect_inventory_anomalies(company_id))
        
        return anomalies
    
    def _detect_ap_anomalies(self, company_id: UUID) -> List[AIAnomaly]:
        """Detect AP invoice anomalies"""
        anomalies = []
        
        # Unusual invoice amounts (3x standard deviation)
        avg_amount = self.db.query(func.avg(APInvoice.total_amount)).filter(
            APInvoice.company_id == company_id
        ).scalar() or 0
        
        std_amount = self.db.query(func.stddev(APInvoice.total_amount)).filter(
            APInvoice.company_id == company_id
        ).scalar() or 0
        
        threshold = avg_amount + (3 * std_amount)
        
        unusual_invoices = self.db.query(APInvoice).filter(
            and_(
                APInvoice.company_id == company_id,
                APInvoice.total_amount > threshold,
                APInvoice.created_at >= datetime.now() - timedelta(days=30)
            )
        ).all()
        
        for invoice in unusual_invoices:
            anomaly = AIAnomaly(
                company_id=company_id,
                title=f"Unusual AP Invoice Amount",
                description=f"Invoice {invoice.invoice_number} amount ${invoice.total_amount} exceeds normal range",
                anomaly_type="amount_outlier",
                module="accounts_payable",
                severity="High",
                anomaly_score=float(invoice.total_amount / avg_amount),
                threshold=float(threshold),
                affected_records=[{"invoice_id": str(invoice.id), "amount": float(invoice.total_amount)}]
            )
            self.db.add(anomaly)
            anomalies.append(anomaly)
        
        return anomalies
    
    def _detect_ar_anomalies(self, company_id: UUID) -> List[AIAnomaly]:
        """Detect AR invoice anomalies"""
        anomalies = []
        
        # Overdue invoices pattern analysis
        overdue_invoices = self.db.query(ARInvoice).filter(
            and_(
                ARInvoice.company_id == company_id,
                ARInvoice.due_date < datetime.now().date(),
                ARInvoice.status.in_(["sent", "overdue"])
            )
        ).all()
        
        if len(overdue_invoices) > 10:  # Threshold for concern
            total_overdue = sum(inv.total_amount - inv.paid_amount for inv in overdue_invoices)
            
            anomaly = AIAnomaly(
                company_id=company_id,
                title="High Volume of Overdue Invoices",
                description=f"{len(overdue_invoices)} invoices overdue totaling ${total_overdue}",
                anomaly_type="collection_risk",
                module="accounts_receivable",
                severity="Critical",
                anomaly_score=len(overdue_invoices) / 10.0,
                threshold=10.0,
                affected_records=[{"count": len(overdue_invoices), "total_amount": float(total_overdue)}]
            )
            self.db.add(anomaly)
            anomalies.append(anomaly)
        
        return anomalies
    
    def _detect_cash_anomalies(self, company_id: UUID) -> List[AIAnomaly]:
        """Detect cash flow anomalies"""
        anomalies = []
        
        # Sudden large cash outflows
        recent_outflows = self.db.query(BankTransaction).filter(
            and_(
                BankTransaction.company_id == company_id,
                BankTransaction.amount < 0,
                BankTransaction.transaction_date >= datetime.now().date() - timedelta(days=7)
            )
        ).all()
        
        total_outflow = sum(abs(t.amount) for t in recent_outflows)
        
        # Get average weekly outflow for comparison
        avg_weekly_outflow = self.db.query(func.avg(func.abs(BankTransaction.amount))).filter(
            and_(
                BankTransaction.company_id == company_id,
                BankTransaction.amount < 0,
                BankTransaction.transaction_date >= datetime.now().date() - timedelta(days=90)
            )
        ).scalar() or 0
        
        if total_outflow > (avg_weekly_outflow * 2):  # 2x normal outflow
            anomaly = AIAnomaly(
                company_id=company_id,
                title="Unusual Cash Outflow Pattern",
                description=f"Weekly cash outflow ${total_outflow} is {total_outflow/avg_weekly_outflow:.1f}x normal",
                anomaly_type="cash_flow_spike",
                module="cash_management",
                severity="High",
                anomaly_score=float(total_outflow / avg_weekly_outflow),
                threshold=2.0,
                affected_records=[{"weekly_outflow": float(total_outflow), "normal_avg": float(avg_weekly_outflow)}]
            )
            self.db.add(anomaly)
            anomalies.append(anomaly)
        
        return anomalies
    
    def _detect_payroll_anomalies(self, company_id: UUID) -> List[AIAnomaly]:
        """Detect payroll anomalies"""
        anomalies = []
        
        # Recent payroll runs with unusual totals
        recent_payrolls = self.db.query(PayrollRun).filter(
            and_(
                PayrollRun.company_id == company_id,
                PayrollRun.pay_date >= datetime.now().date() - timedelta(days=60)
            )
        ).all()
        
        if len(recent_payrolls) >= 2:
            amounts = [pr.total_gross for pr in recent_payrolls]
            avg_amount = sum(amounts) / len(amounts)
            
            for payroll in recent_payrolls[-2:]:  # Check last 2 payrolls
                if payroll.total_gross > (avg_amount * 1.5):  # 50% above average
                    anomaly = AIAnomaly(
                        company_id=company_id,
                        title="Unusual Payroll Amount",
                        description=f"Payroll {payroll.run_number} total ${payroll.total_gross} exceeds normal range",
                        anomaly_type="payroll_spike",
                        module="payroll",
                        severity="Medium",
                        anomaly_score=float(payroll.total_gross / avg_amount),
                        threshold=1.5,
                        affected_records=[{"payroll_id": str(payroll.id), "amount": float(payroll.total_gross)}]
                    )
                    self.db.add(anomaly)
                    anomalies.append(anomaly)
        
        return anomalies
    
    def _detect_inventory_anomalies(self, company_id: UUID) -> List[AIAnomaly]:
        """Detect inventory anomalies"""
        anomalies = []
        
        # Items below reorder level
        low_stock_items = self.db.query(InventoryItem).filter(
            and_(
                InventoryItem.company_id == company_id,
                InventoryItem.quantity_on_hand <= InventoryItem.reorder_level,
                InventoryItem.status == "active"
            )
        ).all()
        
        if low_stock_items:
            anomaly = AIAnomaly(
                company_id=company_id,
                title="Low Stock Alert",
                description=f"{len(low_stock_items)} items below reorder level",
                anomaly_type="inventory_shortage",
                module="inventory",
                severity="Medium",
                anomaly_score=len(low_stock_items),
                threshold=1.0,
                affected_records=[{"item_id": str(item.id), "current_qty": float(item.quantity_on_hand), 
                                 "reorder_level": float(item.reorder_level)} for item in low_stock_items]
            )
            self.db.add(anomaly)
            anomalies.append(anomaly)
        
        return anomalies
    
    # ========================================================================
    # PREDICTIVE ANALYTICS
    # ========================================================================
    
    def generate_cash_flow_prediction(self, company_id: UUID, days_ahead: int = 30) -> AIPrediction:
        """Predict cash flow for next N days"""
        
        # Get historical cash flow data
        historical_transactions = self.db.query(BankTransaction).filter(
            and_(
                BankTransaction.company_id == company_id,
                BankTransaction.transaction_date >= datetime.now().date() - timedelta(days=90)
            )
        ).all()
        
        # Simple trend analysis (in production, use ML models)
        daily_flows = {}
        for transaction in historical_transactions:
            date_key = transaction.transaction_date.strftime('%Y-%m-%d')
            if date_key not in daily_flows:
                daily_flows[date_key] = 0
            daily_flows[date_key] += transaction.amount
        
        # Calculate average daily flow
        avg_daily_flow = sum(daily_flows.values()) / len(daily_flows) if daily_flows else 0
        
        # Predict future cash flow
        predicted_value = avg_daily_flow * days_ahead
        
        prediction = AIPrediction(
            company_id=company_id,
            prediction_type="cash_flow",
            module="cash_management",
            target_date=datetime.now() + timedelta(days=days_ahead),
            predicted_value=float(predicted_value),
            confidence_interval={"lower": float(predicted_value * 0.8), "upper": float(predicted_value * 1.2)},
            accuracy_score=0.75,  # Mock accuracy
            model_version="v1.0",
            input_features={"historical_days": 90, "avg_daily_flow": float(avg_daily_flow)}
        )
        
        self.db.add(prediction)
        return prediction
    
    def generate_revenue_prediction(self, company_id: UUID, months_ahead: int = 3) -> AIPrediction:
        """Predict revenue for next N months"""
        
        # Get historical AR invoice data
        historical_invoices = self.db.query(ARInvoice).filter(
            and_(
                ARInvoice.company_id == company_id,
                ARInvoice.invoice_date >= datetime.now().date() - timedelta(days=365),
                ARInvoice.status.in_(["paid", "sent"])
            )
        ).all()
        
        # Calculate monthly revenue trend
        monthly_revenue = {}
        for invoice in historical_invoices:
            month_key = invoice.invoice_date.strftime('%Y-%m')
            if month_key not in monthly_revenue:
                monthly_revenue[month_key] = 0
            monthly_revenue[month_key] += invoice.total_amount
        
        # Simple trend calculation
        avg_monthly_revenue = sum(monthly_revenue.values()) / len(monthly_revenue) if monthly_revenue else 0
        predicted_value = avg_monthly_revenue * months_ahead
        
        prediction = AIPrediction(
            company_id=company_id,
            prediction_type="revenue",
            module="accounts_receivable",
            target_date=datetime.now() + timedelta(days=months_ahead * 30),
            predicted_value=float(predicted_value),
            confidence_interval={"lower": float(predicted_value * 0.85), "upper": float(predicted_value * 1.15)},
            accuracy_score=0.80,
            model_version="v1.0",
            input_features={"historical_months": len(monthly_revenue), "avg_monthly_revenue": float(avg_monthly_revenue)}
        )
        
        self.db.add(prediction)
        return prediction
    
    # ========================================================================
    # INTELLIGENT RECOMMENDATIONS
    # ========================================================================
    
    def generate_financial_recommendations(self, company_id: UUID) -> List[AIRecommendation]:
        """Generate actionable financial recommendations"""
        recommendations = []
        
        # Cash flow optimization
        recommendations.extend(self._generate_cash_flow_recommendations(company_id))
        
        # AR collection optimization
        recommendations.extend(self._generate_ar_recommendations(company_id))
        
        # AP payment optimization
        recommendations.extend(self._generate_ap_recommendations(company_id))
        
        # Cost reduction opportunities
        recommendations.extend(self._generate_cost_recommendations(company_id))
        
        return recommendations
    
    def _generate_cash_flow_recommendations(self, company_id: UUID) -> List[AIRecommendation]:
        """Generate cash flow optimization recommendations"""
        recommendations = []
        
        # Check current cash position
        current_balance = self.db.query(func.sum(BankAccount.current_balance)).filter(
            BankAccount.company_id == company_id
        ).scalar() or 0
        
        if current_balance < 10000:  # Low cash threshold
            recommendation = AIRecommendation(
                company_id=company_id,
                title="Improve Cash Flow Management",
                description="Current cash position is low. Consider accelerating AR collections and optimizing AP payments.",
                recommendation_type="cash_flow_optimization",
                module="cash_management",
                priority="High",
                confidence_score=0.85,
                estimated_impact=5000.0,
                action_items=[
                    "Send payment reminders to overdue customers",
                    "Negotiate extended payment terms with vendors",
                    "Consider invoice factoring for immediate cash"
                ]
            )
            self.db.add(recommendation)
            recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_ar_recommendations(self, company_id: UUID) -> List[AIRecommendation]:
        """Generate AR optimization recommendations"""
        recommendations = []
        
        # Check for overdue invoices
        overdue_count = self.db.query(func.count(ARInvoice.id)).filter(
            and_(
                ARInvoice.company_id == company_id,
                ARInvoice.due_date < datetime.now().date(),
                ARInvoice.status.in_(["sent", "overdue"])
            )
        ).scalar() or 0
        
        if overdue_count > 5:
            recommendation = AIRecommendation(
                company_id=company_id,
                title="Enhance Collections Process",
                description=f"You have {overdue_count} overdue invoices. Implement automated collection workflows.",
                recommendation_type="collections_optimization",
                module="accounts_receivable",
                priority="High",
                confidence_score=0.90,
                estimated_impact=15000.0,
                action_items=[
                    "Set up automated payment reminders",
                    "Implement early payment discounts",
                    "Review customer credit limits"
                ]
            )
            self.db.add(recommendation)
            recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_ap_recommendations(self, company_id: UUID) -> List[AIRecommendation]:
        """Generate AP optimization recommendations"""
        recommendations = []
        
        # Check for early payment discount opportunities
        upcoming_invoices = self.db.query(APInvoice).filter(
            and_(
                APInvoice.company_id == company_id,
                APInvoice.due_date >= datetime.now().date(),
                APInvoice.due_date <= datetime.now().date() + timedelta(days=30),
                APInvoice.status == "approved"
            )
        ).all()
        
        if len(upcoming_invoices) > 10:
            total_amount = sum(inv.total_amount for inv in upcoming_invoices)
            potential_savings = total_amount * 0.02  # Assume 2% early payment discount
            
            recommendation = AIRecommendation(
                company_id=company_id,
                title="Optimize Payment Timing",
                description=f"Consider early payment discounts on {len(upcoming_invoices)} invoices for potential savings of ${potential_savings:.2f}",
                recommendation_type="payment_optimization",
                module="accounts_payable",
                priority="Medium",
                confidence_score=0.75,
                estimated_impact=float(potential_savings),
                action_items=[
                    "Negotiate early payment discounts with vendors",
                    "Implement payment scheduling optimization",
                    "Review cash flow to maximize discount opportunities"
                ]
            )
            self.db.add(recommendation)
            recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_cost_recommendations(self, company_id: UUID) -> List[AIRecommendation]:
        """Generate cost reduction recommendations"""
        recommendations = []
        
        # Analyze expense patterns from GL
        expense_accounts = self.db.query(ChartOfAccounts).filter(
            and_(
                ChartOfAccounts.company_id == company_id,
                ChartOfAccounts.account_type == "Expense"
            )
        ).all()
        
        for account in expense_accounts[:5]:  # Check top 5 expense accounts
            # Get recent expense total using join
            recent_expenses = self.db.query(func.sum(JournalEntryLine.debit_amount)).join(
                JournalEntry
            ).filter(
                and_(
                    JournalEntryLine.account_id == account.id,
                    JournalEntry.company_id == company_id,
                    JournalEntry.entry_date >= datetime.now().date() - timedelta(days=90)
                )
            ).scalar() or 0
            
            if recent_expenses > 5000:  # Significant expense threshold
                recommendation = AIRecommendation(
                    company_id=company_id,
                    title=f"Review {account.account_name} Expenses",
                    description=f"Recent expenses in {account.account_name} total ${recent_expenses}. Consider cost optimization.",
                    recommendation_type="cost_optimization",
                    module="general_ledger",
                    priority="Medium",
                    confidence_score=0.70,
                    estimated_impact=float(recent_expenses * 0.1),  # 10% potential savings
                    action_items=[
                        f"Review all {account.account_name} transactions",
                        "Negotiate better rates with suppliers",
                        "Consider alternative vendors or solutions"
                    ]
                )
                self.db.add(recommendation)
                recommendations.append(recommendation)
        
        return recommendations
    
    # ========================================================================
    # COMPREHENSIVE ANALYTICS REPORTS
    # ========================================================================
    
    def generate_comprehensive_report(self, company_id: UUID) -> AIAnalyticsReport:
        """Generate comprehensive AI/BI analytics report"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Collect all insights
        insights = self.detect_financial_anomalies(company_id)
        recommendations = self.generate_financial_recommendations(company_id)
        cash_prediction = self.generate_cash_flow_prediction(company_id)
        revenue_prediction = self.generate_revenue_prediction(company_id)
        
        # Compile report data
        report_data = {
            "executive_summary": {
                "total_anomalies": len(insights),
                "critical_issues": len([a for a in insights if a.severity == "Critical"]),
                "recommendations": len(recommendations),
                "cash_flow_prediction": {
                    "30_day_forecast": cash_prediction.predicted_value,
                    "confidence": cash_prediction.accuracy_score
                },
                "revenue_prediction": {
                    "90_day_forecast": revenue_prediction.predicted_value,
                    "confidence": revenue_prediction.accuracy_score
                }
            },
            "module_insights": {
                "accounts_payable": len([a for a in insights if a.module == "accounts_payable"]),
                "accounts_receivable": len([a for a in insights if a.module == "accounts_receivable"]),
                "cash_management": len([a for a in insights if a.module == "cash_management"]),
                "payroll": len([a for a in insights if a.module == "payroll"]),
                "inventory": len([a for a in insights if a.module == "inventory"])
            },
            "recommendations_by_priority": {
                "high": len([r for r in recommendations if r.priority == "High"]),
                "medium": len([r for r in recommendations if r.priority == "Medium"]),
                "low": len([r for r in recommendations if r.priority == "Low"])
            }
        }
        
        report = AIAnalyticsReport(
            company_id=company_id,
            report_name=f"Financial Intelligence Report - {end_date.strftime('%Y-%m-%d')}",
            report_type="comprehensive_financial_analysis",
            module="ai_bi_integration",
            data_range_start=start_date,
            data_range_end=end_date,
            report_data=report_data,
            insights_count=len(insights),
            anomalies_count=len([a for a in insights if isinstance(a, AIAnomaly)]),
            recommendations_count=len(recommendations),
            generated_by="AI/BI Integration Service"
        )
        
        self.db.add(report)
        self.db.commit()
        
        return report