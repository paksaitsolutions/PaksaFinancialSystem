"""
WebSocket endpoints for real-time features
"""
from fastapi import WebSocket, WebSocketDisconnect, Depends
from fastapi.routing import APIRouter
from typing import List, Dict, Any
import json
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.ai_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, connection_type: str = "general"):
        await websocket.accept()
        if connection_type == "ai-insights":
            self.ai_connections.append(websocket)
        else:
            self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket, connection_type: str = "general"):
        if connection_type == "ai-insights" and websocket in self.ai_connections:
            self.ai_connections.remove(websocket)
        elif websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast_to_ai(self, message: dict):
        for connection in self.ai_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                # Remove dead connections
                self.ai_connections.remove(connection)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                # Remove dead connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

@router.websocket("/ws/ai-insights")
async def ai_insights_websocket(websocket: WebSocket):
    await manager.connect(websocket, "ai-insights")
    try:
        # Send initial connection message
        await websocket.send_text(json.dumps({
            "type": "connection",
            "status": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        # Send initial metrics
        await websocket.send_text(json.dumps({
            "type": "metrics",
            "payload": [
                {"value": "94%", "progress": 94, "trend": 2.1},
                {"value": "0", "progress": 0, "trend": -12},
                {"value": "$13,200", "progress": 68, "trend": 5.4},
                {"value": "1.1s", "progress": 88, "trend": -3.2}
            ]
        }))
        
        while True:
            # Keep connection alive and send periodic updates
            await asyncio.sleep(30)  # Send updates every 30 seconds
            
            # Send simulated real-time data
            await websocket.send_text(json.dumps({
                "type": "activity",
                "payload": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "Prediction",
                    "message": f"Real-time update at {datetime.utcnow().strftime('%H:%M:%S')}",
                    "confidence": 92 + (hash(str(datetime.utcnow())) % 8)
                }
            }))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, "ai-insights")
        logger.info("AI insights WebSocket disconnected")
    except Exception as e:
        logger.error(f"AI insights WebSocket error: {e}")
        manager.disconnect(websocket, "ai-insights")

@router.websocket("/ws/notifications")
async def notifications_websocket(websocket: WebSocket):
    await manager.connect(websocket, "notifications")
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for now
            await manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket, "notifications")

# Function to broadcast AI insights from other parts of the application
async def broadcast_ai_insight(insight_type: str, payload: Dict[Any, Any]):
    """Broadcast AI insights to connected clients"""
    message = {
        "type": insight_type,
        "payload": payload,
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.broadcast_to_ai(message)