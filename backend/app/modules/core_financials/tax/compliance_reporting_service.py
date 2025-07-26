from typing import Dict, List, Optional, Any
from decimal import Decimal
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, extract
from .models import TaxReturn, TaxPayment, TaxCalculation, TaxJurisdiction
from .schemas import ComplianceReport, FilingStatus, ComplianceAlert

class ComplianceReportingService:
    """Service for comprehensive tax compliance reporting"""
    
    # Compliance status definitions
    COMPLIANCE_STATUSES = {
        'COMPLIANT': 'All requirements met',
        'WARNING': 'Minor issues requiring attention',
        'NON_COMPLIANT': 'Critical compliance issues',
        'OVERDUE': 'Past due filings or payments'
    }
    
    async def generate_comprehensive_compliance_report(
        self,
        db: AsyncSession,
        company_id: int,
        reporting_period: str,  # 'monthly', 'quarterly', 'annual'
        year: int,
        period: Optional[int] = None
    ) -> ComplianceReport:
        """Generate comprehensive compliance report"""
        
        # Determine date range based on reporting period
        start_date, end_date = self._get_period_dates(reporting_period, year, period)
        
        # Get all tax returns for the period
        returns_result = await db.execute(
            select(TaxReturn).where(
                and_(
                    TaxReturn.company_id == company_id,
                    TaxReturn.tax_period_start >= start_date,
                    TaxReturn.tax_period_end <= end_date
                )
            )
        )
        tax_returns = returns_result.scalars().all()
        
        # Analyze filing compliance
        filing_compliance = await self._analyze_filing_compliance(db, tax_returns)
        
        # Analyze payment compliance
        payment_compliance = await self._analyze_payment_compliance(db, company_id, start_date, end_date)
        
        # Generate compliance alerts
        alerts = await self._generate_compliance_alerts(db, company_id, tax_returns)
        
        # Calculate overall compliance score
        overall_score = self._calculate_overall_compliance_score(
            filing_compliance, payment_compliance
        )
        
        # Get jurisdiction-specific compliance
        jurisdiction_compliance = await self._analyze_jurisdiction_compliance(
            db, company_id, start_date, end_date
        )
        
        return ComplianceReport(
            company_id=company_id,
            reporting_period=reporting_period,
            period_start=start_date,
            period_end=end_date,
            overall_compliance_score=overall_score,
            filing_compliance=filing_compliance,
            payment_compliance=payment_compliance,
            jurisdiction_compliance=jurisdiction_compliance,
            compliance_alerts=alerts,
            recommendations=self._generate_recommendations(filing_compliance, payment_compliance, alerts)
        )
    
    async def _analyze_filing_compliance(
        self,
        db: AsyncSession,
        tax_returns: List['TaxReturn']
    ) -> Dict[str, Any]:
        """Analyze filing compliance metrics"""
        
        total_returns = len(tax_returns)
        filed_returns = len([r for r in tax_returns if r.filing_status == 'filed'])
        overdue_returns = len([r for r in tax_returns if r.due_date < date.today() and r.filing_status != 'filed'])
        draft_returns = len([r for r in tax_returns if r.filing_status == 'draft'])
        
        # Calculate filing timeliness
        timely_filings = 0
        late_filings = 0
        
        for return_obj in tax_returns:
            if return_obj.filing_status == 'filed' and return_obj.filing_date:
                if return_obj.filing_date <= return_obj.due_date:
                    timely_filings += 1
                else:
                    late_filings += 1
        
        filing_rate = (filed_returns / total_returns * 100) if total_returns > 0 else 0
        timeliness_rate = (timely_filings / filed_returns * 100) if filed_returns > 0 else 0
        
        return {
            'total_returns_due': total_returns,
            'filed_returns': filed_returns,
            'overdue_returns': overdue_returns,
            'draft_returns': draft_returns,
            'filing_rate': round(filing_rate, 2),
            'timely_filings': timely_filings,
            'late_filings': late_filings,
            'timeliness_rate': round(timeliness_rate, 2),
            'status': self._get_filing_status(filing_rate, timeliness_rate, overdue_returns)
        }
    
    async def _analyze_payment_compliance(
        self,
        db: AsyncSession,
        company_id: int,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Analyze payment compliance metrics"""
        
        # Get all tax payments for the period
        payments_result = await db.execute(
            select(TaxPayment).where(
                and_(
                    TaxPayment.company_id == company_id,
                    TaxPayment.payment_date >= start_date,
                    TaxPayment.payment_date <= end_date
                )
            )
        )
        tax_payments = payments_result.scalars().all()
        
        # Get all tax returns with payment obligations
        returns_with_tax_due_result = await db.execute(
            select(TaxReturn).where(
                and_(
                    TaxReturn.company_id == company_id,
                    TaxReturn.tax_period_start >= start_date,
                    TaxReturn.tax_period_end <= end_date,
                    TaxReturn.tax_due > 0
                )
            )
        )
        returns_with_tax_due = returns_with_tax_due_result.scalars().all()
        
        # Calculate payment metrics
        total_tax_due = sum(r.tax_due or Decimal('0') for r in returns_with_tax_due)
        total_tax_paid = sum(p.amount for p in tax_payments)
        outstanding_balance = total_tax_due - total_tax_paid
        
        # Analyze payment timeliness
        timely_payments = 0
        late_payments = 0
        
        for payment in tax_payments:
            # Find corresponding return
            corresponding_return = next(
                (r for r in returns_with_tax_due if r.id == payment.tax_return_id),
                None
            )
            
            if corresponding_return and corresponding_return.due_date:
                if payment.payment_date <= corresponding_return.due_date:
                    timely_payments += 1
                else:
                    late_payments += 1
        
        payment_rate = (total_tax_paid / total_tax_due * 100) if total_tax_due > 0 else 100
        timeliness_rate = (timely_payments / len(tax_payments) * 100) if tax_payments else 100
        
        return {
            'total_tax_due': float(total_tax_due),
            'total_tax_paid': float(total_tax_paid),
            'outstanding_balance': float(outstanding_balance),
            'payment_rate': round(payment_rate, 2),
            'timely_payments': timely_payments,
            'late_payments': late_payments,
            'timeliness_rate': round(timeliness_rate, 2),
            'status': self._get_payment_status(payment_rate, timeliness_rate, outstanding_balance)
        }
    
    async def _analyze_jurisdiction_compliance(
        self,
        db: AsyncSession,
        company_id: int,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Analyze compliance by jurisdiction"""
        
        # Get returns grouped by jurisdiction
        jurisdiction_result = await db.execute(
            select(
                TaxReturn.jurisdiction_name,
                func.count(TaxReturn.id).label('total_returns'),
                func.sum(func.case((TaxReturn.filing_status == 'filed', 1), else_=0)).label('filed_returns'),
                func.sum(TaxReturn.tax_due).label('total_tax_due'),
                func.sum(TaxReturn.tax_paid).label('total_tax_paid')
            )
            .where(
                and_(
                    TaxReturn.company_id == company_id,
                    TaxReturn.tax_period_start >= start_date,
                    TaxReturn.tax_period_end <= end_date
                )
            )
            .group_by(TaxReturn.jurisdiction_name)
        )
        
        jurisdiction_compliance = []
        
        for row in jurisdiction_result:
            filing_rate = (row.filed_returns / row.total_returns * 100) if row.total_returns > 0 else 0
            payment_rate = ((row.total_tax_paid or 0) / (row.total_tax_due or 1) * 100) if row.total_tax_due else 100
            
            compliance_status = 'COMPLIANT'
            if filing_rate < 100 or payment_rate < 95:
                compliance_status = 'WARNING'
            if filing_rate < 90 or payment_rate < 80:
                compliance_status = 'NON_COMPLIANT'
            
            jurisdiction_compliance.append({
                'jurisdiction_name': row.jurisdiction_name,
                'total_returns': row.total_returns,
                'filed_returns': row.filed_returns,
                'filing_rate': round(filing_rate, 2),
                'total_tax_due': float(row.total_tax_due or 0),
                'total_tax_paid': float(row.total_tax_paid or 0),
                'payment_rate': round(payment_rate, 2),
                'compliance_status': compliance_status
            })
        
        return jurisdiction_compliance
    
    async def _generate_compliance_alerts(
        self,
        db: AsyncSession,
        company_id: int,
        tax_returns: List['TaxReturn']
    ) -> List[ComplianceAlert]:
        """Generate compliance alerts"""
        
        alerts = []
        current_date = date.today()
        
        # Check for overdue returns
        overdue_returns = [r for r in tax_returns if r.due_date < current_date and r.filing_status != 'filed']
        for return_obj in overdue_returns:
            days_overdue = (current_date - return_obj.due_date).days
            alerts.append(ComplianceAlert(
                alert_type='OVERDUE_FILING',
                severity='HIGH' if days_overdue > 30 else 'MEDIUM',
                message=f"Tax return for {return_obj.jurisdiction_name} is {days_overdue} days overdue",
                entity_type='tax_return',
                entity_id=return_obj.id,
                due_date=return_obj.due_date,
                days_overdue=days_overdue
            ))
        
        # Check for upcoming due dates (next 30 days)
        upcoming_due = [r for r in tax_returns 
                       if current_date <= r.due_date <= current_date + timedelta(days=30)
                       and r.filing_status != 'filed']
        for return_obj in upcoming_due:
            days_until_due = (return_obj.due_date - current_date).days
            alerts.append(ComplianceAlert(
                alert_type='UPCOMING_DUE_DATE',
                severity='MEDIUM' if days_until_due <= 7 else 'LOW',
                message=f"Tax return for {return_obj.jurisdiction_name} due in {days_until_due} days",
                entity_type='tax_return',
                entity_id=return_obj.id,
                due_date=return_obj.due_date,
                days_until_due=days_until_due
            ))
        
        # Check for outstanding tax balances
        outstanding_returns = [r for r in tax_returns 
                             if (r.tax_due or 0) > (r.tax_paid or 0)]
        for return_obj in outstanding_returns:
            outstanding_amount = (return_obj.tax_due or Decimal('0')) - (return_obj.tax_paid or Decimal('0'))
            if outstanding_amount > 0:
                alerts.append(ComplianceAlert(
                    alert_type='OUTSTANDING_BALANCE',
                    severity='HIGH' if outstanding_amount > 10000 else 'MEDIUM',
                    message=f"Outstanding tax balance of ${outstanding_amount:,.2f} for {return_obj.jurisdiction_name}",
                    entity_type='tax_return',
                    entity_id=return_obj.id,
                    amount=outstanding_amount
                ))
        
        return alerts
    
    def _get_period_dates(self, reporting_period: str, year: int, period: Optional[int]) -> tuple[date, date]:
        """Get start and end dates for reporting period"""
        
        if reporting_period == 'annual':
            return date(year, 1, 1), date(year, 12, 31)
        
        elif reporting_period == 'quarterly':
            if not period or period < 1 or period > 4:
                raise ValueError("Quarter must be 1-4")
            
            quarter_start_month = (period - 1) * 3 + 1
            start_date = date(year, quarter_start_month, 1)
            
            if period == 4:
                end_date = date(year, 12, 31)
            else:
                next_quarter_month = period * 3 + 1
                end_date = date(year, next_quarter_month, 1) - timedelta(days=1)
            
            return start_date, end_date
        
        elif reporting_period == 'monthly':
            if not period or period < 1 or period > 12:
                raise ValueError("Month must be 1-12")
            
            start_date = date(year, period, 1)
            if period == 12:
                end_date = date(year, 12, 31)
            else:
                end_date = date(year, period + 1, 1) - timedelta(days=1)
            
            return start_date, end_date
        
        else:
            raise ValueError("Invalid reporting period")
    
    def _get_filing_status(self, filing_rate: float, timeliness_rate: float, overdue_count: int) -> str:
        """Determine filing compliance status"""
        
        if overdue_count > 0:
            return 'OVERDUE'
        elif filing_rate >= 95 and timeliness_rate >= 90:
            return 'COMPLIANT'
        elif filing_rate >= 80 and timeliness_rate >= 70:
            return 'WARNING'
        else:
            return 'NON_COMPLIANT'
    
    def _get_payment_status(self, payment_rate: float, timeliness_rate: float, outstanding_balance: Decimal) -> str:
        """Determine payment compliance status"""
        
        if outstanding_balance > 10000:
            return 'OVERDUE'
        elif payment_rate >= 95 and timeliness_rate >= 90:
            return 'COMPLIANT'
        elif payment_rate >= 80 and timeliness_rate >= 70:
            return 'WARNING'
        else:
            return 'NON_COMPLIANT'
    
    def _calculate_overall_compliance_score(
        self,
        filing_compliance: Dict[str, Any],
        payment_compliance: Dict[str, Any]
    ) -> int:
        """Calculate overall compliance score (0-100)"""
        
        # Weight filing and payment compliance equally
        filing_score = (filing_compliance['filing_rate'] + filing_compliance['timeliness_rate']) / 2
        payment_score = (payment_compliance['payment_rate'] + payment_compliance['timeliness_rate']) / 2
        
        overall_score = (filing_score + payment_score) / 2
        
        return int(round(overall_score))
    
    def _generate_recommendations(
        self,
        filing_compliance: Dict[str, Any],
        payment_compliance: Dict[str, Any],
        alerts: List[ComplianceAlert]
    ) -> List[str]:
        """Generate compliance recommendations"""
        
        recommendations = []
        
        # Filing recommendations
        if filing_compliance['filing_rate'] < 95:
            recommendations.append("Improve filing processes to ensure all returns are submitted on time")
        
        if filing_compliance['timeliness_rate'] < 90:
            recommendations.append("Implement automated reminders for upcoming filing deadlines")
        
        # Payment recommendations
        if payment_compliance['payment_rate'] < 95:
            recommendations.append("Review payment processes to ensure all tax obligations are met")
        
        if payment_compliance['timeliness_rate'] < 90:
            recommendations.append("Set up automated payment scheduling to avoid late payments")
        
        # Alert-based recommendations
        overdue_alerts = [a for a in alerts if a.alert_type == 'OVERDUE_FILING']
        if overdue_alerts:
            recommendations.append("Prioritize filing overdue returns to avoid penalties and interest")
        
        outstanding_alerts = [a for a in alerts if a.alert_type == 'OUTSTANDING_BALANCE']
        if outstanding_alerts:
            recommendations.append("Address outstanding tax balances to maintain good standing")
        
        if not recommendations:
            recommendations.append("Maintain current compliance practices and continue monitoring")
        
        return recommendations
    
    async def export_compliance_report(
        self,
        db: AsyncSession,
        report: ComplianceReport,
        format: str = 'json'
    ) -> Dict[str, Any]:
        """Export compliance report in specified format"""
        
        if format == 'json':
            return report.dict()
        
        elif format == 'summary':
            return {
                'company_id': report.company_id,
                'period': f"{report.reporting_period} - {report.period_start} to {report.period_end}",
                'overall_score': report.overall_compliance_score,
                'filing_rate': report.filing_compliance['filing_rate'],
                'payment_rate': report.payment_compliance['payment_rate'],
                'alert_count': len(report.compliance_alerts),
                'status': 'COMPLIANT' if report.overall_compliance_score >= 90 else 'NEEDS_ATTENTION'
            }
        
        else:
            raise ValueError("Unsupported export format")