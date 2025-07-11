"""
Schemas for BI Reporting endpoints.
"""
from pydantic import BaseModel
from typing import List, Any

class KPIReport(BaseModel):
    kpis: List[dict]

class BIDashboard(BaseModel):
    widgets: List[Any]
