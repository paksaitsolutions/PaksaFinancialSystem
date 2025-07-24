import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class NLPService:
    def __init__(self):
        self.query_patterns = {
            'revenue': r'(revenue|income|sales|earnings)',
            'expenses': r'(expense|cost|spending|expenditure)',
            'profit': r'(profit|margin|net income)',
            'cash': r'(cash|balance|liquidity)',
            'customer': r'(customer|client)',
            'invoice': r'(invoice|bill)',
            'payment': r'(payment|pay|paid)',
            'time_period': r'(last|past|previous|this|current)\s+(month|quarter|year|week)',
            'comparison': r'(compare|vs|versus|against)',
            'trend': r'(trend|growth|increase|decrease|change)'
        }
    
    def process_natural_query(self, query: str) -> Dict[str, Any]:
        """Process natural language query and return structured response"""
        query_lower = query.lower()
        
        # Extract intent and entities
        intent = self._extract_intent(query_lower)
        entities = self._extract_entities(query_lower)
        time_period = self._extract_time_period(query_lower)
        
        # Generate response based on intent
        response = self._generate_response(intent, entities, time_period, query)
        
        return {
            "query": query,
            "intent": intent,
            "entities": entities,
            "time_period": time_period,
            "response": response,
            "sql_query": self._generate_sql_query(intent, entities, time_period)
        }
    
    def _extract_intent(self, query: str) -> str:
        """Extract the main intent from the query"""
        if re.search(r'show|display|get|what', query):
            if re.search(self.query_patterns['revenue'], query):
                return 'show_revenue'
            elif re.search(self.query_patterns['expenses'], query):
                return 'show_expenses'
            elif re.search(self.query_patterns['profit'], query):
                return 'show_profit'
            elif re.search(self.query_patterns['cash'], query):
                return 'show_cash_balance'
            elif re.search(self.query_patterns['customer'], query):
                return 'show_customers'
            elif re.search(self.query_patterns['invoice'], query):
                return 'show_invoices'
        
        if re.search(r'compare|comparison', query):
            return 'compare_metrics'
        
        if re.search(self.query_patterns['trend'], query):
            return 'show_trend'
        
        return 'general_inquiry'
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract entities from the query"""
        entities = []
        
        for entity_type, pattern in self.query_patterns.items():
            if re.search(pattern, query):
                entities.append(entity_type)
        
        return entities
    
    def _extract_time_period(self, query: str) -> Optional[str]:
        """Extract time period from the query"""
        time_match = re.search(self.query_patterns['time_period'], query)
        if time_match:
            return time_match.group()
        
        # Check for specific months/years
        month_match = re.search(r'(january|february|march|april|may|june|july|august|september|october|november|december)', query)
        if month_match:
            return month_match.group()
        
        year_match = re.search(r'20\d{2}', query)
        if year_match:
            return year_match.group()
        
        return None
    
    def _generate_response(self, intent: str, entities: List[str], time_period: Optional[str], original_query: str) -> str:
        """Generate a natural language response"""
        time_phrase = f" for {time_period}" if time_period else ""
        
        responses = {
            'show_revenue': f"Here's the revenue information{time_phrase}:",
            'show_expenses': f"Here are the expense details{time_phrase}:",
            'show_profit': f"Here's the profit analysis{time_phrase}:",
            'show_cash_balance': f"Here's the current cash balance{time_phrase}:",
            'show_customers': f"Here's the customer information{time_phrase}:",
            'show_invoices': f"Here are the invoice details{time_phrase}:",
            'compare_metrics': f"Here's the comparison{time_phrase}:",
            'show_trend': f"Here's the trend analysis{time_phrase}:",
            'general_inquiry': "I'll help you find that information."
        }
        
        return responses.get(intent, "I understand you're asking about financial data. Let me help you with that.")
    
    def _generate_sql_query(self, intent: str, entities: List[str], time_period: Optional[str]) -> str:
        """Generate SQL query based on intent and entities"""
        base_queries = {
            'show_revenue': "SELECT SUM(amount) as total_revenue FROM transactions WHERE type = 'revenue'",
            'show_expenses': "SELECT SUM(amount) as total_expenses FROM transactions WHERE type = 'expense'",
            'show_profit': "SELECT (SELECT SUM(amount) FROM transactions WHERE type = 'revenue') - (SELECT SUM(amount) FROM transactions WHERE type = 'expense') as profit",
            'show_cash_balance': "SELECT SUM(CASE WHEN type = 'revenue' THEN amount ELSE -amount END) as cash_balance FROM transactions",
            'show_customers': "SELECT * FROM customers",
            'show_invoices': "SELECT * FROM invoices"
        }
        
        query = base_queries.get(intent, "SELECT 1")
        
        # Add time filter if specified
        if time_period and 'transactions' in query:
            if 'last month' in time_period:
                query += " AND created_at >= DATE_SUB(NOW(), INTERVAL 1 MONTH)"
            elif 'this year' in time_period:
                query += " AND YEAR(created_at) = YEAR(NOW())"
        
        return query