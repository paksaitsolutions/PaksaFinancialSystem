"""
HRIS system integrations.
"""
import httpx
from typing import Dict, List, Any
from app.core.logging import logger

class BambooHRIntegration:
    """BambooHR HRIS integration."""
    
    def __init__(self, subdomain: str, api_key: str):
        self.subdomain = subdomain
        self.api_key = api_key
        self.base_url = f"https://api.bamboohr.com/api/gateway.php/{subdomain}/v1"
    
    async def get_employees(self) -> List[Dict[str, Any]]:
        """Get employees from BambooHR."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/employees/directory",
                auth=(self.api_key, "x")
            )
            return response.json().get("employees", [])
    
    async def get_employee_details(self, employee_id: str) -> Dict[str, Any]:
        """Get employee details."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/employees/{employee_id}",
                auth=(self.api_key, "x")
            )
            return response.json()
    
    async def sync_employee_data(self, employees: List[Dict[str, Any]]) -> bool:
        """Sync employee data to financial system."""
        try:
            for employee in employees:
                # Process employee data for payroll integration
                logger.info(f"Syncing employee {employee.get('id')}")
            return True
        except Exception as e:
            logger.error(f"Employee sync failed: {str(e)}")
            return False