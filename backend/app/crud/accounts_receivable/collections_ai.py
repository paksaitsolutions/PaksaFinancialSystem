"""
CRUD operations for AI-powered collections insights.
"""
from typing import List, Dict, Any
from datetime import date, datetime, timedelta
from decimal import Decimal
import random

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.accounts_receivable.customer import Customer
from app.models.accounts_receivable.invoice import Invoice
from app.schemas.accounts_receivable.collections_ai import (
    CustomerRiskProfile, CollectionPrediction, CollectionsInsights, CollectionStrategy
)

class CollectionsAICRUD:
    """CRUD operations for AI-powered collections insights."""
    
    async def get_customer_risk_profiles(self, db: AsyncSession) -> List[CustomerRiskProfile]:
        """Generate AI-powered customer risk profiles."""
        # Get customers with outstanding invoices
        query = select(Customer).join(Invoice).where(
            Invoice.status.in_(["sent", "overdue"])
        ).distinct()
        
        result = await db.execute(query)
        customers = result.scalars().all()
        
        profiles = []
        for customer in customers:
            # Calculate risk metrics (simplified AI simulation)
            outstanding_query = select(
                func.sum(Invoice.amount).label("total"),
                func.sum(
                    func.case(
                        (Invoice.due_date < func.current_date(), Invoice.amount),
                        else_=0
                    )
                ).label("overdue")
            ).where(
                and_(
                    Invoice.customer_id == customer.id,
                    Invoice.status.in_(["sent", "overdue"])
                )
            )
            
            outstanding_result = await db.execute(outstanding_query)
            amounts = outstanding_result.first()
            
            total_outstanding = amounts.total or 0
            overdue_amount = amounts.overdue or 0
            
            # Calculate DSO (simplified)
            dso = self._calculate_dso(customer, db)
            
            # AI risk scoring (simplified algorithm)
            risk_score = await self._calculate_risk_score(
                customer, total_outstanding, overdue_amount, dso
            )
            
            risk_level = self._get_risk_level(risk_score)
            payment_behavior = self._analyze_payment_behavior(risk_score)
            
            profile = CustomerRiskProfile(
                customer_id=customer.id,
                customer_name=customer.name,
                risk_score=risk_score,
                risk_level=risk_level,
                payment_behavior=payment_behavior,
                days_sales_outstanding=dso,
                total_outstanding=total_outstanding,
                overdue_amount=overdue_amount,
                payment_history_score=max(0, 100 - risk_score),
                credit_utilization=min(100, (float(total_outstanding) / 10000) * 100),
                recommended_action=self._get_recommended_action(risk_level)
            )
            profiles.append(profile)
        
        return sorted(profiles, key=lambda x: x.risk_score, reverse=True)
    
    async def get_collection_predictions(self, db: AsyncSession) -> List[CollectionPrediction]:
        """Generate AI-powered collection predictions."""
        # Get overdue invoices
        query = select(Invoice).where(
            and_(
                Invoice.status == "overdue",
                Invoice.due_date < func.current_date()
            )
        ).options(selectinload(Invoice.customer))
        
        result = await db.execute(query)
        invoices = result.scalars().all()
        
        predictions = []
        for invoice in invoices:
            days_overdue = (date.today() - invoice.due_date).days
            
            # AI prediction algorithm (simplified)
            collection_probability = self._predict_collection_probability(
                invoice, days_overdue
            )
            
            predicted_date = self._predict_collection_date(
                collection_probability, days_overdue
            )
            
            strategy = self._recommend_strategy(collection_probability, days_overdue)
            confidence = min(0.95, max(0.6, 1 - (days_overdue / 365)))
            
            prediction = CollectionPrediction(
                invoice_id=invoice.id,
                customer_id=invoice.customer_id,
                invoice_number=invoice.invoice_number,
                amount=invoice.amount,
                days_overdue=days_overdue,
                collection_probability=collection_probability,
                predicted_collection_date=predicted_date,
                recommended_strategy=strategy,
                confidence_level=confidence
            )
            predictions.append(prediction)
        
        return sorted(predictions, key=lambda x: x.collection_probability)
    
    async def get_collections_insights(self, db: AsyncSession) -> CollectionsInsights:
        """Generate comprehensive collections insights."""
        # Get total outstanding
        outstanding_query = select(func.sum(Invoice.amount)).where(
            Invoice.status.in_(["sent", "overdue"])
        )
        outstanding_result = await db.execute(outstanding_query)
        total_outstanding = outstanding_result.scalar() or 0
        
        # Get risk profiles
        risk_profiles = await self.get_customer_risk_profiles(db)
        high_risk_customers = len([p for p in risk_profiles if p.risk_level in ["high", "critical"]])
        
        # Predict 30-day collections (simplified)
        predictions = await self.get_collection_predictions(db)
        predicted_30_days = sum(
            p.amount * p.collection_probability 
            for p in predictions 
            if p.predicted_collection_date and 
            p.predicted_collection_date <= date.today() + timedelta(days=30)
        )
        
        # Calculate efficiency score
        efficiency_score = min(100, max(0, 100 - (high_risk_customers * 10)))
        
        # Generate urgent actions
        urgent_actions = self._generate_urgent_actions(risk_profiles, predictions)
        
        # Generate trends (mock data)
        trends = {
            "collection_rate_trend": "improving",
            "dso_trend": "stable",
            "risk_score_trend": "decreasing"
        }
        
        return CollectionsInsights(
            total_outstanding=total_outstanding,
            high_risk_customers=high_risk_customers,
            predicted_collections_30_days=predicted_30_days,
            collection_efficiency_score=efficiency_score,
            top_risks=risk_profiles[:5],
            urgent_actions=urgent_actions,
            trends=trends
        )
    
    async def get_collection_strategies(
        self, db: AsyncSession, customer_id: UUID
    ) -> List[CollectionStrategy]:
        """Generate AI-recommended collection strategies for a customer."""
        # Get customer risk profile
        risk_profiles = await self.get_customer_risk_profiles(db)
        customer_profile = next(
            (p for p in risk_profiles if p.customer_id == customer_id), None
        )
        
        if not customer_profile:
            return []
        
        strategies = []
        
        # Generate strategies based on risk level
        if customer_profile.risk_level == "low":
            strategies.extend([
                CollectionStrategy(
                    customer_id=customer_id,
                    strategy_type="email",
                    priority=3,
                    message_template="Friendly payment reminder",
                    timing="Send in 3 days",
                    expected_outcome="Payment within 7 days",
                    success_probability=0.85
                )
            ])
        elif customer_profile.risk_level == "medium":
            strategies.extend([
                CollectionStrategy(
                    customer_id=customer_id,
                    strategy_type="call",
                    priority=2,
                    message_template="Personal follow-up call",
                    timing="Call within 24 hours",
                    expected_outcome="Payment arrangement",
                    success_probability=0.70
                ),
                CollectionStrategy(
                    customer_id=customer_id,
                    strategy_type="email",
                    priority=3,
                    message_template="Formal payment notice",
                    timing="Send immediately",
                    expected_outcome="Response within 3 days",
                    success_probability=0.60
                )
            ])
        else:  # high or critical
            strategies.extend([
                CollectionStrategy(
                    customer_id=customer_id,
                    strategy_type="legal",
                    priority=1,
                    message_template="Legal action notice",
                    timing="Send immediately",
                    expected_outcome="Immediate payment or legal action",
                    success_probability=0.50
                ),
                CollectionStrategy(
                    customer_id=customer_id,
                    strategy_type="discount",
                    priority=2,
                    message_template="Settlement offer",
                    timing="Offer within 48 hours",
                    expected_outcome="Partial payment",
                    success_probability=0.65
                )
            ])
        
        return sorted(strategies, key=lambda x: x.priority)
    
    def _calculate_dso(self, customer: Customer, db: AsyncSession) -> int:
        """Calculate Days Sales Outstanding (simplified)."""
        # Simplified DSO calculation
        return random.randint(30, 90)
    
    async def _calculate_risk_score(
        self, customer: Customer, total_outstanding: Decimal, 
        overdue_amount: Decimal, dso: int
    ) -> float:
        """Calculate AI risk score (simplified algorithm)."""
        score = 0
        
        # Overdue ratio factor
        if total_outstanding > 0:
            overdue_ratio = float(overdue_amount) / float(total_outstanding)
            score += overdue_ratio * 40
        
        # DSO factor
        if dso > 60:
            score += (dso - 60) * 0.5
        
        # Amount factor
        if total_outstanding > 10000:
            score += 20
        elif total_outstanding > 5000:
            score += 10
        
        # Add some randomness for simulation
        score += random.uniform(-5, 15)
        
        return min(100, max(0, score))
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Convert risk score to risk level."""
        if risk_score >= 80:
            return "critical"
        elif risk_score >= 60:
            return "high"
        elif risk_score >= 40:
            return "medium"
        else:
            return "low"
    
    def _analyze_payment_behavior(self, risk_score: float) -> str:
        """Analyze payment behavior based on risk score."""
        if risk_score >= 80:
            return "Consistently late, multiple defaults"
        elif risk_score >= 60:
            return "Frequently late payments"
        elif risk_score >= 40:
            return "Occasionally late"
        else:
            return "Generally pays on time"
    
    def _get_recommended_action(self, risk_level: str) -> str:
        """Get recommended action based on risk level."""
        actions = {
            "low": "Monitor payment dates",
            "medium": "Send payment reminder",
            "high": "Immediate follow-up required",
            "critical": "Consider legal action"
        }
        return actions.get(risk_level, "Monitor")
    
    def _predict_collection_probability(self, invoice: Invoice, days_overdue: int) -> float:
        """Predict collection probability (simplified AI)."""
        base_probability = 0.9
        
        # Decrease probability based on days overdue
        decay_factor = 0.02
        probability = base_probability * (1 - (days_overdue * decay_factor))
        
        # Add some randomness
        probability += random.uniform(-0.1, 0.1)
        
        return min(1.0, max(0.1, probability))
    
    def _predict_collection_date(
        self, collection_probability: float, days_overdue: int
    ) -> Optional[date]:
        """Predict collection date based on probability."""
        if collection_probability < 0.3:
            return None
        
        # Higher probability = sooner collection
        days_to_collect = int(30 * (1 - collection_probability)) + random.randint(1, 14)
        return date.today() + timedelta(days=days_to_collect)
    
    def _recommend_strategy(self, collection_probability: float, days_overdue: int) -> str:
        """Recommend collection strategy."""
        if collection_probability > 0.7:
            return "Gentle reminder email"
        elif collection_probability > 0.5:
            return "Phone call follow-up"
        elif collection_probability > 0.3:
            return "Formal demand letter"
        else:
            return "Consider legal action"
    
    def _generate_urgent_actions(
        self, risk_profiles: List[CustomerRiskProfile], 
        predictions: List[CollectionPrediction]
    ) -> List[Dict[str, Any]]:
        """Generate urgent action items."""
        actions = []
        
        # Critical risk customers
        critical_customers = [p for p in risk_profiles if p.risk_level == "critical"]
        for customer in critical_customers[:3]:
            actions.append({
                "type": "critical_customer",
                "customer_name": customer.customer_name,
                "amount": float(customer.total_outstanding),
                "action": "Immediate legal action required",
                "priority": 1
            })
        
        # Low probability collections
        low_prob_predictions = [p for p in predictions if p.collection_probability < 0.3]
        for pred in low_prob_predictions[:2]:
            actions.append({
                "type": "low_collection_probability",
                "invoice_number": pred.invoice_number,
                "amount": float(pred.amount),
                "action": "Consider write-off or legal action",
                "priority": 2
            })
        
        return actions

# Create an instance for dependency injection
collections_ai_crud = CollectionsAICRUD()