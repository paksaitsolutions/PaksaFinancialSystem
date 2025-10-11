from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio

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

@router.websocket("/ws/ai-insights")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Send periodic AI insights
            await asyncio.sleep(5)
            insight = {
                "type": "insight",
                "data": {
                    "title": "Cash Flow Analysis",
                    "message": "Positive cash flow trend detected",
                    "timestamp": "2024-01-15T10:30:00Z"
                }
            }
            await manager.send_personal_message(json.dumps(insight), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)