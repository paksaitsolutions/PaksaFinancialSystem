"""
Advanced machine learning service for financial predictions.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

import numpy as np


class MLService:
    """Advanced machine learning service."""
    
    def __init__(self):
        self.models = {}
        self.model_metadata = {}
    
    def predict_cash_flow(self, historical_data: List[Dict[str, Any]], days_ahead: int = 30) -> Dict[str, Any]:
        if len(historical_data) < 10:
            return {"error": "Insufficient data for prediction"}
        
        amounts = [float(d.get('amount', 0)) for d in historical_data]
        
        # Simple trend analysis with seasonal adjustment
        recent_trend = np.mean(np.diff(amounts[-7:]))
        seasonal_factor = self._calculate_seasonal_factor(amounts)
        
        predictions = []
        for i in range(days_ahead):
            base_prediction = amounts[-1] + (recent_trend * (i + 1))
            adjusted_prediction = base_prediction * seasonal_factor
            
            predictions.append({
                "date": (datetime.now() + timedelta(days=i+1)).strftime("%Y-%m-%d"),
                "predicted_amount": float(adjusted_prediction),
                "confidence": max(0.3, 0.9 - (i * 0.02))
            })
        
        return {
            "predictions": predictions,
            "model_type": "Trend-based with seasonal adjustment",
            "total_predicted": sum(p["predicted_amount"] for p in predictions),
            "trend_direction": "increasing" if recent_trend > 0 else "decreasing"
        }
    
    def detect_anomalies(self, transaction_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        if len(transaction_data) < 20:
            return {"error": "Insufficient data for anomaly detection"}
        
        amounts = [float(d.get('amount', 0)) for d in transaction_data]
        mean_amount = np.mean(amounts)
        std_amount = np.std(amounts)
        
        anomalies = []
        for i, data in enumerate(transaction_data):
            amount = float(data.get('amount', 0))
            z_score = abs((amount - mean_amount) / std_amount) if std_amount > 0 else 0
            
            if z_score > 2.5:  # Anomaly threshold
                anomaly_data = data.copy()
                anomaly_data['anomaly_score'] = float(z_score)
                anomaly_data['severity'] = "high" if z_score > 3 else "medium"
                anomalies.append(anomaly_data)
        
        return {
            "total_transactions": len(transaction_data),
            "anomalies_detected": len(anomalies),
            "anomaly_rate": len(anomalies) / len(transaction_data),
            "anomalies": anomalies[:10],
            "threshold_used": 2.5
        }
    
    def predict_customer_churn(self, customer_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        if len(customer_data) < 10:
            return {"error": "Insufficient customer data"}
        
        high_risk = []
        medium_risk = []
        low_risk = []
        
        for customer in customer_data:
            risk_score = self._calculate_churn_risk(customer)
            customer_risk = customer.copy()
            customer_risk['churn_probability'] = risk_score
            
            if risk_score > 0.7:
                high_risk.append(customer_risk)
            elif risk_score > 0.4:
                medium_risk.append(customer_risk)
            else:
                low_risk.append(customer_risk)
        
        return {
            "total_customers": len(customer_data),
            "high_risk_count": len(high_risk),
            "medium_risk_count": len(medium_risk),
            "low_risk_count": len(low_risk),
            "high_risk_customers": high_risk[:10]
        }
    
    def generate_financial_insights(self, financial_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        insights = []
        
        # Revenue analysis
        if 'revenue_data' in financial_data:
            revenue_insight = self._analyze_revenue(financial_data['revenue_data'])
            if revenue_insight:
                insights.append(revenue_insight)
        
        # Expense analysis
        if 'expense_data' in financial_data:
            expense_insight = self._analyze_expenses(financial_data['expense_data'])
            if expense_insight:
                insights.append(expense_insight)
        
        # Cash flow analysis
        if 'cash_flow_data' in financial_data:
            cash_insight = self._analyze_cash_flow(financial_data['cash_flow_data'])
            if cash_insight:
                insights.append(cash_insight)
        
        return insights
    
    def _calculate_seasonal_factor(self, amounts: List[float]) -> float:
        if len(amounts) < 12:
            return 1.0
        
        # Simple seasonal calculation based on recent vs historical average
        recent_avg = np.mean(amounts[-3:])
        historical_avg = np.mean(amounts[:-3])
        
        return recent_avg / historical_avg if historical_avg != 0 else 1.0
    
    def _calculate_churn_risk(self, customer: Dict[str, Any]) -> float:
        risk_score = 0.0
        
        # Days since last transaction
        days_since_last = customer.get('days_since_last_transaction', 0)
        if days_since_last > 90:
            risk_score += 0.4
        elif days_since_last > 30:
            risk_score += 0.2
        
        # Transaction frequency
        total_transactions = customer.get('total_transactions', 0)
        if total_transactions < 5:
            risk_score += 0.3
        
        # Account age
        account_age = customer.get('account_age_days', 0)
        if account_age < 30:
            risk_score += 0.2
        
        # Average transaction amount
        avg_amount = customer.get('average_transaction_amount', 0)
        if avg_amount < 100:
            risk_score += 0.1
        
        return min(1.0, risk_score)
    
    def _analyze_revenue(self, revenue_data: List[Dict]) -> Optional[Dict[str, Any]]:
        if len(revenue_data) < 3:
            return None
        
        amounts = [float(d.get('amount', 0)) for d in revenue_data]
        trend = np.mean(np.diff(amounts))
        
        if trend > 100:
            return {
                "type": "revenue_trend",
                "title": "Revenue Growth Detected",
                "message": f"Revenue trending upward by ${trend:.2f} per period",
                "priority": "positive",
                "confidence": 0.8
            }
        elif trend < -100:
            return {
                "type": "revenue_trend",
                "title": "Revenue Decline Alert",
                "message": f"Revenue declining by ${abs(trend):.2f} per period",
                "priority": "high",
                "confidence": 0.8
            }
        
        return None
    
    def _analyze_expenses(self, expense_data: List[Dict]) -> Optional[Dict[str, Any]]:
        if len(expense_data) < 5:
            return None
        
        amounts = [float(d.get('amount', 0)) for d in expense_data]
        recent_avg = np.mean(amounts[-3:])
        historical_avg = np.mean(amounts[:-3])
        
        if recent_avg > historical_avg * 1.2:
            return {
                "type": "expense_pattern",
                "title": "Expense Increase Detected",
                "message": "Recent expenses 20% higher than average",
                "priority": "medium",
                "confidence": 0.7
            }
        
        return None
    
    def _analyze_cash_flow(self, cash_flow_data: List[Dict]) -> Optional[Dict[str, Any]]:
        if len(cash_flow_data) < 5:
            return None
        
        amounts = [float(d.get('amount', 0)) for d in cash_flow_data]
        negative_periods = sum(1 for amount in amounts if amount < 0)
        
        if negative_periods > len(amounts) * 0.4:
            return {
                "type": "cash_flow",
                "title": "Cash Flow Concern",
                "message": f"Negative cash flow in {negative_periods} periods",
                "priority": "high",
                "confidence": 0.9
            }
        
        return None