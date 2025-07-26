from typing import Dict, List, Optional, Any
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from .models import TaxAuditTrail, TaxReturn, TaxCalculation
from .schemas import AuditTrailEntry, AuditTrailQuery, AuditTrailSummary

class TaxAuditTrailService:
    """Service for comprehensive tax audit trail management"""
    
    # Action types for audit logging
    ACTION_TYPES = {
        'CREATE': 'Record Created',
        'UPDATE': 'Record Updated', 
        'DELETE': 'Record Deleted',
        'CALCULATE': 'Tax Calculated',
        'FILE': 'Return Filed',
        'PAYMENT': 'Payment Made',
        'ADJUSTMENT': 'Adjustment Made',
        'REVIEW': 'Record Reviewed',
        'APPROVE': 'Record Approved',
        'REJECT': 'Record Rejected'
    }
    
    async def log_audit_event(
        self,
        db: AsyncSession,
        entity_type: str,
        entity_id: int,
        action: str,
        user_id: int,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
        notes: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> TaxAuditTrail:
        """Log an audit event"""
        
        audit_entry = TaxAuditTrail(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            user_id=user_id,
            old_values=old_values,
            new_values=new_values,
            notes=notes,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow()
        )
        
        db.add(audit_entry)
        await db.commit()
        await db.refresh(audit_entry)
        
        return audit_entry
    
    async def get_audit_trail(
        self,
        db: AsyncSession,
        query: AuditTrailQuery
    ) -> List[AuditTrailEntry]:
        """Get audit trail entries based on query parameters"""
        
        # Build base query
        base_query = select(TaxAuditTrail)
        
        # Apply filters
        conditions = []
        
        if query.entity_type:
            conditions.append(TaxAuditTrail.entity_type == query.entity_type)
        
        if query.entity_id:
            conditions.append(TaxAuditTrail.entity_id == query.entity_id)
        
        if query.user_id:
            conditions.append(TaxAuditTrail.user_id == query.user_id)
        
        if query.action:
            conditions.append(TaxAuditTrail.action == query.action)
        
        if query.start_date:
            conditions.append(TaxAuditTrail.timestamp >= query.start_date)
        
        if query.end_date:
            conditions.append(TaxAuditTrail.timestamp <= query.end_date)
        
        if conditions:
            base_query = base_query.where(and_(*conditions))
        
        # Apply ordering
        base_query = base_query.order_by(desc(TaxAuditTrail.timestamp))
        
        # Apply pagination
        if query.limit:
            base_query = base_query.limit(query.limit)
        
        if query.offset:
            base_query = base_query.offset(query.offset)
        
        # Execute query
        result = await db.execute(base_query)
        audit_entries = result.scalars().all()
        
        # Convert to response format
        entries = []
        for entry in audit_entries:
            entries.append(AuditTrailEntry(
                id=entry.id,
                entity_type=entry.entity_type,
                entity_id=entry.entity_id,
                action=entry.action,
                action_description=self.ACTION_TYPES.get(entry.action, entry.action),
                user_id=entry.user_id,
                timestamp=entry.timestamp,
                old_values=entry.old_values,
                new_values=entry.new_values,
                notes=entry.notes,
                ip_address=entry.ip_address,
                user_agent=entry.user_agent
            ))
        
        return entries
    
    async def get_entity_audit_history(
        self,
        db: AsyncSession,
        entity_type: str,
        entity_id: int
    ) -> List[AuditTrailEntry]:
        """Get complete audit history for a specific entity"""
        
        query = AuditTrailQuery(
            entity_type=entity_type,
            entity_id=entity_id
        )
        
        return await self.get_audit_trail(db, query)
    
    async def get_audit_summary(
        self,
        db: AsyncSession,
        start_date: date,
        end_date: date,
        company_id: Optional[int] = None
    ) -> AuditTrailSummary:
        """Get audit trail summary for a period"""
        
        # Base conditions
        conditions = [
            TaxAuditTrail.timestamp >= start_date,
            TaxAuditTrail.timestamp <= end_date
        ]
        
        # Add company filter if provided
        if company_id:
            # This would require joining with the entity tables to filter by company
            pass
        
        # Get total count
        count_result = await db.execute(
            select(func.count(TaxAuditTrail.id)).where(and_(*conditions))
        )
        total_events = count_result.scalar()
        
        # Get events by action type
        action_result = await db.execute(
            select(
                TaxAuditTrail.action,
                func.count(TaxAuditTrail.id).label('count')
            )
            .where(and_(*conditions))
            .group_by(TaxAuditTrail.action)
        )
        
        events_by_action = {}
        for row in action_result:
            events_by_action[row.action] = row.count
        
        # Get events by entity type
        entity_result = await db.execute(
            select(
                TaxAuditTrail.entity_type,
                func.count(TaxAuditTrail.id).label('count')
            )
            .where(and_(*conditions))
            .group_by(TaxAuditTrail.entity_type)
        )
        
        events_by_entity = {}
        for row in entity_result:
            events_by_entity[row.entity_type] = row.count
        
        # Get top users by activity
        user_result = await db.execute(
            select(
                TaxAuditTrail.user_id,
                func.count(TaxAuditTrail.id).label('count')
            )
            .where(and_(*conditions))
            .group_by(TaxAuditTrail.user_id)
            .order_by(desc(func.count(TaxAuditTrail.id)))
            .limit(10)
        )
        
        top_users = []
        for row in user_result:
            top_users.append({
                'user_id': row.user_id,
                'event_count': row.count
            })
        
        # Get daily activity
        daily_result = await db.execute(
            select(
                func.date(TaxAuditTrail.timestamp).label('date'),
                func.count(TaxAuditTrail.id).label('count')
            )
            .where(and_(*conditions))
            .group_by(func.date(TaxAuditTrail.timestamp))
            .order_by(func.date(TaxAuditTrail.timestamp))
        )
        
        daily_activity = []
        for row in daily_result:
            daily_activity.append({
                'date': row.date.isoformat(),
                'event_count': row.count
            })
        
        return AuditTrailSummary(
            period_start=start_date,
            period_end=end_date,
            total_events=total_events,
            events_by_action=events_by_action,
            events_by_entity=events_by_entity,
            top_users=top_users,
            daily_activity=daily_activity
        )
    
    async def detect_suspicious_activity(
        self,
        db: AsyncSession,
        lookback_days: int = 30
    ) -> List[Dict[str, Any]]:
        """Detect potentially suspicious audit trail patterns"""
        
        suspicious_activities = []
        
        # Look for unusual patterns in the last N days
        start_date = datetime.utcnow().date() - timedelta(days=lookback_days)
        
        # 1. Multiple rapid changes to the same entity
        rapid_changes_result = await db.execute(
            select(
                TaxAuditTrail.entity_type,
                TaxAuditTrail.entity_id,
                TaxAuditTrail.user_id,
                func.count(TaxAuditTrail.id).label('change_count'),
                func.min(TaxAuditTrail.timestamp).label('first_change'),
                func.max(TaxAuditTrail.timestamp).label('last_change')
            )
            .where(
                and_(
                    TaxAuditTrail.timestamp >= start_date,
                    TaxAuditTrail.action.in_(['UPDATE', 'DELETE'])
                )
            )
            .group_by(TaxAuditTrail.entity_type, TaxAuditTrail.entity_id, TaxAuditTrail.user_id)
            .having(func.count(TaxAuditTrail.id) > 10)  # More than 10 changes
        )
        
        for row in rapid_changes_result:
            time_diff = row.last_change - row.first_change
            if time_diff.total_seconds() < 3600:  # Within 1 hour
                suspicious_activities.append({
                    'type': 'rapid_changes',
                    'description': f'Rapid changes to {row.entity_type} {row.entity_id}',
                    'entity_type': row.entity_type,
                    'entity_id': row.entity_id,
                    'user_id': row.user_id,
                    'change_count': row.change_count,
                    'time_span_minutes': int(time_diff.total_seconds() / 60),
                    'severity': 'high' if row.change_count > 20 else 'medium'
                })
        
        # 2. After-hours activity
        after_hours_result = await db.execute(
            select(
                TaxAuditTrail.user_id,
                func.count(TaxAuditTrail.id).label('after_hours_count')
            )
            .where(
                and_(
                    TaxAuditTrail.timestamp >= start_date,
                    func.extract('hour', TaxAuditTrail.timestamp).between(22, 6)  # 10 PM to 6 AM
                )
            )
            .group_by(TaxAuditTrail.user_id)
            .having(func.count(TaxAuditTrail.id) > 5)
        )
        
        for row in after_hours_result:
            suspicious_activities.append({
                'type': 'after_hours_activity',
                'description': f'Unusual after-hours activity',
                'user_id': row.user_id,
                'event_count': row.after_hours_count,
                'severity': 'medium'
            })
        
        # 3. Bulk deletions
        bulk_deletions_result = await db.execute(
            select(
                TaxAuditTrail.user_id,
                TaxAuditTrail.entity_type,
                func.count(TaxAuditTrail.id).label('deletion_count'),
                func.min(TaxAuditTrail.timestamp).label('first_deletion'),
                func.max(TaxAuditTrail.timestamp).label('last_deletion')
            )
            .where(
                and_(
                    TaxAuditTrail.timestamp >= start_date,
                    TaxAuditTrail.action == 'DELETE'
                )
            )
            .group_by(TaxAuditTrail.user_id, TaxAuditTrail.entity_type)
            .having(func.count(TaxAuditTrail.id) > 5)
        )
        
        for row in bulk_deletions_result:
            time_diff = row.last_deletion - row.first_deletion
            suspicious_activities.append({
                'type': 'bulk_deletions',
                'description': f'Bulk deletion of {row.entity_type} records',
                'user_id': row.user_id,
                'entity_type': row.entity_type,
                'deletion_count': row.deletion_count,
                'time_span_minutes': int(time_diff.total_seconds() / 60),
                'severity': 'high'
            })
        
        return suspicious_activities
    
    async def generate_compliance_report(
        self,
        db: AsyncSession,
        company_id: int,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Generate compliance report based on audit trail"""
        
        # Get all audit events for the period
        conditions = [
            TaxAuditTrail.timestamp >= start_date,
            TaxAuditTrail.timestamp <= end_date
        ]
        
        # Key compliance metrics
        
        # 1. Data integrity checks
        integrity_issues = []
        
        # Check for records modified after filing
        filed_returns_result = await db.execute(
            select(TaxReturn.id, TaxReturn.filing_date)
            .where(
                and_(
                    TaxReturn.filing_status == 'filed',
                    TaxReturn.filing_date >= start_date,
                    TaxReturn.filing_date <= end_date
                )
            )
        )
        
        for return_row in filed_returns_result:
            # Check for modifications after filing
            modifications_result = await db.execute(
                select(func.count(TaxAuditTrail.id))
                .where(
                    and_(
                        TaxAuditTrail.entity_type == 'tax_return',
                        TaxAuditTrail.entity_id == return_row.id,
                        TaxAuditTrail.action == 'UPDATE',
                        TaxAuditTrail.timestamp > return_row.filing_date
                    )
                )
            )
            
            modification_count = modifications_result.scalar()
            if modification_count > 0:
                integrity_issues.append({
                    'type': 'post_filing_modification',
                    'entity_id': return_row.id,
                    'modification_count': modification_count,
                    'filing_date': return_row.filing_date.isoformat()
                })
        
        # 2. Access control compliance
        unauthorized_access = []
        
        # This would check for access violations based on user roles
        # Simplified implementation
        
        # 3. Retention compliance
        retention_status = {
            'records_within_retention': 0,
            'records_approaching_retention': 0,
            'records_past_retention': 0
        }
        
        return {
            'period_start': start_date.isoformat(),
            'period_end': end_date.isoformat(),
            'company_id': company_id,
            'integrity_issues': integrity_issues,
            'unauthorized_access': unauthorized_access,
            'retention_status': retention_status,
            'compliance_score': self._calculate_compliance_score(
                len(integrity_issues), len(unauthorized_access)
            ),
            'recommendations': self._generate_compliance_recommendations(
                integrity_issues, unauthorized_access
            )
        }
    
    def _calculate_compliance_score(
        self,
        integrity_issues: int,
        unauthorized_access: int
    ) -> int:
        """Calculate compliance score (0-100)"""
        
        base_score = 100
        
        # Deduct points for issues
        base_score -= integrity_issues * 10
        base_score -= unauthorized_access * 15
        
        return max(0, base_score)
    
    def _generate_compliance_recommendations(
        self,
        integrity_issues: List,
        unauthorized_access: List
    ) -> List[str]:
        """Generate compliance recommendations"""
        
        recommendations = []
        
        if integrity_issues:
            recommendations.append(
                "Implement controls to prevent modifications to filed returns"
            )
            recommendations.append(
                "Review approval workflows for tax return modifications"
            )
        
        if unauthorized_access:
            recommendations.append(
                "Review user access permissions and role assignments"
            )
            recommendations.append(
                "Implement additional authentication controls for sensitive operations"
            )
        
        if not integrity_issues and not unauthorized_access:
            recommendations.append(
                "Maintain current compliance controls and monitoring"
            )
        
        return recommendations