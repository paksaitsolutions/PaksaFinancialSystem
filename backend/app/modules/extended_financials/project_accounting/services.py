from .models import Project, ProjectExpense
from sqlalchemy.orm import Session

class ProjectAccountingService:
    def __init__(self, db: Session):
        self.db = db

    def get_projects(self):
        return self.db.query(Project).all()

    def get_expenses(self):
        return self.db.query(ProjectExpense).all()
