def test_budget_model():
    from .models import Budget
    budget = Budget(id=1, name='Annual Budget', start_date='2025-01-01', end_date='2025-12-31', total_amount=100000.0)
    assert budget.name == 'Annual Budget'
    assert budget.total_amount == 100000.0

def test_budget_item_model():
    from .models import BudgetItem
    item = BudgetItem(id=1, budget_id=1, name='Marketing', amount=5000.0)
    assert item.name == 'Marketing'
    assert item.amount == 5000.0
