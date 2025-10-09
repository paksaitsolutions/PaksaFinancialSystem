"""
Simple WebSocket test script
"""
import asyncio
import websockets
import json

async def test_ai_insights_websocket():
    uri = "ws://localhost:8000/ws/ai-insights"
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to AI insights WebSocket")
            
            # Listen for messages for 10 seconds
            for i in range(3):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(message)
                    print(f"Received: {data}")
                except asyncio.TimeoutError:
                    print("No message received within timeout")
                    break
                    
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_ai_insights_websocket())