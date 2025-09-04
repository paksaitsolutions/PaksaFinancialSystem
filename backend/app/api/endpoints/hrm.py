from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter()

@router.get("/reports/turnover")
async def get_employee_turnover_report(db: Depends(get_db)):
    # Placeholder for employee turnover report data
    turnover_data = {
        "turnover_rate": 0.15,
        "report_date": "2024-01-01",
        "employee_count": 100,
        "departed_count": 15
    }
    return turnover_data