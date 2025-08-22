"""
Initialize the database with required tables and initial data.
"""
import asyncio
from app.core.database import init_db

async def main():
    print("Initializing database...")
    await init_db()
    print("Database initialization complete!")

if __name__ == "__main__":
    asyncio.run(main())
