from pydantic import BaseModel

class MultiCurrencyBalances(BaseModel):
    balances: dict

class BudgetReport(BaseModel):
    budgets: list

class ConsolidationReport(BaseModel):
    entities: list