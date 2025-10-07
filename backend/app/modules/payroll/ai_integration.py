"""
Payroll AI Module - Handles AI-powered payroll queries and suggestions.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, date
import logging
from ...services.ai.module_interface import AIModule, AIResponse, ModuleResponse
from ...core.config import settings

logger = logging.getLogger(__name__)

class PayrollAIModule(AIModule):
    """AI Module for handling Payroll-related queries."""
    
    def __init__(self):
        self.name = "Payroll Assistant"
        self.description = "Handles payroll processing, tax calculations, and employee compensation queries"
        self.supported_actions = [
            "calculate_payroll",
            "explain_tax_deductions",
            "generate_payslips",
            "process_bonuses",
            "handle_overtime"
        ]
    
    @property
    def module_name(self) -> str:
        """Return the name of the module"""
        return "payroll"
    
    async def handle_query(self, query: str, context: Dict[str, Any]) -> ModuleResponse:
        """Handle a user query within this module's context"""
        ai_response = await self.process_query(query, context)
        return ModuleResponse(
            response=ai_response.answer,
            suggestions=[{"text": s, "type": "suggestion"} for s in (ai_response.suggestions or [])],
            actions=ai_response.actions
        )
    
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> AIResponse:
        """Process payroll-related queries."""
        context = context or {}
        user_id = context.get('user_id', 'unknown')
        
        try:
            logger.info(f"Processing payroll query from user {user_id}: {query}")
            
            # Route to appropriate handler based on query content
            query_lower = query.lower()
            
            if any(term in query_lower for term in ['calculate', 'run', 'process', 'payroll']):
                return await self._handle_payroll_calculation(query, context)
            elif any(term in query_lower for term in ['tax', 'deduction', 'withholding']):
                return await self._handle_tax_queries(query, context)
            elif any(term in query_lower for term in ['payslip', 'pay stub', 'earnings statement']):
                return await self._handle_payslip_queries(query, context)
            elif any(term in query_lower for term in ['bonus', 'incentive', 'commission']):
                return await self._handle_bonus_queries(query, context)
            elif any(term in query_lower for term in ['overtime', 'OT', 'over time']):
                return await self._handle_overtime_queries(query, context)
            else:
                return self._generate_response(
                    "I can help with payroll calculations, tax deductions, payslip generation, bonuses, and overtime. "
                    "Could you please provide more specific details about what you need?"
                )
                
        except Exception as e:
            error_msg = f"Error processing payroll query: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return self._generate_error_response(error_msg)
    
    async def get_suggestions(self, context: Dict[str, Any] = None) -> List[str]:
        """Get context-aware suggestions for the payroll module."""
        context = context or {}
        current_date = date.today()
        
        # Check if it's near the end of the month (common payroll period)
        if 25 <= current_date.day <= 31:
            return [
                "Run end-of-month payroll",
                "Generate payroll reports for this month",
                "Review tax withholdings for next month"
            ]
        
        return [
            "How do I process payroll for this month?",
            "Show me the payroll calendar",
            "What are the tax rates for this year?",
            "How to handle overtime payments?"
        ]
    
    async def _handle_payroll_calculation(self, query: str, context: Dict[str, Any]) -> AIResponse:
        """Handle payroll calculation queries."""
        # In a real implementation, this would connect to the payroll service
        return self._generate_response(
            "I can help you process payroll. To get started, please specify:\n"
            "1. Pay period (e.g., 'for January 2023')\n"
            "2. Employee group (e.g., 'for full-time employees')\n"
            "3. Any special considerations (e.g., 'including bonuses')"
        )
    
    async def _handle_tax_queries(self, query: str, context: Dict[str, Any]) -> AIResponse:
        """Handle tax-related queries."""
        return self._generate_response(
            "I can provide information about tax deductions. For the most accurate calculation, I need:\n"
            "1. Employee's tax filing status\n"
            "2. Number of allowances\n"
            "3. Any additional withholdings\n\n"
            "Would you like me to look up the current tax brackets and rates for you?"
        )
    
    async def _handle_payslip_queries(self, query: str, context: Dict[str, Any]) -> AIResponse:
        """Handle payslip generation queries."""
        return self._generate_response(
            "I can help generate or explain payslips. For a specific employee, please provide:\n"
            "1. Employee ID or name\n"
            "2. Pay period\n\n"
            "I can also explain different sections of a payslip if you need clarification."
        )
    
    async def _handle_bonus_queries(self, query: str, context: Dict[str, Any]) -> AIResponse:
        """Handle bonus and incentive queries."""
        return self._generate_response(
            "For bonus processing, I can help with:\n"
            "1. Calculating bonus amounts based on performance metrics\n"
            "2. Processing bonus payments with proper tax withholding\n"
            "3. Explaining different types of bonuses (e.g., annual, spot, referral)\n\n"
            "Please provide details about the type of bonus you'd like to process."
        )
    
    async def _handle_overtime_queries(self, query: str, context: Dict[str, Any]) -> AIResponse:
        """Handle overtime-related queries."""
        return self._generate_response(
            "For overtime calculations, I need to know:\n"
            "1. Employee's regular hourly rate\n"
            "2. Number of overtime hours worked\n"
            "3. Any applicable overtime multiplier (e.g., 1.5x, 2x)\n\n"
            "Would you like me to calculate overtime pay for specific employees?"
        )
    
    def _generate_response(self, message: str, **kwargs) -> AIResponse:
        """Generate a standardized AI response."""
        return AIResponse(
            answer=message,
            suggestions=kwargs.get('suggestions', []),
            actions=kwargs.get('actions', []),
            metadata={
                'module': 'payroll',
                'timestamp': datetime.utcnow().isoformat(),
                **kwargs.get('metadata', {})
            }
        )
    
    def _generate_error_response(self, error_message: str) -> AIResponse:
        """Generate an error response."""
        return AIResponse(
            answer="I'm sorry, I encountered an error processing your payroll request. "
                  "The issue has been logged and our team has been notified. "
                  "Please try again later or contact support if the issue persists.",
            metadata={
                'error': True,
                'error_message': error_message,
                'module': 'payroll',
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return the capabilities of this module."""
        return {
            'name': self.name,
            'description': self.description,
            'supported_actions': self.supported_actions,
            'version': '1.0.0',
            'last_updated': '2023-09-02'
        }
