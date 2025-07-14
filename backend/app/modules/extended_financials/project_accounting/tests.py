def test_project_model():
    from .models import Project
    project = Project(id=1, name='ERP Implementation', start_date='2025-01-01', end_date='2025-12-31', budget=50000.0)
    assert project.name == 'ERP Implementation'
    assert project.budget == 50000.0

def test_project_expense_model():
    from .models import ProjectExpense
    expense = ProjectExpense(id=1, project_id=1, description='Consulting', amount=10000.0, date='2025-02-01')
    assert expense.description == 'Consulting'
    assert expense.amount == 10000.0
