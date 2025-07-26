from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, List
from datetime import datetime
from decimal import Decimal

class WorkflowIntegrationService:
    """Service for integrated workflows across modules"""
    
    async def process_purchase_to_payment_workflow(self, db: AsyncSession, purchase_data: dict, user_id: int):
        """Complete purchase-to-payment workflow across AP and Cash modules"""
        from ..core_financials.accounts_payable.services.vendor_service import VendorService
        from ..core_financials.accounts_payable.services.bill_service import BillService
        from ..core_financials.accounts_payable.services.payment_service import PaymentService
        from .cross_module_service import CrossModuleIntegrationService
        
        workflow_results = []
        
        # Step 1: Create/validate vendor
        vendor_service = VendorService()
        if purchase_data.get("vendor_id"):
            vendor = await vendor_service.get_vendor(db, purchase_data["vendor_id"])
        else:
            vendor = await vendor_service.create_vendor(db, purchase_data["vendor_data"], user_id)
            workflow_results.append({"step": "vendor_created", "vendor_id": vendor["id"]})
        
        # Step 2: Create bill
        bill_service = BillService()
        bill_data = {
            "vendor_id": vendor["id"] if isinstance(vendor, dict) else vendor.id,
            "bill_number": purchase_data["bill_number"],
            "bill_date": purchase_data["bill_date"],
            "due_date": purchase_data["due_date"],
            "total_amount": purchase_data["total_amount"],
            "line_items": purchase_data.get("line_items", [])
        }
        bill = await bill_service.create_bill(db, bill_data, user_id)
        workflow_results.append({"step": "bill_created", "bill_id": bill["id"]})
        
        # Step 3: Auto-approve if under threshold
        if float(purchase_data["total_amount"]) < 1000:
            approval = await bill_service.approve_bill(db, bill["id"], {"notes": "Auto-approved under threshold"}, user_id)
            workflow_results.append({"step": "bill_approved", "approval_id": approval["id"]})
            
            # Step 4: Create payment
            payment_service = PaymentService()
            payment_data = {
                "bill_id": bill["id"],
                "payment_date": purchase_data.get("payment_date", datetime.now().strftime("%Y-%m-%d")),
                "payment_method": purchase_data.get("payment_method", "check"),
                "bank_account_id": purchase_data["bank_account_id"]
            }
            payment = await payment_service.create_payment(db, payment_data, user_id)
            workflow_results.append({"step": "payment_created", "payment_id": payment["id"]})
            
            # Step 5: Sync to cash management
            integration_service = CrossModuleIntegrationService()
            sync_result = await integration_service.sync_ap_to_cash_management(db, payment["id"])
            workflow_results.append({"step": "cash_sync", "result": sync_result})
        
        return {
            "workflow_id": f"P2P-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "status": "completed" if len(workflow_results) >= 4 else "pending_approval",
            "steps_completed": len(workflow_results),
            "workflow_results": workflow_results,
            "total_amount": float(purchase_data["total_amount"]),
            "created_by": user_id
        }
    
    async def process_invoice_to_cash_workflow(self, db: AsyncSession, invoice_data: dict, user_id: int):
        """Complete invoice-to-cash workflow across AR and Cash modules"""
        from ..core_financials.accounts_receivable.services.customer_service import CustomerService
        from ..core_financials.accounts_receivable.services.invoice_service import InvoiceService
        from .cross_module_service import CrossModuleIntegrationService
        
        workflow_results = []
        
        # Step 1: Validate customer
        customer_service = CustomerService()
        customer = await customer_service.get_customer(db, invoice_data["customer_id"])
        if not customer:
            return {"error": "Customer not found"}
        
        # Step 2: Check credit limit
        if customer["credit_hold"]:
            return {"error": "Customer on credit hold"}
        
        outstanding = customer["outstanding_balance"]
        new_total = outstanding + float(invoice_data["total_amount"])
        if new_total > customer["credit_limit"]:
            return {"error": "Credit limit exceeded"}
        
        workflow_results.append({"step": "credit_check_passed", "available_credit": customer["credit_limit"] - new_total})
        
        # Step 3: Create invoice
        invoice_service = InvoiceService()
        invoice = await invoice_service.create_invoice(db, invoice_data, user_id)
        workflow_results.append({"step": "invoice_created", "invoice_id": invoice["id"]})
        
        # Step 4: Send invoice
        send_result = await invoice_service.send_invoice(db, invoice["id"], {"email": customer["email"]}, user_id)
        workflow_results.append({"step": "invoice_sent", "sent_date": send_result["sent_date"]})
        
        return {
            "workflow_id": f"I2C-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "status": "invoice_sent",
            "steps_completed": len(workflow_results),
            "workflow_results": workflow_results,
            "invoice_id": invoice["id"],
            "customer_id": customer["id"],
            "total_amount": float(invoice_data["total_amount"]),
            "created_by": user_id
        }
    
    async def process_budget_to_actual_workflow(self, db: AsyncSession, budget_id: int, user_id: int):
        """Process budget to actual tracking workflow"""
        from ..core_financials.budget.services.budget_integration_service import BudgetIntegrationService
        from ..core_financials.budget.services.budget_monitoring_service import BudgetMonitoringService
        
        workflow_results = []
        
        # Step 1: Sync actuals from GL
        integration_service = BudgetIntegrationService()
        sync_result = await integration_service.sync_actuals_from_gl(db, budget_id, datetime.now().date())
        workflow_results.append({"step": "actuals_synced", "synced_records": sync_result["synced_records"]})
        
        # Step 2: Calculate variance
        variance_result = await integration_service.generate_budget_to_actual_report(db, budget_id, datetime.now().date())
        workflow_results.append({"step": "variance_calculated", "total_variance": variance_result["executive_summary"]["total_variance"]})
        
        # Step 3: Check for alerts
        monitoring_service = BudgetMonitoringService()
        if abs(variance_result["executive_summary"]["variance_percentage"]) > 15:
            alert_data = {
                "budget_id": budget_id,
                "alert_type": "variance",
                "severity": "high",
                "title": "Budget Variance Alert",
                "message": f"Budget variance of {variance_result['executive_summary']['variance_percentage']:.1f}% detected",
                "current_percentage": variance_result["executive_summary"]["variance_percentage"]
            }
            alert = await monitoring_service.create_budget_alert(db, alert_data, user_id)
            workflow_results.append({"step": "alert_created", "alert_id": alert["alert_id"]})
        
        return {
            "workflow_id": f"B2A-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "status": "completed",
            "steps_completed": len(workflow_results),
            "workflow_results": workflow_results,
            "budget_id": budget_id,
            "variance_percentage": variance_result["executive_summary"]["variance_percentage"],
            "created_by": user_id
        }