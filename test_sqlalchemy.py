"""
Simple SQLAlchemy test script to verify database functionality.
"""
import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define database path
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "test_alchemy.db")
db_url = f"sqlite:///{db_path}"

print(f"Creating test database at: {db_path}")

# Create engine
engine = create_engine(db_url, echo=True)

# Create base class
Base = declarative_base()

# Define a simple model
class TestModel(Base):
    __tablename__ = "test_table"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

# Create tables
print("\nCreating database tables...")
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Add test data
    print("\nAdding test data...")
    test_record = TestModel(name="Test Record")
    session.add(test_record)
    session.commit()
    
    # Query test data
    print("\nQuerying test data...")
    result = session.query(TestModel).first()
    print(f"Retrieved record: ID={result.id}, Name='{result.name}'")
    
    print("\n✅ Test completed successfully!")
    
except Exception as e:
    print(f"\n❌ Error during test: {str(e)}")
    import traceback
    traceback.print_exc()
    
finally:
    session.close()
    
print(f"\nDatabase location: {os.path.abspath(db_path)}")
