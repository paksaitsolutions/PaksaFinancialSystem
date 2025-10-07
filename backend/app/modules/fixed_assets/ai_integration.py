"""
Fixed Assets AI Module - Handles AI-powered fixed assets management queries.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, date, timedelta
import logging
from ...services.ai.module_interface import AIModule, AIResponse, ModuleResponse
from ...core.config import settings

logger = logging.getLogger(__name__)

class FixedAssetsAIModule(AIModule):
    """AI Module for handling Fixed Assets related queries."""
    
    def __init__(self):
        self.name = "Fixed Assets Assistant"
        self.description = "Manages fixed assets tracking, depreciation, and reporting"
        self.supported_actions = [
            "track_asset",
            "calculate_depreciation",
            "generate_asset_reports",
            "manage_disposals",
            "schedule_maintenance"
        ]
        self.current_year = date.today().year
    
    @property
    def module_name(self) -> str:
        """Return the name of the module"""
        return "fixed_assets"
    
    async def handle_query(self, query: str, context: Dict[str, Any]) -> ModuleResponse:
        """Handle a user query within this module's context"""
        ai_response = await self.process_query(query, context)
        return ModuleResponse(
            response=ai_response.answer,
            suggestions=[{"text": s, "type": "suggestion"} for s in (ai_response.suggestions or [])],
            actions=ai_response.actions
        )
    
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> AIResponse:
        """Process fixed assets related queries."""
        context = context or {}
        user_id = context.get('user_id', 'unknown')
        
        try:
            logger.info(f"Processing fixed assets query from user {user_id}: {query}")
            query_lower = query.lower()
            
            if any(term in query_lower for term in ['add', 'new', 'register', 'track']):
                return await self._handle_asset_registration(query, context)
            elif any(term in query_lower for term in ['depreciation', 'amortization']):
                return await self._handle_depreciation_queries(query, context)
            elif any(term in query_lower for term in ['report', 'list', 'inventory']):
                return await self._handle_reporting_queries(query, context)
            elif any(term in query_lower for term in ['dispose', 'sell', 'retire', 'write off']):
                return await self._handle_disposal_queries(query, context)
            elif any(term in query_lower for term in ['maintain', 'service', 'repair']):
                return await self._handle_maintenance_queries(query, context)
            else:
                return self._generate_response(
                    "I can help with fixed assets management including tracking, depreciation, "
                    "reporting, disposals, and maintenance. How can I assist you today?"
                )
                
        except Exception as e:
            error_msg = f"Error processing fixed assets query: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return self._generate_error_response(error_msg)
    
    async def get_suggestions(self, context: Dict[str, Any] = None) -> List[str]:
        """Get context-aware suggestions for the fixed assets module."""
        current_date = date.today()
        quarter = (current_date.month - 1) // 3 + 1
        
        suggestions = [
            "How do I add a new asset?",
            f"Show me assets requiring maintenance in Q{quarter}",
            "Generate a depreciation schedule",
            "What's the current book value of our assets?"
        ]
        
        # Add year-end specific suggestions
        if current_date.month == 12:
            suggestions.append("Prepare year-end fixed assets report")
            suggestions.append("Review assets for impairment")
            
        return suggestions
    
    async def _handle_asset_registration(self, query: str, context: Dict[str, Any]) -> AIResponse:
        """Handle new asset registration queries."""
        return self._generate_response(
            "To register a new fixed asset, I'll need the following details:\n\n"
            "1. Asset description and category (e.g., Equipment, Vehicles, Buildings)\n"
            "2. Purchase date and cost\n"
            "3. Expected useful life (in years)\n"
            "4. Depreciation method (e.g., Straight-line, Double-declining)\n"
            "5. Location and custodian information\n\n"
            "Would you like to start the asset registration process now?"
        )
    
    async def _handle_depreciation_queries(self, query: str, context: Dict[str, Any]) -> AIResponse:
        """Handle depreciation calculation queries."""
        return self._generate_response(
            f"I can help with {self.current_year} depreciation calculations. Please specify:\n\n"
            "1. The asset or asset category you're interested in\n"
            "2. The depreciation method to use (if not using default)\n"
            "3. Any special considerations (e.g., bonus depreciation, Section 179)\n\n"
            "Would you like me to calculate depreciation for a specific asset or see the annual schedule?"
        )
    
    async def _handle_reporting_queries(self, query: str, context: Dict[str, Any]) -> AIResponse:
        """Handle asset reporting queries."""
        return self._generate_response(
            f"I can generate various fixed assets reports for {self.current_year}:\n\n"
            "1. Asset Register (complete listing of all assets)\n"
            "2. Depreciation Schedule (current and projected)\n"
            "3. Maintenance History Report\n"
            "4. Disposal Report\n"
            "5. Tax Reporting Package\n\n"
            "Which report would you like to generate?"
        )
    
    async def _handle_disposal_queries(self, query: str, context: Dict[str, Any]) -> AIResponse:
        """Handle asset disposal queries."""
        return self._generate_response(
            "To process an asset disposal, I'll need:\n\n"
            "1. Asset ID or description\n"
            "2. Disposal date\n"
            "3. Disposal method (sold, scrapped, stolen, etc.)\n"
            "4. If sold, the sale price\n\n"
            "Would you like to record a disposal now?"
        )
    
    async def _handle_maintenance_queries(self, query: str, context: Dict[str, Any]) -> AIResponse:
        """Handle maintenance scheduling queries."""
        return self._generate_response(
            "I can help manage asset maintenance. Please specify:\n\n"
            "1. The asset needing maintenance\n"
            "2. Type of maintenance (preventive, corrective, etc.)\n"
            "3. Any error messages or issues (if applicable)\n\n"
            "Would you like to schedule new maintenance or check upcoming schedules?"
        )
    
    def _generate_response(self, message: str, **kwargs) -> AIResponse:
        """Generate a standardized AI response."""
        return AIResponse(
            answer=message,
            suggestions=kwargs.get('suggestions', []),
            actions=kwargs.get('actions', []),
            metadata={
                'module': 'fixed_assets',
                'timestamp': datetime.utcnow().isoformat(),
                **kwargs.get('metadata', {})
            }
        )
    
    def _generate_error_response(self, error_message: str) -> AIResponse:
        """Generate an error response."""
        return AIResponse(
            answer="I'm sorry, I encountered an error processing your fixed assets request. "
                  "The issue has been logged and our team has been notified. "
                  "Please try again later or contact support if the issue persists.",
            metadata={
                'error': True,
                'error_message': error_message,
                'module': 'fixed_assets',
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
            'last_updated': '2023-09-02',
            'supported_asset_types': ['Tangible', 'Intangible', 'Leasehold Improvements']
        }
