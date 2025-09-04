import asyncio
import uuid
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, selectinload

# Import models
from app.models.employee import Employee
from app.models.department import Department
from app.modules.core_financials.payroll.models.payroll_processing import PayrollRun, PayrollItem

# Database URL - update this to match your configuration
DATABASE_URL = "sqlite+aiosqlite:///./paksa_finance.db"

# Create async engine and session
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    """Initialize the database with test data"""
    async with engine.begin() as conn:
        # Create all tables
        from app.models.base import Base
        await conn.run_sync(Base.metadata.create_all)

async def test_models():
    """Test the models by creating and querying data"""
    async with AsyncSessionLocal() as session:
        # Create a department
        dept = Department(
            name="Finance",
            code="FIN",
            description="Finance Department",
            is_active=True
        )
        session.add(dept)
        await session.commit()
        
        # Create an employee
        emp = Employee(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="1234567890",
            hire_date=date(2020, 1, 1),
            employment_type="FULL_TIME",
            job_title="Accountant",
            department_id=dept.id,
            is_active=True
        )
        session.add(emp)
        await session.commit()
        
        # Create a payroll run
        payroll_run = PayrollRun(
            name="September 2023 Payroll",
            start_date=date(2023, 9, 1),
            end_date=date(2023, 9, 30),
            status="COMPLETED",
            payment_date=date(2023, 10, 5),
            total_gross=5000.00,
            total_deductions=1500.00,
            total_net=3500.00,
            company_id=uuid.uuid4()  # In a real app, this would be a valid company ID
        )
        session.add(payroll_run)
        await session.commit()
        
        # Create a payroll item
        payroll_item = PayrollItem(
            payroll_run_id=payroll_run.id,
            employee_id=emp.id,
            basic_salary=4000.00,
            gross_earnings=5000.00,
            total_deductions=1500.00,
            net_pay=3500.00,
            payment_method="BANK_TRANSFER",
            status="PAID"
        )
        session.add(payroll_item)
        await session.commit()
        
        # Query the data
        print("\n--- Departments ---")
        result = await session.execute(select(Department))
        for dept in result.scalars():
            print(f"{dept.name} ({dept.code}): {dept.description}")
        
        print("\n--- Employees ---")
        result = await session.execute(select(Employee).options(selectinload(Employee.department)))
        for emp in result.scalars():
            print(f"{emp.first_name} {emp.last_name} - {emp.job_title} at {emp.department.name if emp.department else 'No Department'}")
        
        print("\n--- Payroll Runs ---")
        result = await session.execute(select(PayrollRun))
        for run in result.scalars():
            print(f"{run.name}: {run.start_date} to {run.end_date} - Status: {run.status}")
        
        print("\n--- Payroll Items ---")
        result = await session.execute(select(PayrollItem).options(
            selectinload(PayrollItem.employee),
            selectinload(PayrollItem.payroll_run)
        ))
        for item in result.scalars():
            print(f"{item.employee.first_name} {item.employee.last_name} - "
                  f"Net Pay: ${item.net_pay} - Status: {item.status}")

async def main():
    try:
        await init_db()
        await test_models()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
