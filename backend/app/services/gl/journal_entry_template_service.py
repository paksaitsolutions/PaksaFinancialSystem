"""
Journal Entry Template Service.
"""
from typing import List, Dict, Any, Optional
from decimal import Decimal
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.journal_entry_template import JournalEntryTemplate, JournalEntryTemplateLine
from app.models.journal_entry import JournalEntry, JournalEntryLine, JournalEntryStatus
from app.core.exceptions import NotFoundException, ValidationException


class JournalEntryTemplateService:
    """Service for managing journal entry templates."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_template(self, template_data: Dict[str, Any], created_by: UUID) -> JournalEntryTemplate:
        """Create a new journal entry template."""
        template = JournalEntryTemplate(
            template_name=template_data['template_name'],
            template_code=template_data['template_code'],
            description=template_data.get('description'),
            category=template_data.get('category'),
            created_by=created_by,
            updated_by=created_by
        )
        
        self.db.add(template)
        self.db.flush()
        
        for line_data in template_data.get('lines', []):
            line = JournalEntryTemplateLine(
                template_id=template.id,
                account_id=line_data['account_id'],
                description=line_data.get('description'),
                is_debit=line_data['is_debit'],
                amount_formula=line_data.get('amount_formula'),
                line_order=line_data.get('line_order', 1),
                created_by=created_by,
                updated_by=created_by
            )
            self.db.add(line)
        
        self.db.commit()
        self.db.refresh(template)
        return template
    
    def create_entry_from_template(
        self,
        template_id: UUID,
        entry_data: Dict[str, Any],
        created_by: UUID
    ) -> JournalEntry:
        """Create a journal entry from a template."""
        template = self.db.query(JournalEntryTemplate).filter(
            JournalEntryTemplate.id == template_id
        ).first()
        
        if not template:
            raise NotFoundException(f"Template {template_id} not found")
        
        if not template.is_active:
            raise ValidationException("Template is inactive")
        
        je = JournalEntry(
            entry_number=entry_data.get('entry_number', f"JE-{template.template_code}"),
            entry_date=entry_data['entry_date'],
            description=entry_data.get('description', template.description),
            reference=entry_data.get('reference'),
            status=JournalEntryStatus.DRAFT,
            created_by=created_by,
            updated_by=created_by
        )
        
        self.db.add(je)
        self.db.flush()
        
        context = entry_data.get('context', {})
        
        for template_line in template.template_lines:
            amount = self._evaluate_amount(template_line.amount_formula, context)
            
            line = JournalEntryLine(
                journal_entry_id=je.id,
                account_id=template_line.account_id,
                description=template_line.description,
                amount=amount,
                is_debit=template_line.is_debit,
                created_by=created_by,
                updated_by=created_by
            )
            self.db.add(line)
        
        self.db.commit()
        self.db.refresh(je)
        return je
    
    def get_templates(self, skip: int = 0, limit: int = 100) -> List[JournalEntryTemplate]:
        """Get all templates."""
        return self.db.query(JournalEntryTemplate)\
            .filter(JournalEntryTemplate.is_active == True)\
            .offset(skip).limit(limit).all()
    
    def _evaluate_amount(self, formula: Optional[str], context: Dict[str, Any]) -> Decimal:
        """Evaluate amount formula."""
        if not formula:
            return Decimal('0')
        
        try:
            result = eval(formula, {"__builtins__": {}}, context)
            return Decimal(str(result))
        except Exception as e:
            raise ValidationException(f"Formula evaluation failed: {str(e)}")
