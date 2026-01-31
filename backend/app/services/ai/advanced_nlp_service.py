"""
Advanced NLP service with context awareness and multi-language support.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import re


class AdvancedNLPService:
    """Advanced NLP service with context awareness."""
    
    def __init__(self):
        self.conversation_context = {}
        self.intent_patterns = {
            'financial_query': r'(revenue|income|profit|expense|cost|balance|cash|financial)',
            'comparison': r'(compare|vs|versus|against|difference|better|worse)',
            'trend_analysis': r'(trend|growth|increase|decrease|change|pattern|over time)',
            'prediction': r'(predict|forecast|estimate|project|future|next)',
            'anomaly': r'(unusual|strange|anomaly|outlier|abnormal|suspicious)',
            'customer_analysis': r'(customer|client|churn|retention|satisfaction)',
            'time_period': r'(today|yesterday|week|month|quarter|year|daily|monthly)',
            'action_request': r'(create|generate|show|display|export|send|update)'
        }
        
        self.language_patterns = {
            'english': r'[a-zA-Z\s]+',
            'spanish': r'(ingresos|gastos|beneficio|cliente|análisis|tendencia)',
            'french': r'(revenus|dépenses|profit|client|analyse|tendance)',
            'german': r'(einnahmen|ausgaben|gewinn|kunde|analyse|trend)'
        }
    
    def process_advanced_query(self, query: str, user_id: str, session_id: str) -> Dict[str, Any]:
        # Detect language
        language = self._detect_language(query)
        
        # Get conversation context
        context = self._get_conversation_context(user_id, session_id)
        
        # Extract entities and intent with context
        entities = self._extract_entities_with_context(query, context)
        intent = self._extract_intent_with_context(query, context)
        
        # Generate contextual response
        response = self._generate_contextual_response(query, intent, entities, context, language)
        
        # Update conversation context
        self._update_conversation_context(user_id, session_id, query, intent, entities)
        
        return {
            "query": query,
            "language": language,
            "intent": intent,
            "entities": entities,
            "context": context,
            "response": response,
            "suggested_actions": self._generate_suggested_actions(intent, entities),
            "confidence": self._calculate_confidence(intent, entities)
        }
    
    def _detect_language(self, query: str) -> str:
        query_lower = query.lower()
        
        for language, pattern in self.language_patterns.items():
            if re.search(pattern, query_lower):
                return language
        
        return 'english'  # Default
    
    def _get_conversation_context(self, user_id: str, session_id: str) -> Dict[str, Any]:
        context_key = f"{user_id}_{session_id}"
        return self.conversation_context.get(context_key, {
            "previous_queries": [],
            "current_topic": None,
            "user_preferences": {},
            "session_start": datetime.now()
        })
    
    def _extract_entities_with_context(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        entities = {}
        query_lower = query.lower()
        
        # Financial metrics
        if re.search(r'revenue|income|sales', query_lower):
            entities['metric'] = 'revenue'
        elif re.search(r'expense|cost|spending', query_lower):
            entities['metric'] = 'expenses'
        elif re.search(r'profit|margin|net', query_lower):
            entities['metric'] = 'profit'
        elif re.search(r'cash|balance|liquidity', query_lower):
            entities['metric'] = 'cash_flow'
        
        # Time periods
        time_entities = self._extract_time_entities(query_lower)
        if time_entities:
            entities.update(time_entities)
        
        # Amounts and numbers
        amounts = re.findall(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', query)
        if amounts:
            entities['amounts'] = [float(a.replace(',', '')) for a in amounts]
        
        # Account references
        accounts = re.findall(r'account\s+(\w+)', query_lower)
        if accounts:
            entities['accounts'] = accounts
        
        # Context-based entity resolution
        if context.get('current_topic') and not entities.get('metric'):
            entities['metric'] = context['current_topic']
        
        return entities
    
    def _extract_intent_with_context(self, query: str, context: Dict[str, Any]) -> str:
        query_lower = query.lower()
        
        # Primary intent detection
        for intent_type, pattern in self.intent_patterns.items():
            if re.search(pattern, query_lower):
                # Context-aware intent refinement
                if intent_type == 'financial_query' and context.get('previous_queries'):
                    last_query = context['previous_queries'][-1] if context['previous_queries'] else {}
                    if last_query.get('intent') == 'comparison':
                        return 'follow_up_comparison'
                
                return intent_type
        
        # Contextual intent inference
        if context.get('current_topic'):
            if re.search(r'more|details|explain|why', query_lower):
                return 'elaboration_request'
            elif re.search(r'different|other|alternative', query_lower):
                return 'alternative_request'
        
        return 'general_inquiry'
    
    def _extract_time_entities(self, query: str) -> Dict[str, Any]:
        time_entities = {}
        
        # Relative time
        if re.search(r'last\s+(week|month|quarter|year)', query):
            match = re.search(r'last\s+(\w+)', query)
            time_entities['period'] = f"last_{match.group(1)}"
        elif re.search(r'this\s+(week|month|quarter|year)', query):
            match = re.search(r'this\s+(\w+)', query)
            time_entities['period'] = f"current_{match.group(1)}"
        elif re.search(r'next\s+(week|month|quarter|year)', query):
            match = re.search(r'next\s+(\w+)', query)
            time_entities['period'] = f"next_{match.group(1)}"
        
        # Specific dates
        date_patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # MM/DD/YYYY
            r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, query)
            if match:
                time_entities['specific_date'] = match.group(0)
                break
        
        return time_entities
    
    def _generate_contextual_response(
        self, 
        query: str, 
        intent: str, 
        entities: Dict[str, Any], 
        context: Dict[str, Any],
        language: str
    ) -> str:
        """ Generate Contextual Response."""
        """Generate contextual response based on intent and entities."""
        
        responses = {
            'english': {
                'financial_query': "I'll help you analyze the {metric} data{time_phrase}.",
                'comparison': "Let me compare {metric} across the specified periods.",
                'trend_analysis': "I'll analyze the {metric} trends{time_phrase}.",
                'prediction': "Based on historical data, here's the {metric} forecast{time_phrase}.",
                'anomaly': "I've detected some unusual patterns in your {metric} data.",
                'customer_analysis': "Here's the customer analysis you requested.",
                'follow_up_comparison': "Building on our previous comparison, here's additional analysis.",
                'elaboration_request': "Let me provide more details about {topic}.",
                'general_inquiry': "I understand you're asking about financial data. How can I help?"
            },
            'spanish': {
                'financial_query': "Te ayudaré a analizar los datos de {metric}{time_phrase}.",
                'comparison': "Permíteme comparar {metric} en los períodos especificados.",
                'trend_analysis': "Analizaré las tendencias de {metric}{time_phrase}.",
                'general_inquiry': "Entiendo que preguntas sobre datos financieros. ¿Cómo puedo ayudar?"
            }
        }
        
        lang_responses = responses.get(language, responses['english'])
        response_template = lang_responses.get(intent, lang_responses['general_inquiry'])
        
        # Format response with entities
        metric = entities.get('metric', 'financial data')
        time_phrase = f" for {entities.get('period', '')}" if entities.get('period') else ""
        topic = context.get('current_topic', 'the topic')
        
        return response_template.format(
            metric=metric,
            time_phrase=time_phrase,
            topic=topic
        )
    
    def _generate_suggested_actions(self, intent: str, entities: Dict[str, Any]) -> List[str]:
        suggestions = []
        
        if intent == 'financial_query':
            suggestions.extend([
                "View detailed breakdown",
                "Compare with previous period",
                "Export to Excel",
                "Set up alerts"
            ])
        elif intent == 'trend_analysis':
            suggestions.extend([
                "Forecast future trends",
                "Identify key drivers",
                "Create dashboard",
                "Schedule regular reports"
            ])
        elif intent == 'comparison':
            suggestions.extend([
                "Analyze variance reasons",
                "Drill down by category",
                "View graphical comparison",
                "Save comparison template"
            ])
        elif intent == 'prediction':
            suggestions.extend([
                "Adjust forecast parameters",
                "View confidence intervals",
                "Compare scenarios",
                "Set prediction alerts"
            ])
        
        return suggestions[:4]  # Limit to 4 suggestions
    
    def _calculate_confidence(self, intent: str, entities: Dict[str, Any]) -> float:
        base_confidence = 0.7
        
        # Boost confidence for specific entities
        if entities.get('metric'):
            base_confidence += 0.1
        if entities.get('period'):
            base_confidence += 0.1
        if entities.get('amounts'):
            base_confidence += 0.05
        
        # Intent-specific confidence adjustments
        high_confidence_intents = ['financial_query', 'comparison', 'trend_analysis']
        if intent in high_confidence_intents:
            base_confidence += 0.05
        
        return min(0.95, base_confidence)
    
    def _update_conversation_context(
        self, 
        user_id: str, 
        session_id: str, 
        query: str, 
        intent: str, 
        entities: Dict[str, Any]
    ) -> None:
        """ Update Conversation Context."""
        """Update conversation context."""
        context_key = f"{user_id}_{session_id}"
        
        if context_key not in self.conversation_context:
            self.conversation_context[context_key] = {
                "previous_queries": [],
                "current_topic": None,
                "user_preferences": {},
                "session_start": datetime.now()
            }
        
        context = self.conversation_context[context_key]
        
        # Add to query history
        context["previous_queries"].append({
            "query": query,
            "intent": intent,
            "entities": entities,
            "timestamp": datetime.now()
        })
        
        # Keep only last 10 queries
        context["previous_queries"] = context["previous_queries"][-10:]
        
        # Update current topic
        if entities.get('metric'):
            context["current_topic"] = entities['metric']
        
        # Clean up old sessions (older than 1 hour)
        cutoff_time = datetime.now() - timedelta(hours=1)
        keys_to_remove = [
            key for key, ctx in self.conversation_context.items()
            if ctx.get("session_start", datetime.now()) < cutoff_time
        ]
        for key in keys_to_remove:
            del self.conversation_context[key]