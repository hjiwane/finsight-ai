from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.manager import ws_manager
import json

router = APIRouter()

@router.websocket("/ws/feed")
async def feed_ws(ws: WebSocket):
    """
    Frontend connects here to receive live transactions + agent insights.
    Passive — frontend just listens, we only send.
    """
    await ws_manager.connect_feed(ws)
    try:
        while True:
            # only handle keepalive pings from client
            data = await ws.receive_text()
            if data == "ping":
                await ws.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        pass
    finally:
        ws_manager.disconnect_feed(ws)