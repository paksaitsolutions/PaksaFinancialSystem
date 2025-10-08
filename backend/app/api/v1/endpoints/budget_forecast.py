from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api import deps
from app.models.budget_forecast import BudgetForecast, BudgetForecastDetail, BudgetScenario
from app.schemas.budget_forecast import (
    BudgetForecast as BudgetForecastSchema,
    BudgetForecastCreate,
    BudgetForecastUpdate,
    ForecastSummary,
    ChartData,
    BudgetScenario as BudgetScenarioSchema
)
from decimal import Decimal

router = APIRouter()

@router.get("/", response_model=List[BudgetForecastSchema])
def get_forecasts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db)
):
    forecasts = db.query(BudgetForecast).offset(skip).limit(limit).all()
    return forecasts

@router.post("/", response_model=BudgetForecastSchema)
def create_forecast(
    forecast_in: BudgetForecastCreate,
    db: Session = Depends(deps.get_db)
):
    forecast = BudgetForecast(**forecast_in.dict(exclude={"forecast_details"}))
    db.add(forecast)
    db.commit()
    db.refresh(forecast)
    
    # Add forecast details
    for detail_data in forecast_in.forecast_details:
        detail = BudgetForecastDetail(**detail_data.dict(), forecast_id=forecast.id)
        db.add(detail)
    
    db.commit()
    db.refresh(forecast)
    return forecast

@router.get("/{forecast_id}", response_model=BudgetForecastSchema)
def get_forecast(
    forecast_id: int,
    db: Session = Depends(deps.get_db)
):
    forecast = db.query(BudgetForecast).filter(BudgetForecast.id == forecast_id).first()
    if not forecast:
        raise HTTPException(status_code=404, detail="Forecast not found")
    return forecast

@router.put("/{forecast_id}", response_model=BudgetForecastSchema)
def update_forecast(
    forecast_id: int,
    forecast_in: BudgetForecastUpdate,
    db: Session = Depends(deps.get_db)
):
    forecast = db.query(BudgetForecast).filter(BudgetForecast.id == forecast_id).first()
    if not forecast:
        raise HTTPException(status_code=404, detail="Forecast not found")
    
    for field, value in forecast_in.dict(exclude_unset=True).items():
        setattr(forecast, field, value)
    
    db.commit()
    db.refresh(forecast)
    return forecast

@router.delete("/{forecast_id}")
def delete_forecast(
    forecast_id: int,
    db: Session = Depends(deps.get_db)
):
    forecast = db.query(BudgetForecast).filter(BudgetForecast.id == forecast_id).first()
    if not forecast:
        raise HTTPException(status_code=404, detail="Forecast not found")
    
    db.delete(forecast)
    db.commit()
    return {"message": "Forecast deleted successfully"}

@router.post("/generate")
def generate_forecast(
    period: str,
    method: str,
    growth_rate: float,
    db: Session = Depends(deps.get_db)
):
    # Mock forecast generation logic
    base_amounts = [45000, 65000, 35000]
    categories = ["Marketing", "Operations", "IT"]
    periods = ["Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024"]
    
    forecast_details = []
    for i, period_name in enumerate(periods):
        for j, category in enumerate(categories):
            historical = base_amounts[j] * (1 + i * 0.1)
            forecast_amount = historical * (1 + growth_rate / 100)
            variance = forecast_amount - historical
            confidence = 85 - (i * 2) + (j * 1)
            
            forecast_details.append({
                "period": period_name,
                "category": category,
                "historical": historical,
                "forecast": forecast_amount,
                "variance": variance,
                "confidence": confidence
            })
    
    return {"forecast_details": forecast_details}

@router.get("/summary/{forecast_id}", response_model=ForecastSummary)
def get_forecast_summary(
    forecast_id: int,
    db: Session = Depends(deps.get_db)
):
    forecast = db.query(BudgetForecast).filter(BudgetForecast.id == forecast_id).first()
    if not forecast:
        raise HTTPException(status_code=404, detail="Forecast not found")
    
    return ForecastSummary(
        total=forecast.total_forecast,
        growth_rate=forecast.growth_rate,
        confidence=forecast.confidence_level,
        risk_level=forecast.risk_level
    )

@router.get("/chart-data/{forecast_id}", response_model=ChartData)
def get_chart_data(
    forecast_id: int,
    db: Session = Depends(deps.get_db)
):
    # Mock chart data
    return ChartData(
        labels=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        datasets=[
            {
                "label": "Historical",
                "data": [45000, 48000, 52000, 49000, 55000, 58000, 60000, 62000, 59000, 65000, 68000, 70000],
                "borderColor": "#42A5F5",
                "backgroundColor": "rgba(66, 165, 245, 0.1)",
                "fill": True
            },
            {
                "label": "Forecast",
                "data": [None, None, None, None, None, None, None, None, 64000, 69000, 74000, 79000],
                "borderColor": "#FFA726",
                "backgroundColor": "rgba(255, 167, 38, 0.1)",
                "borderDash": [5, 5],
                "fill": True
            }
        ]
    )

@router.get("/scenarios/{forecast_id}", response_model=List[BudgetScenarioSchema])
def get_scenarios(
    forecast_id: int,
    db: Session = Depends(deps.get_db)
):
    scenarios = db.query(BudgetScenario).filter(BudgetScenario.forecast_id == forecast_id).all()
    if not scenarios:
        # Create default scenarios
        default_scenarios = [
            {"scenario_type": "optimistic", "growth_rate": 15, "q1_amount": 575000, "q2_amount": 661250, "q3_amount": 760438, "q4_amount": 874504},
            {"scenario_type": "realistic", "growth_rate": 8, "q1_amount": 540000, "q2_amount": 583200, "q3_amount": 629856, "q4_amount": 680285},
            {"scenario_type": "pessimistic", "growth_rate": 3, "q1_amount": 515000, "q2_amount": 530450, "q3_amount": 546364, "q4_amount": 562754}
        ]
        
        for scenario_data in default_scenarios:
            scenario = BudgetScenario(**scenario_data, forecast_id=forecast_id)
            db.add(scenario)
        
        db.commit()
        scenarios = db.query(BudgetScenario).filter(BudgetScenario.forecast_id == forecast_id).all()
    
    return scenarios