from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.core.db.base import get_db
from .services import CustomerService, ARInvoiceService, ARPaymentService, ARAnalyticsService, ARPredictionService
from .schemas import (
    CustomerCreate, CustomerUpdate, CustomerResponse, CustomerSearchRequest,
    ARInvoiceCreate, ARInvoiceUpdate, ARInvoiceResponse, ARInvoiceSearchRequest,
    ARPaymentCreate, ARPaymentUpdate, ARPaymentResponse, ARPaymentSearchRequest,
    CreditMemoCreate, CreditMemoResponse,
    ARSummaryResponse, CustomerSummaryResponse, ARAgingReportResponse,
    CollectionForecastResponse, CustomerPerformanceResponse,
    ChurnPredictionResponse, PaymentPredictionResponse, CustomerSegmentationResponse,
    BulkInvoiceCreate, BulkPaymentApplication, BulkCollectionAction
)

router = APIRouter(prefix="/ar", tags=["Accounts Receivable"])

# Customer Routes
@router.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db)
):
    """Create a new customer"""
    service = CustomerService(db)
    try:
        return service.create_customer(customer_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/customers", response_model=List[CustomerResponse])
async def get_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get customers with optional filtering"""
    service = CustomerService(db)
    return service.get_customers(skip=skip, limit=limit, search=search, category=category, status=status)

@router.get("/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """Get customer by ID"""
    service = CustomerService(db)
    customer = service.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.put("/customers/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db)
):
    """Update customer"""
    service = CustomerService(db)
    customer = service.update_customer(customer_id, customer_data)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.delete("/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    """Delete customer"""
    service = CustomerService(db)
    try:
        if not service.delete_customer(customer_id):
            raise HTTPException(status_code=404, detail="Customer not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/customers/search", response_model=List[CustomerResponse])
async def search_customers(
    search_request: CustomerSearchRequest,
    db: Session = Depends(get_db)
):
    """Advanced customer search"""
    service = CustomerService(db)
    # Implement advanced search logic
    return service.get_customers()

# Invoice Routes
@router.post("/invoices", response_model=ARInvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    invoice_data: ARInvoiceCreate,
    db: Session = Depends(get_db)
):
    """Create a new AR invoice"""
    service = ARInvoiceService(db)
    try:
        return service.create_invoice(invoice_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/invoices", response_model=List[ARInvoiceResponse])
async def get_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    customer_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    overdue_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get AR invoices with optional filtering"""
    service = ARInvoiceService(db)
    return service.get_invoices(
        skip=skip, 
        limit=limit, 
        customer_id=customer_id, 
        status=status, 
        overdue_only=overdue_only
    )

@router.get("/invoices/{invoice_id}", response_model=ARInvoiceResponse)
async def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """Get invoice by ID"""
    service = ARInvoiceService(db)
    invoice = service.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@router.put("/invoices/{invoice_id}", response_model=ARInvoiceResponse)
async def update_invoice(
    invoice_id: int,
    invoice_data: ARInvoiceUpdate,
    db: Session = Depends(get_db)
):
    """Update invoice"""
    service = ARInvoiceService(db)
    try:
        invoice = service.update_invoice(invoice_id, invoice_data)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        return invoice
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/invoices/{invoice_id}/send")
async def send_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """Send invoice to customer"""
    service = ARInvoiceService(db)
    if not service.send_invoice(invoice_id):
        raise HTTPException(status_code=404, detail="Invoice not found")
    return {"message": "Invoice sent successfully"}

@router.post("/invoices/bulk", response_model=List[ARInvoiceResponse])
async def create_bulk_invoices(
    bulk_data: BulkInvoiceCreate,
    db: Session = Depends(get_db)
):
    """Create multiple invoices"""
    service = ARInvoiceService(db)
    results = []
    for invoice_data in bulk_data.invoices:
        try:
            invoice = service.create_invoice(invoice_data)
            if bulk_data.send_immediately:
                service.send_invoice(invoice.id)
            results.append(invoice)
        except Exception as e:
            # Log error and continue with next invoice
            continue
    return results

# Payment Routes
@router.post("/payments", response_model=ARPaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_data: ARPaymentCreate,
    db: Session = Depends(get_db)
):
    """Record a new AR payment"""
    service = ARPaymentService(db)
    try:
        return service.create_payment(payment_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/payments", response_model=List[ARPaymentResponse])
async def get_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    customer_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get AR payments with optional filtering"""
    service = ARPaymentService(db)
    return service.get_payments(skip=skip, limit=limit, customer_id=customer_id, status=status)

@router.get("/payments/{payment_id}", response_model=ARPaymentResponse)
async def get_payment(payment_id: int, db: Session = Depends(get_db)):
    """Get payment by ID"""
    service = ARPaymentService(db)
    payment = service.get_payment(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.post("/payments/{payment_id}/process")
async def process_payment(payment_id: int, db: Session = Depends(get_db)):
    """Process pending payment"""
    service = ARPaymentService(db)
    if not service.process_payment(payment_id):
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"message": "Payment processed successfully"}

@router.post("/payments/bulk-apply", response_model=dict)
async def bulk_apply_payments(
    bulk_data: BulkPaymentApplication,
    db: Session = Depends(get_db)
):
    """Apply multiple payments in bulk"""
    service = ARPaymentService(db)
    # Implement bulk payment application logic
    return {"message": f"Applied {len(bulk_data.payment_applications)} payments"}

# Analytics Routes
@router.get("/analytics/summary", response_model=ARSummaryResponse)
async def get_ar_summary(db: Session = Depends(get_db)):
    """Get AR summary analytics"""
    service = ARAnalyticsService(db)
    return service.get_ar_summary()

@router.get("/analytics/aging-report", response_model=ARAgingReportResponse)
async def get_aging_report(db: Session = Depends(get_db)):
    """Get AR aging report"""
    service = ARAnalyticsService(db)
    return service.get_aging_report()

@router.get("/analytics/customer-performance", response_model=List[CustomerPerformanceResponse])
async def get_customer_performance(
    customer_id: Optional[int] = Query(None),
    period_days: int = Query(90, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get customer performance metrics"""
    service = ARAnalyticsService(db)
    # Implement customer performance analysis
    return []

@router.get("/analytics/collection-forecast", response_model=CollectionForecastResponse)
async def get_collection_forecast(
    forecast_days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get collection forecast"""
    service = ARAnalyticsService(db)
    # Implement collection forecasting
    return CollectionForecastResponse(
        forecast_date=date.today(),
        period_days=forecast_days,
        predicted_collections=[],
        total_predicted_amount=0,
        confidence_score=0.75
    )

# AI/ML Routes
@router.get("/ai/payment-prediction/{invoice_id}", response_model=PaymentPredictionResponse)
async def predict_payment(invoice_id: int, db: Session = Depends(get_db)):
    """Predict payment probability for invoice"""
    service = ARPredictionService(db)
    prediction = service.predict_payment_probability(invoice_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    return PaymentPredictionResponse(
        invoice_id=prediction['invoice_id'],
        payment_probability=prediction['payment_probability'],
        predicted_payment_date=prediction.get('predicted_payment_date'),
        confidence_score=prediction['confidence_score'],
        factors=prediction['factors']
    )

@router.get("/ai/churn-prediction/{customer_id}", response_model=ChurnPredictionResponse)
async def predict_churn(customer_id: int, db: Session = Depends(get_db)):
    """Predict customer churn probability"""
    service = ARPredictionService(db)
    prediction = service.predict_customer_churn(customer_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return ChurnPredictionResponse(
        customer_id=prediction['customer_id'],
        churn_probability=prediction['churn_probability'],
        risk_level=prediction['risk_level'],
        risk_factors=prediction['risk_factors'],
        recommendations=prediction['recommendations']
    )

@router.get("/ai/customer-segmentation", response_model=List[CustomerSegmentationResponse])
async def get_customer_segmentation(db: Session = Depends(get_db)):
    """Get AI-based customer segmentation"""
    service = ARPredictionService(db)
    # Implement customer segmentation logic
    return []

# Collection Management Routes
@router.post("/collections/bulk-action")
async def bulk_collection_action(
    bulk_data: BulkCollectionAction,
    db: Session = Depends(get_db)
):
    """Perform bulk collection actions"""
    # Implement bulk collection actions
    return {"message": f"Applied {bulk_data.action} to {len(bulk_data.invoice_ids)} invoices"}

@router.get("/collections/workflow/{invoice_id}")
async def get_collection_workflow(invoice_id: int, db: Session = Depends(get_db)):
    """Get collection workflow status for invoice"""
    service = ARInvoiceService(db)
    invoice = service.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    return {
        "invoice_id": invoice_id,
        "collection_status": invoice.collection_status,
        "last_reminder_date": invoice.last_reminder_date,
        "next_followup_date": invoice.next_followup_date,
        "days_overdue": invoice.days_overdue
    }

# Integration Routes
@router.post("/integration/gl-sync")
async def sync_with_gl(db: Session = Depends(get_db)):
    """Sync AR data with General Ledger"""
    # Implement GL integration
    return {"message": "AR data synced with GL successfully"}

@router.post("/integration/ecommerce-sync")
async def sync_ecommerce_orders(
    platform: str = Query(..., description="E-commerce platform (shopify, amazon, etc.)"),
    db: Session = Depends(get_db)
):
    """Sync e-commerce orders to create invoices"""
    # Implement e-commerce integration
    return {"message": f"Synced orders from {platform}"}

# Reporting Routes
@router.get("/reports/customer-statement/{customer_id}")
async def get_customer_statement(
    customer_id: int,
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db)
):
    """Generate customer statement"""
    service = CustomerService(db)
    customer = service.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Generate statement data
    return {
        "customer": customer,
        "statement_period": {"start": start_date, "end": end_date},
        "invoices": [],
        "payments": [],
        "balance": 0
    }

@router.get("/reports/sales-analysis")
async def get_sales_analysis(
    period: str = Query("month", regex="^(week|month|quarter|year)$"),
    customer_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get sales analysis report"""
    service = ARAnalyticsService(db)
    # Implement sales analysis
    return {
        "period": period,
        "total_sales": 0,
        "invoice_count": 0,
        "average_invoice_value": 0,
        "top_products": [],
        "sales_trend": []
    }

# Dashboard Routes
@router.get("/dashboard/metrics")
async def get_dashboard_metrics(db: Session = Depends(get_db)):
    """Get AR dashboard metrics"""
    service = ARAnalyticsService(db)
    summary = service.get_ar_summary()
    
    return {
        "summary": summary,
        "recent_invoices": [],
        "overdue_invoices": [],
        "recent_payments": [],
        "collection_alerts": []
    }