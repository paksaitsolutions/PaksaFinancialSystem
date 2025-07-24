import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ..ml_framework import MLFramework

class PredictiveAnalyticsService:
    def __init__(self):
        self.ml_framework = MLFramework()
    
    def predict_cash_flow(self, historical_data: List[Dict[str, Any]], days_ahead: int = 30) -> Dict[str, Any]:
        """Predict cash flow for next N days"""
        if not historical_data:
            return {"prediction": 0, "confidence": 0}
        
        df = pd.DataFrame(historical_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Simple moving average prediction
        recent_amounts = df['amount'].tail(7).values
        prediction = np.mean(recent_amounts) * days_ahead
        confidence = min(0.9, len(recent_amounts) / 10)
        
        return {
            "prediction": float(prediction),
            "confidence": float(confidence),
            "trend": "increasing" if recent_amounts[-1] > recent_amounts[0] else "decreasing"
        }
    
    def predict_customer_payment(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict customer payment probability"""
        payment_history = customer_data.get('payment_history', [])
        
        if not payment_history:
            return {"probability": 0.5, "risk_level": "medium"}
        
        # Calculate payment score based on history
        on_time_payments = sum(1 for p in payment_history if p.get('on_time', False))
        total_payments = len(payment_history)
        
        probability = on_time_payments / total_payments if total_payments > 0 else 0.5
        
        if probability >= 0.8:
            risk_level = "low"
        elif probability >= 0.6:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        return {
            "probability": probability,
            "risk_level": risk_level,
            "recommended_credit_limit": customer_data.get('current_balance', 0) * (1 + probability)
        }
    
    def forecast_revenue(self, revenue_data: List[Dict[str, Any]], months_ahead: int = 3) -> List[Dict[str, Any]]:
        """Forecast revenue for next N months"""
        if len(revenue_data) < 3:
            return []
        
        df = pd.DataFrame(revenue_data)
        df['month'] = pd.to_datetime(df['month'])
        df = df.sort_values('month')
        
        # Simple trend-based forecast
        recent_revenue = df['revenue'].tail(3).values
        trend = np.mean(np.diff(recent_revenue))
        
        forecasts = []
        last_revenue = recent_revenue[-1]
        last_month = df['month'].iloc[-1]
        
        for i in range(1, months_ahead + 1):
            forecast_month = last_month + pd.DateOffset(months=i)
            forecast_revenue = last_revenue + (trend * i)
            
            forecasts.append({
                "month": forecast_month.strftime("%Y-%m"),
                "forecasted_revenue": max(0, float(forecast_revenue)),
                "confidence": max(0.3, 0.9 - (i * 0.1))
            })
        
        return forecasts