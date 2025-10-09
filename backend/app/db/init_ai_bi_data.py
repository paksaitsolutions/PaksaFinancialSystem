"""
Initialize AI/BI module with mock data for testing
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from app.models.ai_bi_models import (
    AIInsight, AIRecommendation, AIAnomaly, AIPrediction, AIModelMetrics
)


def init_ai_bi_mock_data(db: Session, tenant_id: str = "12345678-1234-5678-9012-123456789012"):
    """Initialize AI/BI module with comprehensive mock data"""
    
    # Clear existing data for this tenant
    db.query(AIInsight).filter(AIInsight.tenant_id == tenant_id).delete()
    db.query(AIRecommendation).filter(AIRecommendation.tenant_id == tenant_id).delete()
    db.query(AIAnomaly).filter(AIAnomaly.tenant_id == tenant_id).delete()
    db.query(AIPrediction).filter(AIPrediction.tenant_id == tenant_id).delete()
    db.query(AIModelMetrics).filter(AIModelMetrics.tenant_id == tenant_id).delete()
    
    # Create AI Insights
    insights = [
        AIInsight(
            tenant_id=tenant_id,
            title="Cash Flow Pattern Analysis",
            description="Analysis shows seasonal cash flow patterns with 15% variance in Q4. Consider adjusting payment schedules.",
            insight_type="trend",
            module="cash",
            priority="Medium",
            confidence_score=0.87,
            meta_data={"variance": 0.15, "quarter": "Q4", "pattern": "seasonal"}
        ),
        AIInsight(
            tenant_id=tenant_id,
            title="Vendor Payment Optimization",
            description="Current vendor payment terms show potential for 8% cost reduction through early payment discounts.",
            insight_type="recommendation",
            module="ap",
            priority="High",
            confidence_score=0.92,
            meta_data={"potential_savings": 0.08, "vendors_affected": 12}
        ),
        AIInsight(
            tenant_id=tenant_id,
            title="Customer Payment Behavior",
            description="Customer payment patterns indicate 23% of invoices are paid early, suggesting room for discount optimization.",
            insight_type="trend",
            module="ar",
            priority="Medium",
            confidence_score=0.79,
            meta_data={"early_payment_rate": 0.23, "optimization_potential": True}
        ),
        AIInsight(
            tenant_id=tenant_id,
            title="Budget Variance Detection",
            description="Budget variance analysis reveals consistent overspending in office supplies category by 12%.",
            insight_type="anomaly",
            module="budget",
            priority="High",
            confidence_score=0.94,
            meta_data={"category": "office_supplies", "variance": 0.12, "trend": "consistent"}
        )
    ]
    
    # Create AI Recommendations
    recommendations = [
        AIRecommendation(
            tenant_id=tenant_id,
            title="Implement Dynamic Cash Flow Forecasting",
            description="Deploy machine learning-based cash flow forecasting to improve accuracy by 25% and reduce cash gaps.",
            recommendation_type="cash_flow_optimization",
            module="cash",
            priority="High",
            confidence_score=0.91,
            estimated_impact=35000.0,
            action_items=[
                "Implement ML forecasting model",
                "Set up automated cash position alerts",
                "Create weekly cash flow reports",
                "Establish minimum cash thresholds"
            ]
        ),
        AIRecommendation(
            tenant_id=tenant_id,
            title="Optimize Vendor Payment Terms",
            description="Negotiate extended payment terms with top 10 vendors to improve cash flow by $45K monthly.",
            recommendation_type="payment_optimization",
            module="ap",
            priority="High",
            confidence_score=0.88,
            estimated_impact=45000.0,
            action_items=[
                "Identify top 10 vendors by volume",
                "Analyze current payment terms",
                "Prepare negotiation strategy",
                "Implement new payment schedules"
            ]
        ),
        AIRecommendation(
            tenant_id=tenant_id,
            title="Accelerate Receivables Collection",
            description="Implement automated collection workflow to reduce DSO by 8 days and improve cash flow.",
            recommendation_type="collection_optimization",
            module="ar",
            priority="Medium",
            confidence_score=0.85,
            estimated_impact=28000.0,
            action_items=[
                "Set up automated reminder system",
                "Create collection workflow templates",
                "Implement early payment incentives",
                "Monitor DSO metrics weekly"
            ]
        ),
        AIRecommendation(
            tenant_id=tenant_id,
            title="Budget Control Enhancement",
            description="Implement real-time budget monitoring to prevent overspending and improve budget accuracy.",
            recommendation_type="budget_control",
            module="budget",
            priority="Medium",
            confidence_score=0.82,
            estimated_impact=15000.0,
            action_items=[
                "Set up real-time budget alerts",
                "Create approval workflows",
                "Implement spending limits",
                "Generate variance reports"
            ]
        )
    ]
    
    # Create AI Anomalies
    anomalies = [
        AIAnomaly(
            tenant_id=tenant_id,
            title="Unusual Cash Outflow Spike",
            description="Cash outflow increased by 45% compared to historical average for this period.",
            anomaly_type="cash_flow_deviation",
            module="cash",
            severity="High",
            anomaly_score=0.89,
            threshold=0.75,
            affected_records=[
                {"account": "main_checking", "deviation": 0.45, "amount": 125000},
                {"account": "payroll_account", "deviation": 0.32, "amount": 85000}
            ]
        ),
        AIAnomaly(
            tenant_id=tenant_id,
            title="Vendor Payment Delay Pattern",
            description="Average payment delay to vendors increased from 2 days to 12 days over the past month.",
            anomaly_type="payment_delay",
            module="ap",
            severity="Medium",
            anomaly_score=0.73,
            threshold=0.65,
            affected_records=[
                {"vendor_count": 8, "avg_delay_increase": 10, "impact": "moderate"}
            ]
        ),
        AIAnomaly(
            tenant_id=tenant_id,
            title="Customer Payment Behavior Change",
            description="Customer payment times have increased by 18% indicating potential collection issues.",
            anomaly_type="collection_delay",
            module="ar",
            severity="Medium",
            anomaly_score=0.71,
            threshold=0.60,
            affected_records=[
                {"customer_count": 15, "avg_delay_increase": 6, "dso_impact": 18}
            ]
        )
    ]
    
    # Create AI Predictions
    predictions = [
        AIPrediction(
            tenant_id=tenant_id,
            prediction_type="cash_flow",
            module="cash",
            target_date=datetime.utcnow() + timedelta(days=30),
            predicted_value=285000.0,
            confidence_interval={"lower": 265000.0, "upper": 305000.0},
            accuracy_score=0.87,
            model_version="v2.1",
            input_features={
                "historical_periods": 12,
                "seasonal_adjustment": True,
                "trend_analysis": True,
                "external_factors": ["market_conditions", "seasonal_patterns"]
            }
        ),
        AIPrediction(
            tenant_id=tenant_id,
            prediction_type="revenue",
            module="ar",
            target_date=datetime.utcnow() + timedelta(days=30),
            predicted_value=450000.0,
            confidence_interval={"lower": 420000.0, "upper": 480000.0},
            accuracy_score=0.83,
            model_version="v1.8",
            input_features={
                "customer_trends": True,
                "seasonal_factors": True,
                "market_indicators": True
            }
        ),
        AIPrediction(
            tenant_id=tenant_id,
            prediction_type="expense",
            module="ap",
            target_date=datetime.utcnow() + timedelta(days=30),
            predicted_value=320000.0,
            confidence_interval={"lower": 305000.0, "upper": 335000.0},
            accuracy_score=0.79,
            model_version="v1.5",
            input_features={
                "vendor_patterns": True,
                "seasonal_spending": True,
                "budget_constraints": True
            }
        ),
        AIPrediction(
            tenant_id=tenant_id,
            prediction_type="budget_variance",
            module="budget",
            target_date=datetime.utcnow() + timedelta(days=90),
            predicted_value=0.08,  # 8% variance
            confidence_interval={"lower": 0.05, "upper": 0.12},
            accuracy_score=0.91,
            model_version="v2.0",
            input_features={
                "historical_variance": True,
                "spending_patterns": True,
                "seasonal_adjustments": True
            }
        )
    ]
    
    # Create AI Model Metrics
    model_metrics = [
        AIModelMetrics(
            tenant_id=tenant_id,
            model_name="CashFlowPredictor",
            model_type="forecasting",
            version="v2.1",
            accuracy=0.87,
            precision=0.89,
            recall=0.85,
            f1_score=0.87,
            training_data_size=2400,
            last_trained=datetime.utcnow() - timedelta(days=7),
            hyperparameters={
                "learning_rate": 0.001,
                "epochs": 100,
                "batch_size": 32,
                "hidden_layers": [128, 64, 32]
            }
        ),
        AIModelMetrics(
            tenant_id=tenant_id,
            model_name="AnomalyDetector",
            model_type="classification",
            version="v1.9",
            accuracy=0.92,
            precision=0.94,
            recall=0.89,
            f1_score=0.91,
            training_data_size=5000,
            last_trained=datetime.utcnow() - timedelta(days=3),
            hyperparameters={
                "algorithm": "isolation_forest",
                "contamination": 0.1,
                "n_estimators": 100
            }
        ),
        AIModelMetrics(
            tenant_id=tenant_id,
            model_name="RecommendationEngine",
            model_type="classification",
            version="v1.6",
            accuracy=0.84,
            precision=0.86,
            recall=0.82,
            f1_score=0.84,
            training_data_size=3200,
            last_trained=datetime.utcnow() - timedelta(days=5),
            hyperparameters={
                "algorithm": "random_forest",
                "n_estimators": 200,
                "max_depth": 10,
                "min_samples_split": 5
            }
        )
    ]
    
    # Add all data to database
    for insight in insights:
        db.add(insight)
    
    for recommendation in recommendations:
        db.add(recommendation)
    
    for anomaly in anomalies:
        db.add(anomaly)
    
    for prediction in predictions:
        db.add(prediction)
    
    for metric in model_metrics:
        db.add(metric)
    
    db.commit()
    
    print(f"AI/BI mock data initialized successfully:")
    print(f"- {len(insights)} insights created")
    print(f"- {len(recommendations)} recommendations created")
    print(f"- {len(anomalies)} anomalies created")
    print(f"- {len(predictions)} predictions created")
    print(f"- {len(model_metrics)} model metrics created")


if __name__ == "__main__":
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    try:
        init_ai_bi_mock_data(db)
    finally:
        db.close()