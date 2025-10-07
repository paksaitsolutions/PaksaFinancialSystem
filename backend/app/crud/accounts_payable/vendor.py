"""
Vendor CRUD operations - placeholder
"""

class PlaceholderVendorCRUD:
    async def get_by_code(self, db, code):
        return None
    
    async def create(self, db, obj_in):
        return {"id": "placeholder", "code": obj_in.code}
    
    async def get_paginated(self, db, **kwargs):
        return {"items": [], "pagination": {"total": 0, "total_pages": 0}}
    
    async def get(self, db, id):
        return None
    
    async def update(self, db, db_obj, obj_in):
        return db_obj
    
    async def delete(self, db, id):
        return True

vendor_crud = PlaceholderVendorCRUD()