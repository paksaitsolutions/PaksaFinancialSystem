"""
Advanced performance management service.
"""
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.models.hrm.employee import Employee
from app.models.hrm.performance import PerformanceReview, Goal

class PerformanceService:
    """Advanced performance management service."""
    
    async def create_performance_review(
        self,
        db: AsyncSession,
        employee_id: UUID,
        reviewer_id: UUID,
        review_data: Dict[str, Any]
    ) -> PerformanceReview:
        """Create a new performance review."""
        review = PerformanceReview(
            employee_id=employee_id,
            reviewer_id=reviewer_id,
            **review_data
        )
        db.add(review)
        await db.commit()
        await db.refresh(review)
        return review
    
    async def complete_performance_review(
        self,
        db: AsyncSession,
        review_id: UUID,
        completion_data: Dict[str, Any]
    ) -> PerformanceReview:
        """Complete a performance review."""
        result = await db.execute(
            select(PerformanceReview).where(PerformanceReview.id == review_id)
        )
        review = result.scalar_one_or_none()
        
        if not review:
            raise ValueError("Performance review not found")
        
        # Update review with completion data
        for key, value in completion_data.items():
            if hasattr(review, key):
                setattr(review, key, value)
        
        review.status = "completed"
        review.completed_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(review)
        return review
    
    async def create_employee_goal(
        self,
        db: AsyncSession,
        employee_id: UUID,
        goal_data: Dict[str, Any]
    ) -> Goal:
        """Create a new employee goal."""
        goal = Goal(
            employee_id=employee_id,
            **goal_data
        )
        db.add(goal)
        await db.commit()
        await db.refresh(goal)
        return goal
    
    async def update_goal_progress(
        self,
        db: AsyncSession,
        goal_id: UUID,
        progress_percentage: int,
        notes: Optional[str] = None
    ) -> Goal:
        """Update goal progress."""
        result = await db.execute(
            select(Goal).where(Goal.id == goal_id)
        )
        goal = result.scalar_one_or_none()
        
        if not goal:
            raise ValueError("Goal not found")
        
        goal.progress_percentage = min(100, max(0, progress_percentage))
        goal.updated_at = datetime.utcnow()
        
        if progress_percentage >= 100:
            goal.status = "completed"
        
        await db.commit()
        await db.refresh(goal)
        return goal
    
    async def get_employee_performance_summary(
        self,
        db: AsyncSession,
        employee_id: UUID,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get employee performance summary."""
        if not year:
            year = datetime.now().year
        
        # Get performance reviews for the year
        reviews_result = await db.execute(
            select(PerformanceReview).where(
                and_(
                    PerformanceReview.employee_id == employee_id,
                    func.extract('year', PerformanceReview.review_period_end) == year
                )
            )
        )
        reviews = reviews_result.scalars().all()
        
        # Get goals for the year
        goals_result = await db.execute(
            select(Goal).where(
                and_(
                    Goal.employee_id == employee_id,
                    func.extract('year', Goal.created_at) == year
                )
            )
        )
        goals = goals_result.scalars().all()
        
        # Calculate averages
        avg_rating = 0
        if reviews:
            total_rating = sum(r.overall_rating or 0 for r in reviews)
            avg_rating = total_rating / len(reviews)
        
        # Goal completion rate
        completed_goals = [g for g in goals if g.status == "completed"]
        goal_completion_rate = len(completed_goals) / len(goals) * 100 if goals else 0
        
        return {
            "employee_id": employee_id,
            "year": year,
            "total_reviews": len(reviews),
            "average_rating": float(avg_rating),
            "total_goals": len(goals),
            "completed_goals": len(completed_goals),
            "goal_completion_rate": goal_completion_rate,
            "reviews": [self._serialize_review(r) for r in reviews],
            "goals": [self._serialize_goal(g) for g in goals]
        }
    
    async def get_team_performance_analytics(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        department: Optional[str] = None,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get team performance analytics."""
        if not year:
            year = datetime.now().year
        
        # Build employee filter
        employee_filter = [Employee.tenant_id == tenant_id, Employee.is_active == True]
        if department:
            employee_filter.append(Employee.department == department)
        
        # Get employees
        employees_result = await db.execute(
            select(Employee).where(and_(*employee_filter))
        )
        employees = employees_result.scalars().all()
        employee_ids = [e.id for e in employees]
        
        if not employee_ids:
            return {"message": "No employees found"}
        
        # Get performance reviews
        reviews_result = await db.execute(
            select(PerformanceReview).where(
                and_(
                    PerformanceReview.employee_id.in_(employee_ids),
                    func.extract('year', PerformanceReview.review_period_end) == year,
                    PerformanceReview.status == "completed"
                )
            )
        )
        reviews = reviews_result.scalars().all()
        
        # Calculate analytics
        total_employees = len(employees)
        employees_with_reviews = len(set(r.employee_id for r in reviews))
        review_completion_rate = employees_with_reviews / total_employees * 100 if total_employees else 0
        
        # Rating distribution
        ratings = [r.overall_rating for r in reviews if r.overall_rating]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        rating_distribution = {
            "excellent": len([r for r in ratings if r >= 4.5]),
            "good": len([r for r in ratings if 3.5 <= r < 4.5]),
            "satisfactory": len([r for r in ratings if 2.5 <= r < 3.5]),
            "needs_improvement": len([r for r in ratings if r < 2.5])
        }
        
        return {
            "department": department or "All Departments",
            "year": year,
            "total_employees": total_employees,
            "employees_with_reviews": employees_with_reviews,
            "review_completion_rate": review_completion_rate,
            "average_rating": float(avg_rating),
            "total_reviews": len(reviews),
            "rating_distribution": rating_distribution
        }
    
    def _serialize_review(self, review: PerformanceReview) -> Dict[str, Any]:
        """Serialize performance review."""
        return {
            "id": str(review.id),
            "review_period_start": review.review_period_start.isoformat() if review.review_period_start else None,
            "review_period_end": review.review_period_end.isoformat() if review.review_period_end else None,
            "review_type": review.review_type,
            "overall_rating": float(review.overall_rating) if review.overall_rating else None,
            "status": review.status,
            "completed_at": review.completed_at.isoformat() if review.completed_at else None
        }
    
    def _serialize_goal(self, goal: Goal) -> Dict[str, Any]:
        """Serialize goal."""
        return {
            "id": str(goal.id),
            "title": goal.title,
            "description": goal.description,
            "target_date": goal.target_date.isoformat() if goal.target_date else None,
            "status": goal.status,
            "progress_percentage": goal.progress_percentage
        }