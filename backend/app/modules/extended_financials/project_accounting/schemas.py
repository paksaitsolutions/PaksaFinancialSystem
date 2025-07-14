from pydantic import BaseModel
from datetime import date

class ProjectSchema(BaseModel):
    id: int
    name: str
    start_date: date
    end_date: date
    budget: float

class ProjectExpenseSchema(BaseModel):
    id: int
    project_id: int
    description: str
    amount: float
    date: date
