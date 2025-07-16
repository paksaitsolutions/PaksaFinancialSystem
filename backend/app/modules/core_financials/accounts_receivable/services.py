from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from datetime import date, datetime, timedelta
from decimal import Decimal
import uuid

from .models import (
    Customer, ARInvoice, ARInvoiceLine, ARPayment, ARPaymentInvoice,
    CreditMemo, ARAnalytics, CustomerPerformanceMetrics
)
from .schemas import (
    CustomerCreate, CustomerUpdate, CustomerResponse,
    ARInvoiceCreate, ARInvoiceUpdate, ARInvoiceResponse,
    ARPaymentCreate, ARPaymentUpdate, ARPaymentResponse,
    CreditMemoCreate, CreditMemoResponse,
    ARSummaryResponse, CustomerSummaryResponse,
    ARAgingReportResponse, ARAgingReportItem
)

class CustomerService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_customer(self, customer_data: CustomerCreate) -> CustomerResponse:
        # Generate customer ID
        last_customer = self.db.query(Customer).order_by(desc(Customer.id)).first()
        customer_id = f"C{str((last_customer.id if last_customer else 0) + 1).zfill(6)}"
        
        customer = Customer(
            customer_id=customer_id,
            **customer_data.dict()
        )
        
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        
        # Create GL integration entry
        self._create_customer_gl_entry(customer)
        
        return CustomerResponse.from_orm(customer)
    
    def get_customer(self, customer_id: int) -> Optional[CustomerResponse]:
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        return CustomerResponse.from_orm(customer) if customer else None
    
    def get_customers(
        self, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[CustomerResponse]:
        query = self.db.query(Customer)
        
        if search:
            query = query.filter(
                or_(
                    Customer.name.ilike(f"%{search}%"),
                    Customer.customer_id.ilike(f"%{search}%"),
                    Customer.email.ilike(f"%{search}%")
                )
            )
        
        if category:
            query = query.filter(Customer.category == category)
        
        if status:
            query = query.filter(Customer.status == status)
        
        customers = query.offset(skip).limit(limit).all()
        return [CustomerResponse.from_orm(customer) for customer in customers]
    
    def update_customer(self, customer_id: int, customer_data: CustomerUpdate) -> Optional[CustomerResponse]:
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return None
        
        update_data = customer_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(customer, field, value)
        
        customer.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(customer)
        
        return CustomerResponse.from_orm(customer)
    
    def delete_customer(self, customer_id: int) -> bool:
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return False
        
        # Check for outstanding invoices
        outstanding_invoices = self.db.query(ARInvoice).filter(
            and_(ARInvoice.customer_id == customer_id, ARInvoice.balance_due > 0)
        ).count()
        
        if outstanding_invoices > 0:
            raise ValueError("Cannot delete customer with outstanding invoices")
        
        self.db.delete(customer)
        self.db.commit()
        return True
    
    def _create_customer_gl_entry(self, customer: Customer):
        """Create GL account for customer if needed"""
        # This would integrate with GL module to create customer receivable account
        pass

class ARInvoiceService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_invoice(self, invoice_data: ARInvoiceCreate) -> ARInvoiceResponse:
        # Generate invoice number
        last_invoice = self.db.query(ARInvoice).order_by(desc(ARInvoice.id)).first()
        invoice_number = f"INV-{datetime.now().year}-{str((last_invoice.id if last_invoice else 0) + 1).zfill(6)}"
        
        # Calculate totals
        subtotal = sum(line.quantity * line.unit_price - line.discount_amount for line in invoice_data.lines)
        total_amount = subtotal + invoice_data.tax_amount + invoice_data.shipping_amount - invoice_data.discount_amount
        
        invoice = ARInvoice(
            invoice_number=invoice_number,
            customer_id=invoice_data.customer_id,
            invoice_date=invoice_data.invoice_date,
            due_date=invoice_data.due_date,
            description=invoice_data.description,
            so_number=invoice_data.so_number,
            po_number=invoice_data.po_number,
            subtotal=subtotal,
            tax_amount=invoice_data.tax_amount,
            discount_amount=invoice_data.discount_amount,
            shipping_amount=invoice_data.shipping_amount,
            total_amount=total_amount,
            balance_due=total_amount,
            currency_code=invoice_data.currency_code,
            exchange_rate=invoice_data.exchange_rate,
            status=invoice_data.status,
            order_source=invoice_data.order_source,
            marketplace_order_id=invoice_data.marketplace_order_id,
            tags=invoice_data.tags,
            custom_fields=invoice_data.custom_fields
        )
        
        self.db.add(invoice)
        self.db.flush()
        
        # Add invoice lines
        for line_data in invoice_data.lines:
            line_total = line_data.quantity * line_data.unit_price - line_data.discount_amount
            tax_amount = line_total * (line_data.tax_rate / 100) if line_data.tax_rate else 0
            
            line = ARInvoiceLine(
                invoice_id=invoice.id,
                line_number=line_data.line_number,
                product_code=line_data.product_code,
                description=line_data.description,
                category=line_data.category,
                quantity=line_data.quantity,
                unit_of_measure=line_data.unit_of_measure,
                unit_price=line_data.unit_price,
                discount_percentage=line_data.discount_percentage,
                discount_amount=line_data.discount_amount,
                line_total=line_total,
                tax_code=line_data.tax_code,
                tax_rate=line_data.tax_rate,
                tax_amount=tax_amount,
                revenue_account_id=line_data.revenue_account_id
            )
            self.db.add(line)
        
        self.db.commit()
        self.db.refresh(invoice)
        
        # Create GL entries
        self._create_invoice_gl_entries(invoice)
        
        return ARInvoiceResponse.from_orm(invoice)
    
    def get_invoice(self, invoice_id: int) -> Optional[ARInvoiceResponse]:
        invoice = self.db.query(ARInvoice).filter(ARInvoice.id == invoice_id).first()
        return ARInvoiceResponse.from_orm(invoice) if invoice else None
    
    def get_invoices(
        self,
        skip: int = 0,
        limit: int = 100,
        customer_id: Optional[int] = None,
        status: Optional[str] = None,
        overdue_only: bool = False
    ) -> List[ARInvoiceResponse]:
        query = self.db.query(ARInvoice)
        
        if customer_id:
            query = query.filter(ARInvoice.customer_id == customer_id)
        
        if status:
            query = query.filter(ARInvoice.status == status)
        
        if overdue_only:
            query = query.filter(
                and_(ARInvoice.due_date < date.today(), ARInvoice.balance_due > 0)
            )
        
        invoices = query.order_by(desc(ARInvoice.created_at)).offset(skip).limit(limit).all()
        return [ARInvoiceResponse.from_orm(invoice) for invoice in invoices]
    
    def update_invoice(self, invoice_id: int, invoice_data: ARInvoiceUpdate) -> Optional[ARInvoiceResponse]:
        invoice = self.db.query(ARInvoice).filter(ARInvoice.id == invoice_id).first()
        if not invoice:
            return None
        
        # Check if invoice can be updated
        if invoice.status in ['paid', 'cancelled']:
            raise ValueError("Cannot update paid or cancelled invoice")
        
        update_data = invoice_data.dict(exclude_unset=True)
        
        # Handle line items update
        if 'lines' in update_data:
            # Delete existing lines
            self.db.query(ARInvoiceLine).filter(ARInvoiceLine.invoice_id == invoice_id).delete()
            
            # Add new lines
            for line_data in update_data['lines']:
                line_total = line_data['quantity'] * line_data['unit_price'] - line_data.get('discount_amount', 0)
                line = ARInvoiceLine(
                    invoice_id=invoice.id,
                    **line_data,
                    line_total=line_total
                )
                self.db.add(line)
            
            del update_data['lines']
        
        # Update invoice fields
        for field, value in update_data.items():
            setattr(invoice, field, value)
        
        # Recalculate totals if needed
        if 'lines' in invoice_data.dict(exclude_unset=True):
            self._recalculate_invoice_totals(invoice)
        
        invoice.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(invoice)
        
        return ARInvoiceResponse.from_orm(invoice)
    
    def send_invoice(self, invoice_id: int) -> bool:
        invoice = self.db.query(ARInvoice).filter(ARInvoice.id == invoice_id).first()
        if not invoice:
            return False
        
        invoice.status = 'sent'
        invoice.sent_date = date.today()
        invoice.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        # Send email notification (integrate with email service)
        self._send_invoice_email(invoice)
        
        return True
    
    def _create_invoice_gl_entries(self, invoice: ARInvoice):
        """Create GL entries for invoice"""
        # This would integrate with GL module
        # Dr. Accounts Receivable
        # Cr. Revenue
        # Cr. Tax Payable (if applicable)
        pass
    
    def _recalculate_invoice_totals(self, invoice: ARInvoice):
        """Recalculate invoice totals based on lines"""
        lines = self.db.query(ARInvoiceLine).filter(ARInvoiceLine.invoice_id == invoice.id).all()
        subtotal = sum(line.line_total for line in lines)
        invoice.subtotal = subtotal
        invoice.total_amount = subtotal + invoice.tax_amount + invoice.shipping_amount - invoice.discount_amount
        invoice.balance_due = invoice.total_amount - invoice.paid_amount
    
    def _send_invoice_email(self, invoice: ARInvoice):
        """Send invoice via email"""
        # Integrate with email service
        pass

class ARPaymentService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_payment(self, payment_data: ARPaymentCreate) -> ARPaymentResponse:
        # Generate payment number
        last_payment = self.db.query(ARPayment).order_by(desc(ARPayment.id)).first()
        payment_number = f"PAY-{datetime.now().year}-{str((last_payment.id if last_payment else 0) + 1).zfill(6)}"
        
        payment = ARPayment(
            payment_number=payment_number,
            customer_id=payment_data.customer_id,
            payment_date=payment_data.payment_date,
            amount=payment_data.amount,
            payment_method=payment_data.payment_method,
            reference_number=payment_data.reference_number,
            bank_account_id=payment_data.bank_account_id,
            transaction_id=payment_data.transaction_id,
            currency_code=payment_data.currency_code,
            exchange_rate=payment_data.exchange_rate,
            gateway_transaction_id=payment_data.gateway_transaction_id,
            gateway_name=payment_data.gateway_name,
            notes=payment_data.notes,
            tags=payment_data.tags
        )
        
        self.db.add(payment)
        self.db.flush()
        
        # Apply payment to invoices
        remaining_amount = payment_data.amount
        for i, invoice_id in enumerate(payment_data.invoice_ids):
            if remaining_amount <= 0:
                break
            
            invoice = self.db.query(ARInvoice).filter(ARInvoice.id == invoice_id).first()
            if not invoice:
                continue
            
            # Determine amount to apply
            if payment_data.amounts_applied and i < len(payment_data.amounts_applied):
                amount_to_apply = min(payment_data.amounts_applied[i], remaining_amount, invoice.balance_due)
            else:
                amount_to_apply = min(remaining_amount, invoice.balance_due)
            
            if amount_to_apply > 0:
                # Create payment application
                payment_invoice = ARPaymentInvoice(
                    payment_id=payment.id,
                    invoice_id=invoice_id,
                    amount_applied=amount_to_apply
                )
                self.db.add(payment_invoice)
                
                # Update invoice
                invoice.paid_amount += amount_to_apply
                invoice.balance_due -= amount_to_apply
                
                if invoice.balance_due <= 0:
                    invoice.status = 'paid'
                elif invoice.paid_amount > 0:
                    invoice.status = 'partial_payment'
                
                remaining_amount -= amount_to_apply
        
        self.db.commit()
        self.db.refresh(payment)
        
        # Create GL entries
        self._create_payment_gl_entries(payment)
        
        return ARPaymentResponse.from_orm(payment)
    
    def get_payment(self, payment_id: int) -> Optional[ARPaymentResponse]:
        payment = self.db.query(ARPayment).filter(ARPayment.id == payment_id).first()
        return ARPaymentResponse.from_orm(payment) if payment else None
    
    def get_payments(
        self,
        skip: int = 0,
        limit: int = 100,
        customer_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[ARPaymentResponse]:
        query = self.db.query(ARPayment)
        
        if customer_id:
            query = query.filter(ARPayment.customer_id == customer_id)
        
        if status:
            query = query.filter(ARPayment.status == status)
        
        payments = query.order_by(desc(ARPayment.created_at)).offset(skip).limit(limit).all()
        return [ARPaymentResponse.from_orm(payment) for payment in payments]
    
    def process_payment(self, payment_id: int) -> bool:
        payment = self.db.query(ARPayment).filter(ARPayment.id == payment_id).first()
        if not payment:
            return False
        
        payment.status = 'completed'
        payment.processed_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    def _create_payment_gl_entries(self, payment: ARPayment):
        """Create GL entries for payment"""
        # Dr. Cash/Bank Account
        # Cr. Accounts Receivable
        pass

class ARAnalyticsService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_ar_summary(self) -> ARSummaryResponse:
        # Calculate summary metrics
        total_outstanding = self.db.query(func.sum(ARInvoice.balance_due)).filter(
            ARInvoice.balance_due > 0
        ).scalar() or Decimal('0')
        
        overdue_amount = self.db.query(func.sum(ARInvoice.balance_due)).filter(
            and_(ARInvoice.due_date < date.today(), ARInvoice.balance_due > 0)
        ).scalar() or Decimal('0')
        
        # This month sales
        current_month_start = date.today().replace(day=1)
        this_month_sales = self.db.query(func.sum(ARInvoice.total_amount)).filter(
            and_(
                ARInvoice.invoice_date >= current_month_start,
                ARInvoice.status.in_(['sent', 'paid', 'partial_payment'])
            )
        ).scalar() or Decimal('0')
        
        # Customer counts
        total_customers = self.db.query(Customer).count()
        active_customers = self.db.query(Customer).filter(Customer.status == 'active').count()
        
        # Average collection days
        avg_collection_days = self._calculate_avg_collection_days()
        
        # Payment success rate
        payment_success_rate = self._calculate_payment_success_rate()
        
        # Top customers by sales
        top_customers = self._get_top_customers_by_sales()
        
        return ARSummaryResponse(
            total_outstanding=total_outstanding,
            overdue_amount=overdue_amount,
            this_month_sales=this_month_sales,
            avg_collection_days=avg_collection_days,
            total_customers=total_customers,
            active_customers=active_customers,
            payment_success_rate=payment_success_rate,
            top_customers_by_sales=top_customers
        )
    
    def get_aging_report(self) -> ARAgingReportResponse:
        customers = self.db.query(Customer).all()
        aging_items = []
        
        for customer in customers:
            invoices = self.db.query(ARInvoice).filter(
                and_(ARInvoice.customer_id == customer.id, ARInvoice.balance_due > 0)
            ).all()
            
            current = Decimal('0')
            days_1_30 = Decimal('0')
            days_31_60 = Decimal('0')
            days_61_90 = Decimal('0')
            over_90_days = Decimal('0')
            
            for invoice in invoices:
                days_overdue = (date.today() - invoice.due_date).days
                
                if days_overdue <= 0:
                    current += invoice.balance_due
                elif days_overdue <= 30:
                    days_1_30 += invoice.balance_due
                elif days_overdue <= 60:
                    days_31_60 += invoice.balance_due
                elif days_overdue <= 90:
                    days_61_90 += invoice.balance_due
                else:
                    over_90_days += invoice.balance_due
            
            total_outstanding = current + days_1_30 + days_31_60 + days_61_90 + over_90_days
            
            if total_outstanding > 0:
                aging_items.append(ARAgingReportItem(
                    customer_id=customer.id,
                    customer_name=customer.name,
                    current=current,
                    days_1_30=days_1_30,
                    days_31_60=days_31_60,
                    days_61_90=days_61_90,
                    over_90_days=over_90_days,
                    total_outstanding=total_outstanding
                ))
        
        # Calculate totals
        totals = ARAgingReportItem(
            customer_id=0,
            customer_name="TOTAL",
            current=sum(item.current for item in aging_items),
            days_1_30=sum(item.days_1_30 for item in aging_items),
            days_31_60=sum(item.days_31_60 for item in aging_items),
            days_61_90=sum(item.days_61_90 for item in aging_items),
            over_90_days=sum(item.over_90_days for item in aging_items),
            total_outstanding=sum(item.total_outstanding for item in aging_items)
        )
        
        return ARAgingReportResponse(
            report_date=date.today(),
            items=aging_items,
            totals=totals
        )
    
    def _calculate_avg_collection_days(self) -> Optional[Decimal]:
        # Calculate average days to collect payment
        paid_invoices = self.db.query(ARInvoice).filter(ARInvoice.status == 'paid').all()
        
        if not paid_invoices:
            return None
        
        total_days = 0
        count = 0
        
        for invoice in paid_invoices:
            # Find the last payment for this invoice
            last_payment = self.db.query(ARPaymentInvoice).join(ARPayment).filter(
                ARPaymentInvoice.invoice_id == invoice.id
            ).order_by(desc(ARPayment.payment_date)).first()
            
            if last_payment:
                days_to_collect = (last_payment.payment.payment_date - invoice.invoice_date).days
                total_days += days_to_collect
                count += 1
        
        return Decimal(str(total_days / count)) if count > 0 else None
    
    def _calculate_payment_success_rate(self) -> Optional[Decimal]:
        total_invoices = self.db.query(ARInvoice).filter(
            ARInvoice.status.in_(['sent', 'paid', 'partial_payment', 'overdue'])
        ).count()
        
        paid_invoices = self.db.query(ARInvoice).filter(
            ARInvoice.status.in_(['paid', 'partial_payment'])
        ).count()
        
        if total_invoices == 0:
            return None
        
        return Decimal(str((paid_invoices / total_invoices) * 100))
    
    def _get_top_customers_by_sales(self, limit: int = 5) -> List[Dict[str, Any]]:
        # Get top customers by total sales this year
        current_year = date.today().year
        
        results = self.db.query(
            Customer.id,
            Customer.name,
            func.sum(ARInvoice.total_amount).label('total_sales')
        ).join(ARInvoice).filter(
            func.extract('year', ARInvoice.invoice_date) == current_year
        ).group_by(Customer.id, Customer.name).order_by(
            desc('total_sales')
        ).limit(limit).all()
        
        return [
            {
                'customer_id': result.id,
                'customer_name': result.name,
                'total_sales': float(result.total_sales)
            }
            for result in results
        ]

# AI/ML Integration Services
class ARPredictionService:
    def __init__(self, db: Session):
        self.db = db
    
    def predict_payment_probability(self, invoice_id: int) -> Dict[str, Any]:
        """Predict probability of payment for an invoice"""
        invoice = self.db.query(ARInvoice).filter(ARInvoice.id == invoice_id).first()
        if not invoice:
            return {}
        
        # Simple rule-based prediction (replace with ML model)
        customer = invoice.customer
        
        # Factors affecting payment probability
        factors = []
        probability = 0.7  # Base probability
        
        # Customer payment history
        if customer.payment_behavior_score:
            if customer.payment_behavior_score > 80:
                probability += 0.2
                factors.append("Excellent payment history")
            elif customer.payment_behavior_score < 40:
                probability -= 0.3
                factors.append("Poor payment history")
        
        # Invoice amount vs credit limit
        if customer.credit_limit > 0:
            utilization = float(invoice.total_amount / customer.credit_limit)
            if utilization > 0.8:
                probability -= 0.2
                factors.append("High credit utilization")
        
        # Days overdue
        if invoice.is_overdue:
            days_overdue = invoice.days_overdue
            if days_overdue > 30:
                probability -= 0.4
                factors.append(f"{days_overdue} days overdue")
        
        # Customer status
        if customer.status == 'vip':
            probability += 0.1
            factors.append("VIP customer")
        elif customer.status == 'suspended':
            probability -= 0.5
            factors.append("Suspended customer")
        
        probability = max(0.0, min(1.0, probability))
        
        return {
            'invoice_id': invoice_id,
            'payment_probability': round(probability * 100, 1),
            'confidence_score': 0.75,
            'factors': factors,
            'predicted_payment_date': self._predict_payment_date(invoice, probability)
        }
    
    def predict_customer_churn(self, customer_id: int) -> Dict[str, Any]:
        """Predict customer churn probability"""
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return {}
        
        # Simple rule-based churn prediction
        churn_probability = 0.3  # Base probability
        risk_factors = []
        
        # Recent invoice activity
        recent_invoices = self.db.query(ARInvoice).filter(
            and_(
                ARInvoice.customer_id == customer_id,
                ARInvoice.invoice_date >= date.today() - timedelta(days=90)
            )
        ).count()
        
        if recent_invoices == 0:
            churn_probability += 0.4
            risk_factors.append("No recent activity")
        
        # Payment delays
        overdue_invoices = self.db.query(ARInvoice).filter(
            and_(
                ARInvoice.customer_id == customer_id,
                ARInvoice.due_date < date.today(),
                ARInvoice.balance_due > 0
            )
        ).count()
        
        if overdue_invoices > 0:
            churn_probability += 0.2
            risk_factors.append("Overdue payments")
        
        # Customer engagement
        if customer.churn_risk_score:
            if customer.churn_risk_score > 70:
                churn_probability += 0.3
                risk_factors.append("High churn risk score")
        
        churn_probability = min(1.0, churn_probability)
        
        risk_level = "Low"
        if churn_probability > 0.7:
            risk_level = "High"
        elif churn_probability > 0.4:
            risk_level = "Medium"
        
        return {
            'customer_id': customer_id,
            'churn_probability': round(churn_probability * 100, 1),
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'recommendations': self._get_churn_prevention_recommendations(churn_probability, risk_factors)
        }
    
    def _predict_payment_date(self, invoice: ARInvoice, probability: float) -> Optional[date]:
        """Predict when payment will be received"""
        if probability < 0.3:
            return None
        
        # Base prediction on customer payment terms and history
        customer = invoice.customer
        
        if customer.payment_terms == 'net30':
            base_days = 30
        elif customer.payment_terms == 'net15':
            base_days = 15
        else:
            base_days = 30
        
        # Adjust based on probability
        if probability > 0.8:
            adjustment = -5  # Pay early
        elif probability < 0.5:
            adjustment = 10  # Pay late
        else:
            adjustment = 0
        
        predicted_days = base_days + adjustment
        return invoice.invoice_date + timedelta(days=predicted_days)
    
    def _get_churn_prevention_recommendations(self, churn_probability: float, risk_factors: List[str]) -> List[str]:
        """Get recommendations to prevent customer churn"""
        recommendations = []
        
        if churn_probability > 0.7:
            recommendations.append("Schedule immediate customer outreach")
            recommendations.append("Offer payment plan or discount")
            recommendations.append("Assign dedicated account manager")
        
        if "No recent activity" in risk_factors:
            recommendations.append("Send promotional offers")
            recommendations.append("Schedule business review meeting")
        
        if "Overdue payments" in risk_factors:
            recommendations.append("Contact for payment arrangement")
            recommendations.append("Review credit terms")
        
        return recommendations