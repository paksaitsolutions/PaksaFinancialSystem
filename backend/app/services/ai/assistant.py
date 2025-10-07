"""
AI Assistant Core Service
Handles the main AI assistant functionality including context management,
module integration, and response generation.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import logging
from datetime import datetime, timedelta
from functools import wraps

def handle_ai_errors(func):
    """Decorator to handle AI errors gracefully"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            return {"error": str(e), "status": "error"}
    return wrapper

logger = logging.getLogger(__name__)

class AssistantContext(BaseModel):
    """Context for the AI assistant"""
    module: str
    user_id: str
    session_id: str
    metadata: Dict[str, Any] = {}

class AIModelConfig(BaseModel):
    """Configuration for AI models"""
    model_name: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 1000

class AIAssistant:
    """
    Core AI Assistant service that manages AI modules and processes queries.
    
    Features:
    - Module registration and management
    - Context-aware query processing
    - Comprehensive error handling and logging
    - Request tracing and monitoring
    - Performance metrics collection
    """
    
    def __init__(self, debug_mode: bool = False):
        """
        Initialize the AI Assistant.
        
        Args:
            debug_mode: If True, enables additional debug information in responses
        """
        self.modules: Dict[str, Any] = {}
        self.context_history: Dict[str, List[Dict[str, Any]]] = {}
        self.request_count = 0
        self.error_count = 0
        self.start_time = datetime.utcnow()
        self.debug_mode = debug_mode
        
        logger.info("AI Assistant initialized", extra={
            'start_time': self.start_time.isoformat(),
            'debug_mode': debug_mode
        })
    
    @handle_ai_errors
    async def register_module(self, module_id: str, module: Any) -> Dict[str, Any]:
        """
        Register an AI module with the assistant.
        
        Args:
            module_id: Unique identifier for the module
            module: Instance of the AI module
            
        Returns:
            Dict with registration status and module info
        """
        if module_id in self.modules:
            logger.warning(f"Module {module_id} is already registered. Overwriting.")
            
        self.modules[module_id] = module
        
        # Get module capabilities for logging
        capabilities = getattr(module, 'get_capabilities', lambda: {})()
        
        logger.info(
            f"Registered AI module: {module_id}",
            extra={
                'module_id': module_id,
                'module_name': getattr(module, 'name', 'Unknown'),
                'capabilities': capabilities
            }
        )
        
        return {
            'status': 'success',
            'module_id': module_id,
            'module_name': getattr(module, 'name', 'Unknown'),
            'capabilities': capabilities,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    @handle_ai_errors
    async def process_query(
        self, 
        user_id: str, 
        module: Optional[str] = None,
        query: str = "",
        context: Dict[str, Any] = None
    ) -> Dict:
        """
        Process a user query through the appropriate AI module.
        
        Args:
            user_id: ID of the user making the request
            module: Optional module ID to direct the query to
            query: The user's query text
            context: Additional context for the query
            
        Returns:
            Dict with the module's response
        """
        context = context or {}
        self.request_count += 1
        
        # Enrich context with metadata
        context.update({
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'request_id': context.get('request_id', f"req_{self.request_count:08d}")
        })
        
        # Update context history (keep last 100 interactions per user)
        if user_id not in self.context_history:
            self.context_history[user_id] = []
            
        self.context_history[user_id].append({
            "query": query,
            "context": {k: v for k, v in context.items() if k != 'auth_token'},  # Don't log auth tokens
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep only the last 100 interactions per user
        self.context_history[user_id] = self.context_history[user_id][-100:]
        
        # Log the query
        logger.info(
            "Processing AI query",
            extra={
                'request_id': context['request_id'],
                'user_id': user_id,
                'module': module,
                'query': query,
                'context_keys': list(context.keys())
            }
        )
        
        # If no module specified, try to determine it from context or query
        if not module:
            module = self._determine_module(query, context)
            logger.debug(
                f"Determined module '{module}' for query",
                extra={'request_id': context['request_id']}
            )
        
        # If still no module or module not found, return fallback
        if not module or module not in self.modules:
            logger.warning(
                f"Module '{module}' not found for query",
                extra={
                    'request_id': context['request_id'],
                    'available_modules': list(self.modules.keys())
                }
            )
            return self._generate_fallback_response(query, context)
        
        # Process the query with the selected module
        start_time = datetime.utcnow()
        try:
            response = await self.modules[module].process_query(query, context)
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Log successful processing
            logger.info(
                f"Successfully processed query with module '{module}'",
                extra={
                    'request_id': context['request_id'],
                    'module': module,
                    'processing_time_seconds': processing_time,
                    'response_type': type(response).__name__
                }
            )
            
            # Add performance metrics to response metadata
            if not isinstance(response, dict) or 'metadata' not in response:
                response['metadata'] = {}
                
            response['metadata'].update({
                'processing_time_seconds': processing_time,
                'module': module,
                'module_version': getattr(self.modules[module], 'version', '1.0.0'),
                'request_id': context['request_id']
            })
            
            return response
            
        except Exception as e:
            self.error_count += 1
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            logger.error(
                f"Error processing query in module '{module}': {str(e)}",
                exc_info=True,
                extra={
                    'request_id': context['request_id'],
                    'module': module,
                    'processing_time_seconds': processing_time,
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                }
            )
            
            # Generate error response with request ID for tracking
            return {
                "answer": (
                    "I'm sorry, I encountered an error processing your request. "
                    f"Reference ID: {context['request_id']}. Please try again later."
                ),
                "metadata": {
                    'error': True,
                    'request_id': context['request_id'],
                    'module': module,
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'processing_time_seconds': processing_time,
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
    
    @handle_ai_errors
    async def get_suggestions(
        self, 
        user_id: str, 
        module: Optional[str] = None,
        context: Dict[str, Any] = None
    ) -> List[str]:
        """
        Get context-aware suggestions from the specified or most relevant modules.
        
        Args:
            user_id: ID of the user requesting suggestions
            module: Optional module ID to get suggestions from
            context: Additional context for generating suggestions
            
        Returns:
            List of suggestion strings
        """
        context = context or {}
        context['user_id'] = user_id
        
        # If module is specified, get suggestions only from that module
        if module and module in self.modules:
            try:
                return await self.modules[module].get_suggestions(context)
            except Exception as e:
                logger.error(
                    f"Error getting suggestions from module '{module}': {str(e)}",
                    exc_info=True,
                    extra={
                        'user_id': user_id,
                        'module': module,
                        'error_type': type(e).__name__
                    }
                )
                return []
        
        # If no module specified, get suggestions from all modules
        all_suggestions = []
        for mod_id, mod in self.modules.items():
            try:
                suggestions = await mod.get_suggestions(context)
                if suggestions:
                    all_suggestions.extend(suggestions)
            except Exception as e:
                logger.error(
                    f"Error getting suggestions from module '{mod_id}': {str(e)}",
                    exc_info=True,
                    extra={
                        'user_id': user_id,
                        'module': mod_id,
                        'error_type': type(e).__name__
                    }
                )
        
        # Return a randomized selection of suggestions (up to 10)
        import random
        random.shuffle(all_suggestions)
        return all_suggestions[:10]
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get performance and usage metrics for the AI Assistant.
        
        Returns:
            Dict containing various metrics
        """
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        return {
            'start_time': self.start_time.isoformat(),
            'uptime_seconds': uptime,
            'uptime_human_readable': str(timedelta(seconds=int(uptime))),
            'total_requests': self.request_count,
            'total_errors': self.error_count,
            'error_rate': self.error_count / max(self.request_count, 1),
            'modules_registered': len(self.modules),
            'module_names': list(self.modules.keys()),
            'active_users': len(self.context_history)
        }
    
    def _determine_module(self, query: str, context: Dict[str, Any]) -> Optional[str]:
        """
        Determine the most relevant module for a query using keyword matching.
        
        Args:
            query: The user's query text
            context: Additional context
            
        Returns:
            Module ID or None if no match found
        """
        query_lower = query.lower()
        
        # Define module keywords with weights
        module_keywords = {
            'hrm': [
                ('employee', 2), ('leave', 3), ('attendance', 2), 
                ('payroll', 3), ('staff', 1), ('team', 1), ('vacation', 2),
                ('sick', 1), ('time off', 2), ('holiday', 1), ('benefit', 2)
            ],
            'finance': [
                ('invoice', 3), ('payment', 2), ('transaction', 2), 
                ('expense', 2), ('revenue', 2), ('budget', 3), ('forecast', 2),
                ('financial', 2), ('report', 1), ('cash flow', 2), ('reconcile', 2)
            ],
            'inventory': [
                ('stock', 3), ('item', 2), ('product', 2), ('supply', 2), 
                ('warehouse', 2), ('inventory', 3), ('reorder', 2), ('supplier', 1),
                ('stock level', 2), ('low stock', 2), ('out of stock', 3)
            ],
            'payroll': [
                ('payroll', 3), ('salary', 2), ('wage', 2), ('paycheck', 2),
                ('deduction', 2), ('tax', 2), ('withholding', 2), ('bonus', 1),
                ('overtime', 2), ('payslip', 2), ('compensation', 1)
            ],
            'tax': [
                ('tax', 3), ('withholding', 2), ('deduction', 2), ('filing', 2),
                ('irs', 2), ('form', 1), ('w-2', 3), ('1099', 3), ('withhold', 2),
                ('taxable', 2), ('deductible', 2), ('tax return', 3)
            ],
            'fixed_assets': [
                ('asset', 3), ('depreciation', 3), ('amortization', 2), ('capital', 2),
                ('equipment', 2), ('property', 1), ('plant', 1), ('ppe', 2),
                ('fixed asset', 3), ('book value', 2), ('disposal', 2), ('impairment', 2)
            ]
        }
        
        # Calculate scores for each module
        scores = {module: 0 for module in module_keywords}
        
        for module, keywords in module_keywords.items():
            for keyword, weight in keywords:
                if keyword in query_lower:
                    scores[module] += weight
        
        # Get the module with the highest score
        if scores:
            max_score = max(scores.values())
            if max_score > 0:
                # Get all modules with the max score
                best_modules = [m for m, s in scores.items() if s == max_score]
                # Return the first one (or random if there's a tie)
                import random
                return random.choice(best_modules)
        
        # If no module scored, try to use the last used module from context
        last_module = context.get('last_module')
        if last_module and last_module in self.modules:
            return last_module
            
        # Default to None if no match found
        return None
    
    def _generate_fallback_response(self, query: str, context: Dict[str, Any]) -> Dict:
        """
        Generate a fallback response when no module is found.
        
        Args:
            query: The user's query
            context: Additional context
            
        Returns:
            Dict with a helpful message
        """
        available_modules = ", ".join([f"'{m}'" for m in sorted(self.modules.keys())])
        
        # Try to provide more specific guidance based on query content
        if not query.strip():
            message = "I didn't receive any input. How can I assist you today?"
        elif '?' not in query and len(query.split()) < 3:
            message = (
                f"I'm not sure what you're asking. Could you please provide more details? "
                f"For example, you can ask about specific modules like: {available_modules}."
            )
        else:
            message = (
                f"I'm not sure which module can best handle your request. "
                f"Available modules are: {available_modules}. "
                "Please try rephrasing or specify a module."
            )
        
        return {
            "answer": message,
            "metadata": {
                'fallback': True,
                'available_modules': list(self.modules.keys()),
                'request_id': context.get('request_id', 'unknown'),
                'timestamp': datetime.utcnow().isoformat()
            }
        }

# Singleton instance
assistant = AIAssistant()
