"""
Allocation rules engine for automatic transaction allocation.
"""
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from app.models.allocation import (
    AllocationRule, 
    AllocationRuleLine, 
    Allocation, 
    AllocationEntry,
    AllocationMethod,
    AllocationStatus
)
from app.models.journal_entry import JournalEntry, JournalEntryLine, JournalEntryStatus
from app.core.exceptions import NotFoundException, ValidationException


class AllocationEngine:
    """Engine for processing allocation rules and creating allocations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_allocation_rule(self, rule_data: Dict[str, Any], created_by: UUID) -> AllocationRule:
        """Create a new allocation rule."""
        if not rule_data.get('rule_code'):
            rule_data['rule_code'] = self._generate_rule_code()
        
        rule = AllocationRule(
            rule_name=rule_data['rule_name'],
            rule_code=rule_data['rule_code'],
            description=rule_data.get('description'),
            allocation_method=AllocationMethod(rule_data['allocation_method']),
            status=AllocationStatus(rule_data.get('status', AllocationStatus.ACTIVE)),
            source_account_id=rule_data.get('source_account_id'),
            effective_from=rule_data['effective_from'],
            effective_to=rule_data.get('effective_to'),
            priority=rule_data.get('priority', 100),
            created_by=created_by,
            updated_by=created_by
        )
        
        self.db.add(rule)
        self.db.flush()
        
        for line_data in rule_data.get('allocation_lines', []):
            line = AllocationRuleLine(
                allocation_rule_id=rule.id,
                target_account_id=line_data['target_account_id'],
                allocation_percentage=line_data.get('allocation_percentage'),
                fixed_amount=line_data.get('fixed_amount'),
                weight=line_data.get('weight'),
                line_order=line_data.get('line_order', 1),
                created_by=created_by,
                updated_by=created_by
            )
            self.db.add(line)
        
        self.db.commit()
        self.db.refresh(rule)
        
        return rule
    
    def process_allocation(self, journal_entry_id: UUID, created_by: UUID) -> Optional[Allocation]:
        """Process allocation for a journal entry based on matching rules."""
        journal_entry = self.db.query(JournalEntry).filter(
            JournalEntry.id == journal_entry_id
        ).first()
        
        if not journal_entry:
            raise NotFoundException(f"Journal entry {journal_entry_id} not found")
        
        matching_rules = self._find_matching_rules(journal_entry)
        
        if not matching_rules:
            return None
        
        rule = matching_rules[0]
        total_amount = sum(line.amount for line in journal_entry.lines if line.is_debit)
        
        if total_amount <= 0:
            return None
        
        allocation = Allocation(
            allocation_number=self._generate_allocation_number(),
            allocation_date=journal_entry.entry_date,
            source_journal_entry_id=journal_entry_id,
            source_amount=total_amount,
            allocation_rule_id=rule.id,
            description=f"Allocation based on rule: {rule.rule_name}",
            created_by=created_by,
            updated_by=created_by
        )
        
        self.db.add(allocation)
        self.db.flush()
        
        allocation_entries = self._create_allocation_entries(allocation, rule, total_amount, created_by)
        
        for entry in allocation_entries:
            je = self._create_allocation_journal_entry(entry, journal_entry, created_by)
            entry.journal_entry_id = je.id
        
        self.db.commit()
        self.db.refresh(allocation)
        
        return allocation
    
    def get_allocation_rules(self, skip: int = 0, limit: int = 100) -> List[AllocationRule]:
        """Get allocation rules."""
        return self.db.query(AllocationRule)\
                   .order_by(AllocationRule.priority, AllocationRule.rule_name)\
                   .offset(skip).limit(limit).all()
    
    def get_allocation_rule(self, rule_id: UUID) -> Optional[AllocationRule]:
        """Get an allocation rule by ID."""
        return self.db.query(AllocationRule).filter(
            AllocationRule.id == rule_id
        ).first()
    
    def _find_matching_rules(self, journal_entry: JournalEntry) -> List[AllocationRule]:
        """Find allocation rules that match a journal entry."""
        query = self.db.query(AllocationRule).filter(
            and_(
                AllocationRule.status == AllocationStatus.ACTIVE,
                AllocationRule.effective_from <= journal_entry.entry_date,
                or_(
                    AllocationRule.effective_to.is_(None),
                    AllocationRule.effective_to >= journal_entry.entry_date
                )
            )
        )
        
        return query.order_by(AllocationRule.priority).all()
    
    def _create_allocation_entries(
        self, 
        allocation: Allocation, 
        rule: AllocationRule, 
        total_amount: Decimal,
        created_by: UUID
    ) -> List[AllocationEntry]:
        """Create allocation entries based on the rule."""
        entries = []
        
        if rule.allocation_method == AllocationMethod.PERCENTAGE:
            entries = self._allocate_by_percentage(allocation, rule, total_amount, created_by)
        elif rule.allocation_method == AllocationMethod.EQUAL:
            entries = self._allocate_equally(allocation, rule, total_amount, created_by)
        
        return entries
    
    def _allocate_by_percentage(
        self, 
        allocation: Allocation, 
        rule: AllocationRule, 
        total_amount: Decimal,
        created_by: UUID
    ) -> List[AllocationEntry]:
        """Allocate amount based on percentages."""
        entries = []
        
        for line in rule.allocation_lines:
            if line.allocation_percentage:
                allocated_amount = (total_amount * line.allocation_percentage / 100).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP
                )
                
                entry = AllocationEntry(
                    allocation_id=allocation.id,
                    target_account_id=line.target_account_id,
                    allocated_amount=allocated_amount,
                    allocation_percentage=line.allocation_percentage,
                    description=f"Allocation {line.allocation_percentage}% of {total_amount}",
                    created_by=created_by,
                    updated_by=created_by
                )
                
                self.db.add(entry)
                entries.append(entry)
        
        return entries
    
    def _allocate_equally(
        self, 
        allocation: Allocation, 
        rule: AllocationRule, 
        total_amount: Decimal,
        created_by: UUID
    ) -> List[AllocationEntry]:
        """Allocate amount equally among targets."""
        entries = []
        line_count = len(rule.allocation_lines)
        
        if line_count == 0:
            return entries
        
        amount_per_line = (total_amount / line_count).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        for line in rule.allocation_lines:
            entry = AllocationEntry(
                allocation_id=allocation.id,
                target_account_id=line.target_account_id,
                allocated_amount=amount_per_line,
                allocation_percentage=Decimal('100') / line_count,
                description=f"Equal allocation of {amount_per_line}",
                created_by=created_by,
                updated_by=created_by
            )
            
            self.db.add(entry)
            entries.append(entry)
        
        return entries
    
    def _create_allocation_journal_entry(
        self, 
        allocation_entry: AllocationEntry, 
        source_je: JournalEntry,
        created_by: UUID
    ) -> JournalEntry:
        """Create a journal entry for an allocation entry."""
        je = JournalEntry(
            entry_number=f"ALLOC-{allocation_entry.allocation.allocation_number}",
            entry_date=allocation_entry.allocation.allocation_date,
            description=f"Allocation: {allocation_entry.description}",
            reference=source_je.reference,
            status=JournalEntryStatus.POSTED,
            created_by=created_by,
            updated_by=created_by
        )
        
        self.db.add(je)
        self.db.flush()
        
        debit_line = JournalEntryLine(
            journal_entry_id=je.id,
            account_id=allocation_entry.target_account_id,
            description=allocation_entry.description,
            amount=allocation_entry.allocated_amount,
            is_debit=True,
            created_by=created_by,
            updated_by=created_by
        )
        
        source_account_id = source_je.lines[0].account_id
        credit_line = JournalEntryLine(
            journal_entry_id=je.id,
            account_id=source_account_id,
            description=f"Allocation from {allocation_entry.description}",
            amount=allocation_entry.allocated_amount,
            is_debit=False,
            created_by=created_by,
            updated_by=created_by
        )
        
        self.db.add(debit_line)
        self.db.add(credit_line)
        
        return je
    
    def _generate_rule_code(self) -> str:
        """Generate a unique rule code."""
        last_rule = self.db.query(AllocationRule)\
            .order_by(desc(AllocationRule.created_at))\
            .first()
        
        if last_rule and last_rule.rule_code.startswith('AR'):
            try:
                last_num = int(last_rule.rule_code.split('-')[1])
                next_num = last_num + 1
            except (IndexError, ValueError):
                next_num = 1
        else:
            next_num = 1
        
        return f"AR-{next_num:04d}"
    
    def _generate_allocation_number(self) -> str:
        """Generate a unique allocation number."""
        last_allocation = self.db.query(Allocation)\
            .order_by(desc(Allocation.created_at))\
            .first()
        
        if last_allocation and last_allocation.allocation_number.startswith('ALLOC'):
            try:
                last_num = int(last_allocation.allocation_number.split('-')[1])
                next_num = last_num + 1
            except (IndexError, ValueError):
                next_num = 1
        else:
            next_num = 1
        
        return f"ALLOC-{next_num:06d}"