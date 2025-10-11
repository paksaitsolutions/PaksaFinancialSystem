"""
Initialize AI/BI module with mock data for testing
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from app.models.ai_bi_models import (
    AIInsight, AIRecommendation, AIAnomaly, AIPrediction, AIModelMetrics
)


def init_ai_bi_mock_data(db: Session, company_id: str = "12345678-1234-5678-9012-123456789012"):
    """Initialize AI/BI module with comprehensive mock data"""
    
    # Create tables if they don't exist
    from app.models.base import Base
    from app.core.database import engine
    Base.metadata.create_all(bind=engine, tables=[
        AIInsight.__table__,
        AIRecommendation.__table__,
        AIAnomaly.__table__,
        AIPrediction.__table__,
        AIModelMetrics.__table__
    ])
    
    # Convert string to UUID
    company_uuid = uuid.UUID(company_id)
    
    # Clear existing data for this company
    try:
        db.query(AIInsight).filter(AIInsight.company_id == company_uuid).delete()
        db.query(AIRecommendation).filter(AIRecommendation.company_id == company_uuid).delete()
        db.query(AIAnomaly).filter(AIAnomaly.company_id == company_uuid).delete()
        db.query(AIPrediction).filter(AIPrediction.company_id == company_uuid).delete()
        db.query(AIModelMetrics).filter(AIModelMetrics.company_id == company_uuid).delete()
    except Exception as e:
        print(f"Warning: Could not clear existing data: {e}")
        db.rollback()
    
    # Create AI Insights
    insights = [
        AIInsight(
            company_id=company_uuid,
            title="Cash Flow Pattern Analysis",
            description="Analysis shows seasonal cash flow patterns with 15% variance in Q4.",
            insight_type="trend",
            module="cash",
            priority="Medium",
            confidence_score=0.87,
            meta_data={"variance": 0.15, "quarter": "Q4"}
        ),
        AIInsight(
            company_id=company_uuid,
            title="Vendor Payment Optimization",
            description="Current vendor payment terms show potential for 8% cost reduction.",
            insight_type="recommendation",
            module="ap",
            priority="High",
            confidence_score=0.92,
            meta_data={"potential_savings": 0.08}
        )
    ]
    
    # Create AI Recommendations
    recommendations = [
        AIRecommendation(
            company_id=company_uuid,
            title="Implement Dynamic Cash Flow Forecasting",
            description="Deploy ML-based cash flow forecasting to improve accuracy by 25%.",
            recommendation_type="cash_flow_optimization",
            module="cash",
            priority="High",
            confidence_score=0.91,
            estimated_impact=35000.0,
            action_items=["Implement ML forecasting model", "Set up automated alerts"]
        )
    ]
    
    # Create AI Anomalies
    anomalies = [
        AIAnomaly(
            company_id=company_uuid,
            title="Unusual Cash Outflow Spike",
            description="Cash outflow increased by 45% compared to historical average.",
            anomaly_type="cash_flow_deviation",
            module="cash",
            severity="High",
            anomaly_score=0.89,
            threshold=0.75,
            affected_records=[{"account": "main_checking", "deviation": 0.45}]
        )
    ]
    
    # Create AI Predictions
    predictions = [
        AIPrediction(
            company_id=company_uuid,
            prediction_type="cash_flow",
            module="cash",
            target_date=datetime.utcnow() + timedelta(days=30),
            predicted_value=285000.0,
            confidence_interval={"lower": 265000.0, "upper": 305000.0},
            accuracy_score=0.87,
            model_version="v2.1",
            input_features={"historical_periods": 12, "seasonal_adjustment": True}
        )
    ]
    
    # Create AI Model Metrics
    model_metrics = [
        AIModelMetrics(
            company_id=company_uuid,
            model_name="CashFlowPredictor",
            model_type="forecasting",
            version="v2.1",
            accuracy=0.87,
            precision=0.89,
            recall=0.85,
            f1_score=0.87,
            training_data_size=2400,
            last_trained=datetime.utcnow() - timedelta(days=7),
            hyperparameters={"learning_rate": 0.001, "epochs": 100}
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