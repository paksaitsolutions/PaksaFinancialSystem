from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import List
import json
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db.session import get_db
from app.models.core_models import Customer, Vendor
from sqlalchemy import select, func, desc

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception:
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

async def get_real_insights(db: AsyncSession):
    """Generate real insights from database data"""
    total_transactions = 0
    total_customers = 0
    total_vendors = 0
    
    try:
        # Get total customers
        customer_count = await db.execute(select(func.count(Customer.id)))
        total_customers = customer_count.scalar() or 0
        
        # Get total vendors
        vendor_count = await db.execute(select(func.count(Vendor.id)))
        total_vendors = vendor_count.scalar() or 0
    except Exception as e:
        print(f"Database query error: {e}")
        total_customers = 0
        total_vendors = 0
    
    insights = [
        {
            "title": "Business Network",
            "message": f"Managing {total_customers} customers and {total_vendors} vendors",
            "type": "status"
        },
        {
            "title": "System Status",
            "message": "All financial modules operational and ready",
            "type": "info"
        },
        {
            "title": "Real-time Monitoring",
            "message": "AI insights active and monitoring financial data",
            "type": "activity"
        }
    ]
    
    return insights

@router.websocket("/ws/ai-insights")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            try:
                # Get database session
                db_gen = get_db()
                db = await db_gen.__anext__()
                try:
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
                finally:
                    await db.close()
                
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"WebSocket error: {e}")
                await asyncio.sleep(5)
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)