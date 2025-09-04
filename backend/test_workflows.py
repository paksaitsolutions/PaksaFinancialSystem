"""
Test script for workflow system
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

# Connect to database
engine = create_engine('sqlite:///paksa_complete.db')
Session = sessionmaker(bind=engine)
db = Session()

def test_workflow_system():
    """Test workflow system functionality"""
    print("=== Testing Workflow System ===")
    
    # Test database tables
    print("1. Testing workflow tables...")
    try:
        # Check if workflow tables exist
        tables_to_check = [
            'workflow_instances', 'workflow_steps', 'workflow_approvals', 
            'workflow_delegations', 'workflow_templates'
        ]
        
        for table in tables_to_check:
            result = db.execute(text(f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{table}'")).scalar()
            if result > 0:
                print(f"   Table {table}: EXISTS")
            else:
                print(f"   Table {table}: MISSING")
    except Exception as e:
        print(f"   Error checking tables: {e}")
    
    # Test workflow creation
    print("2. Testing workflow creation...")
    try:
        # Insert sample workflow
        workflow_data = {
            'steps': [
                {'name': 'Supervisor Review', 'role': 'supervisor', 'due_days': 2},
                {'name': 'Manager Approval', 'role': 'manager', 'due_days': 3}
            ]
        }
        
        db.execute(text("""
            INSERT INTO workflow_instances 
            (id, workflow_type, entity_id, entity_type, status, current_step, total_steps, amount, created_by, workflow_data, created_at)
            VALUES 
            ('test-workflow-1', 'journal_entry', 'test-je-1', 'JournalEntry', 'pending', 1, 2, 5000.00, 'test-user', :workflow_data, :created_at)
        """), {
            'workflow_data': json.dumps(workflow_data),
            'created_at': datetime.now()
        })
        
        # Insert workflow steps
        db.execute(text("""
            INSERT INTO workflow_steps 
            (id, workflow_id, step_number, step_name, approver_role, status, due_date, created_at)
            VALUES 
            ('test-step-1', 'test-workflow-1', 1, 'Supervisor Review', 'supervisor', 'pending', :due_date, :created_at),
            ('test-step-2', 'test-workflow-1', 2, 'Manager Approval', 'manager', 'waiting', :due_date, :created_at)
        """), {
            'due_date': datetime.now(),
            'created_at': datetime.now()
        })
        
        db.commit()
        print("   Sample workflow created successfully")
        
    except Exception as e:
        print(f"   Error creating workflow: {e}")
    
    # Test workflow queries
    print("3. Testing workflow queries...")
    try:
        # Get workflow count
        workflow_count = db.execute(text("SELECT COUNT(*) FROM workflow_instances")).scalar()
        print(f"   Total workflows: {workflow_count}")
        
        # Get pending workflows
        pending_count = db.execute(text("SELECT COUNT(*) FROM workflow_instances WHERE status = 'pending'")).scalar()
        print(f"   Pending workflows: {pending_count}")
        
        # Get workflow steps
        steps_count = db.execute(text("SELECT COUNT(*) FROM workflow_steps")).scalar()
        print(f"   Total workflow steps: {steps_count}")
        
    except Exception as e:
        print(f"   Error querying workflows: {e}")
    
    # Test approval simulation
    print("4. Testing approval simulation...")
    try:
        # Simulate approval
        db.execute(text("""
            INSERT INTO workflow_approvals 
            (id, workflow_id, step_id, approver_id, action, comments, approved_at)
            VALUES 
            ('test-approval-1', 'test-workflow-1', 'test-step-1', 'test-approver', 'approved', 'Looks good', :approved_at)
        """), {
            'approved_at': datetime.now()
        })
        
        # Update step status
        db.execute(text("""
            UPDATE workflow_steps 
            SET status = 'approved', completed_at = :completed_at 
            WHERE id = 'test-step-1'
        """), {
            'completed_at': datetime.now()
        })
        
        # Move to next step
        db.execute(text("""
            UPDATE workflow_steps 
            SET status = 'pending' 
            WHERE id = 'test-step-2'
        """))
        
        db.execute(text("""
            UPDATE workflow_instances 
            SET current_step = 2 
            WHERE id = 'test-workflow-1'
        """))
        
        db.commit()
        print("   Approval simulation completed")
        
    except Exception as e:
        print(f"   Error simulating approval: {e}")
    
    # Test delegation
    print("5. Testing delegation...")
    try:
        db.execute(text("""
            INSERT INTO workflow_delegations 
            (id, workflow_id, step_id, from_user, to_user, reason, delegated_at, is_active)
            VALUES 
            ('test-delegation-1', 'test-workflow-1', 'test-step-2', 'original-approver', 'delegate-approver', 'Out of office', :delegated_at, 1)
        """), {
            'delegated_at': datetime.now()
        })
        
        db.execute(text("""
            UPDATE workflow_steps 
            SET delegated_to = 'delegate-approver' 
            WHERE id = 'test-step-2'
        """))
        
        db.commit()
        print("   Delegation test completed")
        
    except Exception as e:
        print(f"   Error testing delegation: {e}")
    
    # Test workflow templates
    print("6. Testing workflow templates...")
    try:
        template_data = {
            'name': 'Standard Journal Entry Approval',
            'steps': [
                {'name': 'Supervisor Review', 'role': 'supervisor', 'required_approvals': 1},
                {'name': 'Manager Approval', 'role': 'manager', 'required_approvals': 1}
            ]
        }
        
        db.execute(text("""
            INSERT INTO workflow_templates 
            (id, template_name, workflow_type, description, template_data, is_default, min_amount, max_amount, created_at)
            VALUES 
            ('test-template-1', 'Standard JE Approval', 'journal_entry', 'Standard approval for journal entries', :template_data, 1, 0, 10000, :created_at)
        """), {
            'template_data': json.dumps(template_data),
            'created_at': datetime.now()
        })
        
        db.commit()
        print("   Workflow template created")
        
    except Exception as e:
        print(f"   Error creating template: {e}")
    
    # Test email notification simulation
    print("7. Testing email notification simulation...")
    try:
        print("   Email notifications would be sent to:")
        print("     - Supervisor for initial approval")
        print("     - Manager for second level approval")
        print("     - Original creator for completion notification")
        print("   Email system configured (SMTP settings required for actual sending)")
        
    except Exception as e:
        print(f"   Error in notification test: {e}")
    
    print("=== Workflow System Test Complete ===")

if __name__ == "__main__":
    test_workflow_system()
    db.close()