"""
Succession planning service.
"""
from datetime import date, datetime
from typing import List, Dict, Any, Optional

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.hrm.employee import Employee
from app.models.hrm.succession import SuccessionPlan, SuccessionCandidate, DevelopmentPlan, DevelopmentActivity




class SuccessionService:
    """Succession planning service."""
    
    async def create_succession_plan(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        plan_data: Dict[str, Any]
    ) -> SuccessionPlan:
        """Create Succession Plan."""
        """Create a new succession plan."""
        plan = SuccessionPlan(
            tenant_id=tenant_id,
            **plan_data
        )
        db.add(plan)
        await db.commit()
        await db.refresh(plan)
        return plan
    
    async def add_succession_candidate(
        self,
        db: AsyncSession,
        succession_plan_id: UUID,
        employee_id: UUID,
        candidate_data: Dict[str, Any]
    ) -> SuccessionCandidate:
        """Add Succession Candidate."""
        """Add a candidate to succession plan."""
        candidate = SuccessionCandidate(
            succession_plan_id=succession_plan_id,
            employee_id=employee_id,
            **candidate_data
        )
        db.add(candidate)
        await db.commit()
        await db.refresh(candidate)
        return candidate
    
    async def create_development_plan(
        self,
        db: AsyncSession,
        employee_id: UUID,
        plan_data: Dict[str, Any]
    ) -> DevelopmentPlan:
        """Create Development Plan."""
        """Create employee development plan."""
        plan = DevelopmentPlan(
            employee_id=employee_id,
            **plan_data
        )
        db.add(plan)
        await db.commit()
        await db.refresh(plan)
        return plan
    
    async def add_development_activity(
        self,
        db: AsyncSession,
        development_plan_id: UUID,
        activity_data: Dict[str, Any]
    ) -> DevelopmentActivity:
        """Add Development Activity."""
        """Add activity to development plan."""
        activity = DevelopmentActivity(
            development_plan_id=development_plan_id,
            **activity_data
        )
        db.add(activity)
        await db.commit()
        await db.refresh(activity)
        return activity
    
    async def get_succession_plans(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        department: Optional[str] = None,
        risk_level: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get Succession Plans."""
        """Get succession plans with filters."""
        filters = [SuccessionPlan.tenant_id == tenant_id, SuccessionPlan.status == "active"]
        
        if department:
            filters.append(SuccessionPlan.department == department)
        if risk_level:
            filters.append(SuccessionPlan.risk_level == risk_level)
        
        result = await db.execute(
            select(SuccessionPlan).where(and_(*filters))
        )
        plans = result.scalars().all()
        
        return [await self._serialize_succession_plan(db, plan) for plan in plans]
    
    async def get_succession_readiness_report(
        self,
        db: AsyncSession,
        tenant_id: UUID
    ) -> Dict[str, Any]:
        """Get Succession Readiness Report."""
        """Generate succession readiness report."""
        # Get all active succession plans
        plans_result = await db.execute(
            select(SuccessionPlan).where(
                and_(
                    SuccessionPlan.tenant_id == tenant_id,
                    SuccessionPlan.status == "active"
                )
            )
        )
        plans = plans_result.scalars().all()
        
        # Get all candidates
        candidates_result = await db.execute(
            select(SuccessionCandidate).join(SuccessionPlan).where(
                and_(
                    SuccessionPlan.tenant_id == tenant_id,
                    SuccessionCandidate.is_active == True
                )
            )
        )
        candidates = candidates_result.scalars().all()
        
        # Calculate readiness metrics
        total_positions = len(plans)
        positions_with_ready_candidates = 0
        positions_at_risk = 0
        
        readiness_summary = {
            "ready_now": 0,
            "ready_1_2_years": 0,
            "ready_3_5_years": 0,
            "developing": 0
        }
        
        risk_summary = {
            "low": 0,
            "medium": 0,
            "high": 0,
            "critical": 0
        }
        
        for plan in plans:
            # Count risk levels
            risk_summary[plan.risk_level] += 1
            
            # Check if position has ready candidates
            plan_candidates = [c for c in candidates if c.succession_plan_id == plan.id]
            ready_candidates = [c for c in plan_candidates if c.readiness_level == "ready_now"]
            
            if ready_candidates:
                positions_with_ready_candidates += 1
            elif plan.risk_level in ["high", "critical"]:
                positions_at_risk += 1
            
            # Count readiness levels
            for candidate in plan_candidates:
                readiness_summary[candidate.readiness_level] += 1
        
        coverage_rate = positions_with_ready_candidates / total_positions * 100 if total_positions else 0
        
        return {
            "total_positions": total_positions,
            "positions_with_ready_candidates": positions_with_ready_candidates,
            "positions_at_risk": positions_at_risk,
            "succession_coverage_rate": coverage_rate,
            "readiness_distribution": readiness_summary,
            "risk_distribution": risk_summary,
            "recommendations": self._generate_succession_recommendations(
                coverage_rate, positions_at_risk, risk_summary
            )
        }
    
    async def get_employee_development_dashboard(
        self,
        db: AsyncSession,
        employee_id: UUID
    ) -> Dict[str, Any]:
        """Get Employee Development Dashboard."""
        """Get employee development dashboard."""
        # Get development plans
        plans_result = await db.execute(
            select(DevelopmentPlan).where(DevelopmentPlan.employee_id == employee_id)
        )
        plans = plans_result.scalars().all()
        
        # Get activities
        activities_result = await db.execute(
            select(DevelopmentActivity).join(DevelopmentPlan).where(
                DevelopmentPlan.employee_id == employee_id
            )
        )
        activities = activities_result.scalars().all()
        
        # Calculate metrics
        active_plans = [p for p in plans if p.status == "active"]
        completed_plans = [p for p in plans if p.status == "completed"]
        
        active_activities = [a for a in activities if a.status in ["planned", "in_progress"]]
        completed_activities = [a for a in activities if a.status == "completed"]
        
        # Calculate completion rates
        plan_completion_rate = len(completed_plans) / len(plans) * 100 if plans else 0
        activity_completion_rate = len(completed_activities) / len(activities) * 100 if activities else 0
        
        return {
            "employee_id": employee_id,
            "total_development_plans": len(plans),
            "active_plans": len(active_plans),
            "completed_plans": len(completed_plans),
            "plan_completion_rate": plan_completion_rate,
            "total_activities": len(activities),
            "active_activities": len(active_activities),
            "completed_activities": len(completed_activities),
            "activity_completion_rate": activity_completion_rate,
            "development_plans": [self._serialize_development_plan(p) for p in active_plans],
            "upcoming_activities": [self._serialize_activity(a) for a in active_activities[:5]]
        }
    
    async def _serialize_succession_plan(self, db: AsyncSession, plan: SuccessionPlan) -> Dict[str, Any]:
        """Serialize Succession Plan."""
        """Serialize succession plan with candidates."""
        # Get candidates
        candidates_result = await db.execute(
            select(SuccessionCandidate).where(
                and_(
                    SuccessionCandidate.succession_plan_id == plan.id,
                    SuccessionCandidate.is_active == True
                )
            )
        )
        candidates = candidates_result.scalars().all()
        
        return {
            "id": str(plan.id),
            "position_title": plan.position_title,
            "department": plan.department,
            "risk_level": plan.risk_level,
            "succession_timeline": plan.succession_timeline,
            "status": plan.status,
            "candidates_count": len(candidates),
            "ready_candidates": len([c for c in candidates if c.readiness_level == "ready_now"]),
            "candidates": [self._serialize_candidate(c) for c in candidates]
        }
    
    def _serialize_candidate(self, candidate: SuccessionCandidate) -> Dict[str, Any]:
        """ Serialize Candidate."""
        """Serialize succession candidate."""
        return {
            "id": str(candidate.id),
            "employee_id": str(candidate.employee_id),
            "readiness_level": candidate.readiness_level,
            "potential_rating": candidate.potential_rating,
            "progress_percentage": candidate.progress_percentage,
            "last_assessment_date": candidate.last_assessment_date.isoformat() if candidate.last_assessment_date else None,
            "next_review_date": candidate.next_review_date.isoformat() if candidate.next_review_date else None
        }
    
    def _serialize_development_plan(self, plan: DevelopmentPlan) -> Dict[str, Any]:
        """ Serialize Development Plan."""
        """Serialize development plan."""
        return {
            "id": str(plan.id),
            "plan_name": plan.plan_name,
            "description": plan.description,
            "development_type": plan.development_type,
            "priority": plan.priority,
            "status": plan.status,
            "completion_percentage": plan.completion_percentage,
            "start_date": plan.start_date.isoformat() if plan.start_date else None,
            "target_completion_date": plan.target_completion_date.isoformat() if plan.target_completion_date else None
        }
    
    def _serialize_activity(self, activity: DevelopmentActivity) -> Dict[str, Any]:
        """ Serialize Activity."""
        """Serialize development activity."""
        return {
            "id": str(activity.id),
            "activity_name": activity.activity_name,
            "activity_type": activity.activity_type,
            "status": activity.status,
            "completion_percentage": activity.completion_percentage,
            "planned_start_date": activity.planned_start_date.isoformat() if activity.planned_start_date else None,
            "planned_end_date": activity.planned_end_date.isoformat() if activity.planned_end_date else None
        }
    
    def _generate_succession_recommendations(
        self,
        coverage_rate: float,
        positions_at_risk: int,
        risk_summary: Dict[str, int]
    ) -> List[str]:
        """ Generate Succession Recommendations."""
        """Generate succession planning recommendations."""
        recommendations = []
        
        if coverage_rate < 70:
            recommendations.append("Increase succession planning coverage - identify and develop more candidates")
        
        if positions_at_risk > 0:
            recommendations.append(f"Address {positions_at_risk} high-risk positions without ready successors")
        
        if risk_summary.get("critical", 0) > 0:
            recommendations.append("Prioritize critical positions for immediate succession planning")
        
        if coverage_rate > 90:
            recommendations.append("Excellent succession coverage - focus on candidate development quality")
        
        return recommendations