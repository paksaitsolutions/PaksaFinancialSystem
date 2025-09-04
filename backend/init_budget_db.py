#!/usr/bin/env python3
"""
Initialize Budget Database Tables
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.database import get_db_url
from app.modules.core_financials.budget.models import Budget, BudgetLineItem

def init_budget_tables():
    """Initialize budget tables in the database"""
    
    # Create engine
    engine = create_engine(get_db_url())
    
    # Create tables
    try:
        Budget.metadata.create_all(engine)
        print("✅ Budget tables created successfully")
        
        # Insert sample data
        with engine.connect() as conn:
            # Insert sample budgets
            conn.execute(text("""
                INSERT OR IGNORE INTO budgets (id, name, amount, type, status, start_date, end_date, description, created_at, updated_at)
                VALUES 
                (1, 'Marketing Q1 2024', 50000.00, 'OPERATIONAL', 'APPROVED', '2024-01-01', '2024-03-31', 'Q1 Marketing budget', datetime('now'), datetime('now')),
                (2, 'IT Infrastructure', 100000.00, 'CAPITAL', 'APPROVED', '2024-01-01', '2024-12-31', 'Annual IT infrastructure budget', datetime('now'), datetime('now')),
                (3, 'HR Training Program', 25000.00, 'DEPARTMENT', 'DRAFT', '2024-04-01', '2024-06-30', 'Employee training and development', datetime('now'), datetime('now'))
            """))
            
            # Insert sample line items
            conn.execute(text("""
                INSERT OR IGNORE INTO budget_line_items (id, budget_id, category, description, amount, created_at, updated_at)
                VALUES 
                (1, 1, 'Digital Marketing', 'Online advertising campaigns', 30000.00, datetime('now'), datetime('now')),
                (2, 1, 'Events', 'Trade shows and conferences', 20000.00, datetime('now'), datetime('now')),
                (3, 2, 'Hardware', 'Servers and networking equipment', 70000.00, datetime('now'), datetime('now')),
                (4, 2, 'Software', 'Licenses and subscriptions', 30000.00, datetime('now'), datetime('now')),
                (5, 3, 'Training Materials', 'Books and online courses', 10000.00, datetime('now'), datetime('now')),
                (6, 3, 'External Training', 'Professional workshops', 15000.00, datetime('now'), datetime('now'))
            """))
            
            conn.commit()
            print("✅ Sample budget data inserted successfully")
            
    except Exception as e:
        print(f"❌ Error creating budget tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Initializing Budget Database Tables...")
    success = init_budget_tables()
    if success:
        print("✅ Budget module database initialization completed successfully!")
    else:
        print("❌ Budget module database initialization failed!")
        sys.exit(1)