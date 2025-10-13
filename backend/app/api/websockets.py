from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import List
import json
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db.session import get_db
from app.models.core_models import Transaction, Customer, Vendor
from sqlalchemy import select, func, desc

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

async def get_real_insights(db: AsyncSession):
    """Generate real insights from database data"""
    # Get recent transaction count
    recent_transactions = await db.execute(
        select(func.count(Transaction.id)).where(
            Transaction.created_at >= datetime.now().replace(hour=0, minute=0, second=0)
        )
    )
    transaction_count = recent_transactions.scalar() or 0
    
    # Get total customers
    customer_count = await db.execute(select(func.count(Customer.id)))
    total_customers = customer_count.scalar() or 0
    
    # Get total vendors
    vendor_count = await db.execute(select(func.count(Vendor.id)))
    total_vendors = vendor_count.scalar() or 0
    
    insights = [
        {
            "title": "Daily Activity",
            "message": f"{transaction_count} transactions processed today",
            "type": "activity"
        },
        {
            "title": "System Status",
            "message": f"Managing {total_customers} customers and {total_vendors} vendors",
            "type": "status"
        }
    ]
    
    return insights

@router.websocket("/ws/ai-insights")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Get database session
            async with get_db() as db:
                insights = await get_real_insights(db)
                
                for insight in insights:
                    insight_data = {
                        "type": "insight",
                        "data": {
                            "title": insight["title"],
                            "message": insight["message"],
                            "timestamp": datetime.now().isoformat(),
                            "insight_type": insight["type"]
                        }
                    }
                    await manager.send_personal_message(json.dumps(insight_data), websocket)
                    await asyncio.sleep(2)
            
            await asyncio.sleep(30)  # Send updates every 30 seconds
    except WebSocketDisconnect:
        manager.disconnect(websocket)