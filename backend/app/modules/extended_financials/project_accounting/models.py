from sqlalchemy import Column, Integer, String, Date, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    budget = Column(Float, nullable=False)

class ProjectExpense(Base):
    __tablename__ = 'project_expenses'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer)
    description = Column(String)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
