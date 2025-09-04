import asyncio
from app.core.database import engine
from sqlalchemy import inspect

async def check_tables():
    async with engine.connect() as conn:
        inspector = inspect(engine)
        print("Database URL:", engine.url)
        print("Tables in database:", inspector.get_table_names())
        
        # Check if our tables exist
        for table in ['departments', 'payroll_runs', 'payroll_items']:
            exists = await conn.run_sync(
                lambda conn, t: inspect(conn).has_table(t),
                table
            )
            print(f"Table {table} exists:", exists)

if __name__ == "__main__":
    asyncio.run(check_tables())
