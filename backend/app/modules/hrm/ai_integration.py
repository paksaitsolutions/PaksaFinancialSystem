"""
HRM Module AI Integration
Handles AI assistant functionality specific to the HRM module.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from ...services.ai.module_interface import AIModule, ModuleResponse
from ...models.core_models import Employee
# from ...crud.hrm.employee import get_employees, get_employee

class HRMAIModule(AIModule):
    """AI integration for HRM module"""
    
    @property
    def module_name(self) -> str:
        return "hrm"
    
    async def handle_query(self, query: str, context: Dict[str, Any]) -> ModuleResponse:
        """Handle HRM-specific queries"""
        query = query.lower()
        
        # Handle leave requests
        if any(term in query for term in ["leave", "time off", "vacation"]):
            return await self._handle_leave_queries(query, context)
            
        # Handle employee-related queries
        elif any(term in query for term in ["employee", "staff", "team member"]):
            return await self._handle_employee_queries(query, context)
            
        # Handle general HRM queries
        return ModuleResponse(
            response="I can help you with various HRM tasks. You can ask about employees, leave requests, or other HR-related matters.",
            suggestions=[
                {"text": "Show me active employees", "type": "query"},
                {"text": "How many people are on leave today?", "type": "query"},
                {"text": "Create a new leave request", "type": "action"}
            ]
        )
    
    async def _handle_leave_queries(self, query: str, context: Dict[str, Any]) -> ModuleResponse:
        """Handle leave-related queries"""
        if any(term in query for term in ["create", "new", "request"]):
            return ModuleResponse(
                response="I can help you create a new leave request. Please provide the employee name and the leave dates.",
                requires_confirmation=True,
                actions=[{"type": "navigate", "path": "/hrm/leave/requests/new"}]
            )
            
        elif any(term in query for term in ["check", "status", "balance"]):
            return await self._get_leave_balance(query, context)
            
        return ModuleResponse(
            response="I can help you with leave requests. You can create a new request, check leave balances, or view the leave calendar.",
            suggestions=[
                {"text": "Check my leave balance", "type": "query"},
                {"text": "View leave calendar", "type": "action"}
            ]
        )
    
    async def _handle_employee_queries(self, query: str, context: Dict[str, Any]) -> ModuleResponse:
        """Handle employee-related queries"""
        if any(term in query for term in ["list", "show", "all"]):
            # Mock employee data for now
            employees = [{"full_name": "John Doe", "position": "Manager"}, {"full_name": "Jane Smith", "position": "Developer"}]
            employee_names = [f"- {emp['full_name']} ({emp['position']})" for emp in employees[:5]]
            if len(employees) > 5:
                employee_names.append(f"... and {len(employees) - 5} more")
                
            return ModuleResponse(
                response=f"Here are the employees in the system:\n" + "\n".join(employee_names),
                actions=[{"type": "navigate", "path": "/hrm/employees"}]
            )
            
        return ModuleResponse(
            response="I can help you find information about employees. You can ask to list all employees or search for specific ones.",
            suggestions=[
                {"text": "List all employees", "type": "query"},
                {"text": "Search for an employee", "type": "search"}
            ]
        )
    
    async def _get_leave_balance(self, query: str, context: Dict[str, Any]) -> ModuleResponse:
        """Get leave balance for an employee"""
        # In a real implementation, this would fetch actual data
        return ModuleResponse(
            response="Your current leave balance is:\n- Annual Leave: 15 days\n- Sick Leave: 10 days\n- Personal Leave: 5 days",
            actions=[{"type": "navigate", "path": "/hrm/leave/balance"}]
        )
    
    async def get_suggestions(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        """Get contextual suggestions for HRM"""
        return [
            {"text": "Create new employee", "type": "action"},
            {"text": "View leave calendar", "type": "action"},
            {"text": "Generate HR report", "type": "action"},
            {"text": "Check team attendance", "type": "query"}
        ]
    
    async def get_module_info(self) -> Dict[str, Any]:
        return {
            "name": self.module_name,
            "description": "Human Resource Management module for employee and leave management",
            "capabilities": [
                "Employee management",
                "Leave request processing",
                "Attendance tracking",
                "HR reporting"
            ]
        }
