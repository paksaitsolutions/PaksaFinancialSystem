from typing import List, Optional
from uuid import UUID, uuid4
from decimal import Decimal
from datetime import date
from ..schemas.customer import Customer, CustomerCreate, CustomerUpdate

class CustomerService:
    def __init__(self):
        self._customers = {}
        self._next_code = 1000
    
    def create_customer(self, customer_data: CustomerCreate) -> Customer:
        customer_id = uuid4()
        customer = Customer(
            id=customer_id,
            customer_code=f"CUST-{self._next_code:04d}",
            created_at=date.today(),
            **customer_data.dict()
        )
        self._customers[customer_id] = customer
        self._next_code += 1
        return customer
    
    def get_customer(self, customer_id: UUID) -> Optional[Customer]:
        return self._customers.get(customer_id)
    
    def list_customers(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        customers = list(self._customers.values())
        return customers[skip:skip + limit]
    
    def update_customer(self, customer_id: UUID, customer_data: CustomerUpdate) -> Optional[Customer]:
        if customer_id not in self._customers:
            return None
        
        customer = self._customers[customer_id]
        update_data = customer_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(customer, field, value)
        
        return customer
    
    def delete_customer(self, customer_id: UUID) -> bool:
        if customer_id in self._customers:
            del self._customers[customer_id]
            return True
        return False