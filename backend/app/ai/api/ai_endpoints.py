from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from ..services.anomaly_detection import AnomalyDetectionService
from ..services.predictive_analytics import PredictiveAnalyticsService
from ..services.recommendation_engine import RecommendationEngine
from ..services.nlp_service import NLPService

router = APIRouter(prefix="/ai", tags=["AI"])

# Initialize services
anomaly_service = AnomalyDetectionService()
predictive_service = PredictiveAnalyticsService()
recommendation_engine = RecommendationEngine()
nlp_service = NLPService()

@router.post("/detect-anomalies")
async def detect_anomalies(transactions: List[Dict[str, Any]]):
    """Detect anomalies in transaction data"""
    try:
        anomalies = anomaly_service.detect_transaction_anomalies(transactions)
        return {"anomalies": anomalies, "count": len(anomalies)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict-cash-flow")
async def predict_cash_flow(historical_data: List[Dict[str, Any]], days_ahead: int = 30):
    """Predict cash flow for specified days ahead"""
    try:
        prediction = predictive_service.predict_cash_flow(historical_data, days_ahead)
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict-customer-payment")
async def predict_customer_payment(customer_data: Dict[str, Any]):
    """Predict customer payment probability"""
    try:
        prediction = predictive_service.predict_customer_payment(customer_data)
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/forecast-revenue")
async def forecast_revenue(revenue_data: List[Dict[str, Any]], months_ahead: int = 3):
    """Forecast revenue for specified months ahead"""
    try:
        forecast = predictive_service.forecast_revenue(revenue_data, months_ahead)
        return {"forecast": forecast}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get-recommendations")
async def get_recommendations(user_id: str, user_data: Dict[str, Any]):
    """Get AI-powered financial recommendations"""
    try:
        recommendations = recommendation_engine.get_financial_recommendations(user_id, user_data)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/natural-query")
async def process_natural_query(query: str):
    """Process natural language query"""
    try:
        response = nlp_service.process_natural_query(query)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))