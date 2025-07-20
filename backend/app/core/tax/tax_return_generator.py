from datetime import date, datetime
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app import crud, models
from app.core.tax.tax_calculator import TaxCalculator
from app.models.tax_return import TaxReturn, TaxReturnLineItem
from app.schemas.tax_return import (
    TaxReturn as TaxReturnSchema,
    TaxReturnLineItem as TaxReturnLineItemSchema,
    TaxReturnStatus,
)
from app.services.document_generation import PDFGenerator


class TaxReturnGenerator:
    """
    Service for generating tax returns based on transaction data and tax rules.
    """

    def __init__(self, db: Session, company_id: UUID, user_id: UUID):
        self.db = db
        self.company_id = company_id
        self.user_id = user_id
        self.tax_calculator = TaxCalculator(db, company_id)

    async def generate_tax_return(
        self,
        return_type: str,
        tax_period_start: date,
        tax_period_end: date,
        jurisdiction_code: str,
        filing_frequency: str = "monthly",
        force_recalculation: bool = False,
    ) -> TaxReturn:
        """
        Generate a tax return for the specified period and jurisdiction.

        Args:
            return_type: Type of tax return (e.g., 'vat', 'gst', 'income_tax')
            tax_period_start: Start date of the tax period
            tax_period_end: End date of the tax period
            jurisdiction_code: Tax jurisdiction code
            filing_frequency: Filing frequency (monthly, quarterly, etc.)
            force_recalculation: If True, recalculate even if a return exists

        Returns:
            The generated or existing tax return
        """
        # Check if a return already exists for this period
        existing_return = crud.tax_return.get_by_period(
            self.db,
            company_id=self.company_id,
            return_type=return_type,
            jurisdiction_code=jurisdiction_code,
            period_start=tax_period_start,
            period_end=tax_period_end,
        )

        if existing_return and not force_recalculation:
            return existing_return

        # Get transactions for the tax period
        transactions = self._get_taxable_transactions(
            tax_period_start, tax_period_end, jurisdiction_code, return_type
        )

        # Calculate tax liabilities
        tax_summary = self.tax_calculator.calculate_tax_liabilities(
            transactions, jurisdiction_code, return_type
        )

        # Create tax return line items
        line_items = self._create_line_items(tax_summary, return_type)

        # Calculate total amounts
        total_taxable_amount = self._sum_amounts(
            [item.amount for item in line_items if item.amount]
        )
        total_tax_amount = self._sum_amounts(
            [item.tax_amount for item in line_items if item.tax_amount]
        )

        # Create or update tax return
        tax_return_data = {
            "company_id": self.company_id,
            "return_type": return_type,
            "filing_frequency": filing_frequency,
            "tax_period_start": tax_period_start,
            "tax_period_end": tax_period_end,
            "due_date": self._calculate_due_date(tax_period_end, jurisdiction_code, filing_frequency),
            "jurisdiction_code": jurisdiction_code,
            "status": TaxReturnStatus.DRAFT,
            "total_taxable_amount": total_taxable_amount,
            "total_tax_amount": total_tax_amount,
            "total_paid_amount": {},
            "total_due_amount": total_tax_amount,  # Initially due amount equals tax amount
            "created_by": self.user_id,
        }

        if existing_return:
            tax_return = crud.tax_return.update(
                self.db, db_obj=existing_return, obj_in=tax_return_data
            )
            # Delete existing line items to replace them with new ones
            crud.tax_return_line_item.remove_by_tax_return(
                self.db, tax_return_id=existing_return.id
            )
        else:
            tax_return = crud.tax_return.create(self.db, obj_in=tax_return_data)

        # Add line items to the tax return
        for item in line_items:
            crud.tax_return_line_item.create_with_tax_return(
                self.db, obj_in=item, tax_return_id=tax_return.id
            )

        return tax_return

    async def generate_tax_return_pdf(
        self, tax_return_id: UUID, include_attachments: bool = False
    ) -> bytes:
        """
        Generate a PDF version of a tax return.

        Args:
            tax_return_id: ID of the tax return
            include_attachments: Whether to include attachments in the PDF

        Returns:
            PDF content as bytes
        """
        tax_return = crud.tax_return.get(self.db, id=tax_return_id)
        if not tax_return:
            raise ValueError(f"Tax return with ID {tax_return_id} not found")

        line_items = crud.tax_return_line_item.get_by_tax_return(
            self.db, tax_return_id=tax_return_id
        )

        # Prepare data for PDF generation
        context = {
            "tax_return": tax_return,
            "line_items": line_items,
            "company": crud.company.get(self.db, id=tax_return.company_id),
            "generated_at": datetime.utcnow(),
        }

        if include_attachments:
            attachments = crud.tax_return_attachment.get_by_tax_return(
                self.db, tax_return_id=tax_return_id
            )
            context["attachments"] = attachments

        # Generate PDF
        pdf_generator = PDFGenerator()
        pdf_content = pdf_generator.generate_pdf(
            template_name="tax_return.html", context=context
        )

        return pdf_content

    def _get_taxable_transactions(
        self,
        period_start: date,
        period_end: date,
        jurisdiction_code: str,
        return_type: str,
    ) -> List[Dict]:
        """
        Retrieve transactions that are subject to the specified tax type.
        
        Args:
            period_start: Start of the tax period
            period_end: End of the tax period
            jurisdiction_code: Tax jurisdiction code
            return_type: Type of tax return
            
        Returns:
            List of transactions with tax details
        """
        # Get transactions from AR/AP/GL modules
        # This is a simplified example - in a real implementation, you would
        # query the appropriate modules for taxable transactions
        transactions = []
        
        # Example: Get AR invoices with tax
        ar_invoices = crud.ar_invoice.get_taxable_invoices(
            self.db,
            company_id=self.company_id,
            start_date=period_start,
            end_date=period_end,
            jurisdiction_code=jurisdiction_code,
            tax_type=return_type,
        )
        transactions.extend(ar_invoices)
        
        # Example: Get AP bills with tax
        ap_bills = crud.ap_bill.get_taxable_bills(
            self.db,
            company_id=self.company_id,
            start_date=period_start,
            end_date=period_end,
            jurisdiction_code=jurisdiction_code,
            tax_type=return_type,
        )
        transactions.extend(ap_bills)
        
        # Add GL transactions with tax implications if needed
        gl_transactions = crud.gl_transaction.get_taxable_transactions(
            self.db,
            company_id=self.company_id,
            start_date=period_start,
            end_date=period_end,
            tax_type=return_type,
        )
        transactions.extend(gl_transactions)
        
        return transactions

    def _create_line_items(
        self, tax_summary: Dict, return_type: str
    ) -> List[TaxReturnLineItemSchema]:
        """
        Create tax return line items from tax calculation results.
        
        Args:
            tax_summary: Tax calculation results from TaxCalculator
            return_type: Type of tax return
            
        Returns:
            List of tax return line items
        """
        line_items = []
        
        # Add line items for each tax rate/category
        for rate, details in tax_summary.get("rates", {}).items():
            line_item = TaxReturnLineItemSchema(
                line_item_code=f"TAX_RATE_{rate}",
                description=f"Tax at {rate}% - {details.get('description', 'Standard Rate')}",
                amount=details.get("taxable_amount", {}),
                tax_type=return_type.upper(),
                tax_rate={"rate": float(rate), "type": "percentage"},
                tax_amount=details.get("tax_amount", {}),
            )
            line_items.append(line_item)
        
        # Add summary line items
        if "totals" in tax_summary:
            totals = tax_summary["totals"]
            if "taxable_amount" in totals:
                line_items.append(
                    TaxReturnLineItemSchema(
                        line_item_code="TOTAL_TAXABLE",
                        description="Total Taxable Amount",
                        amount=totals["taxable_amount"],
                    )
                )
            
            if "tax_amount" in totals:
                line_items.append(
                    TaxReturnLineItemSchema(
                        line_item_code="TOTAL_TAX",
                        description="Total Tax Due",
                        amount=totals["tax_amount"],
                        tax_type=return_type.upper(),
                    )
                )
        
        return line_items

    def _sum_amounts(self, amount_dicts: List[Dict[str, float]]) -> Dict[str, float]:
        """
        Sum multiple amount dictionaries by currency.
        
        Args:
            amount_dicts: List of amount dictionaries {currency: amount}
            
        Returns:
            Dictionary of summed amounts by currency
        """
        result = {}
        for amount_dict in amount_dicts:
            if not amount_dict:
                continue
                
            for currency, amount in amount_dict.items():
                if currency not in result:
                    result[currency] = 0.0
                result[currency] += amount
                
        return result

    def _calculate_due_date(
        self, period_end: date, jurisdiction_code: str, filing_frequency: str
    ) -> date:
        """
        Calculate the due date for a tax return based on jurisdiction rules.
        
        Args:
            period_end: End date of the tax period
            jurisdiction_code: Tax jurisdiction code
            filing_frequency: Filing frequency (monthly, quarterly, etc.)
            
        Returns:
            Due date for the tax return
        """
        # Get jurisdiction-specific rules
        jurisdiction = crud.tax_jurisdiction.get_by_code(
            self.db, code=jurisdiction_code, company_id=self.company_id
        )
        
        if not jurisdiction:
            # Default to 30 days after period end if no jurisdiction rules found
            return period_end + timedelta(days=30)
            
        # Get due date rules for this filing frequency
        due_date_rules = jurisdiction.due_date_rules or {}
        rule = due_date_rules.get(filing_frequency, {})
        
        if not rule:
            # Default to 30 days after period end if no specific rule
            return period_end + timedelta(days=30)
            
        # Apply the rule (example: "days_after_period_end" or "day_of_month_after_period")
        if "days_after_period_end" in rule:
            return period_end + timedelta(days=rule["days_after_period_end"])
        elif "day_of_month_after_period" in rule:
            day = rule["day_of_month_after_period"]
            # Calculate the next occurrence of the specified day after period end
            next_month = period_end.replace(day=28) + timedelta(days=4)  # Move to next month
            return next_month.replace(day=min(day, 28))  # Handle months with fewer days
        
        # Default fallback
        return period_end + timedelta(days=30)
