import numpy as np
from typing import List, Dict, Any
from collections import defaultdict

class RecommendationEngine:
    def __init__(self):
        self.user_preferences = defaultdict(dict)
    
    def get_financial_recommendations(self, user_id: str, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate financial recommendations for user"""
        recommendations = []
        
        # Cash flow recommendations
        cash_balance = user_data.get('cash_balance', 0)
        if cash_balance < 10000:
            recommendations.append({
                "type": "cash_management",
                "title": "Improve Cash Flow",
                "description": "Consider accelerating receivables collection",
                "priority": "high",
                "action": "review_aging_report"
            })
        
        # Expense optimization
        monthly_expenses = user_data.get('monthly_expenses', 0)
        monthly_revenue = user_data.get('monthly_revenue', 0)
        
        if monthly_expenses > monthly_revenue * 0.8:
            recommendations.append({
                "type": "expense_optimization",
                "title": "Reduce Operating Expenses",
                "description": "Expenses are high relative to revenue",
                "priority": "medium",
                "action": "analyze_expense_categories"
            })
        
        # Investment opportunities
        if cash_balance > 50000:
            recommendations.append({
                "type": "investment",
                "title": "Investment Opportunity",
                "description": "Consider short-term investments for excess cash",
                "priority": "low",
                "action": "explore_investment_options"
            })
        
        return recommendations
    
    def recommend_payment_terms(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend optimal payment terms for customer"""
        payment_history = customer_data.get('payment_history', [])
        credit_score = customer_data.get('credit_score', 700)
        
        if credit_score >= 750 and len(payment_history) > 5:
            recommended_terms = 45
            credit_limit_multiplier = 1.5
        elif credit_score >= 650:
            recommended_terms = 30
            credit_limit_multiplier = 1.2
        else:
            recommended_terms = 15
            credit_limit_multiplier = 0.8
        
        current_balance = customer_data.get('current_balance', 0)
        
        return {
            "recommended_payment_terms": recommended_terms,
            "recommended_credit_limit": current_balance * credit_limit_multiplier,
            "risk_assessment": "low" if credit_score >= 750 else "medium" if credit_score >= 650 else "high"
        }
    
    def suggest_cost_savings(self, expense_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Suggest cost-saving opportunities"""
        if not expense_data:
            return []
        
        # Analyze expense patterns
        category_totals = defaultdict(float)
        for expense in expense_data:
            category_totals[expense.get('category', 'other')] += expense.get('amount', 0)
        
        suggestions = []
        total_expenses = sum(category_totals.values())
        
        for category, amount in category_totals.items():
            percentage = (amount / total_expenses) * 100 if total_expenses > 0 else 0
            
            if percentage > 20:  # High expense category
                suggestions.append({
                    "category": category,
                    "current_amount": amount,
                    "percentage_of_total": percentage,
                    "suggestion": f"Review {category} expenses - represents {percentage:.1f}% of total",
                    "potential_savings": amount * 0.1  # Assume 10% potential savings
                })
        
        return sorted(suggestions, key=lambda x: x['potential_savings'], reverse=True)