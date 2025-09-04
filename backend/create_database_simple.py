"""
Simple database creation script
"""
from sqlalchemy import create_engine
from app.models.base import Base
from app.models.user_enhanced import *
from app.models.financial_core import *

# Create database
engine = create_engine("sqlite:///./paksa_financial.db", echo=True)

# Create all tables
Base.metadata.create_all(bind=engine)

print("Database created successfully with all tables!")
print("Tables created:")
for table in Base.metadata.tables.keys():
    print(f"  - {table}")