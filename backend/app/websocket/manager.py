# from fastapi import WebSocket
# import json

# class WebSocketManager:
#     def __init__(self):
#         # separate lists so broadcast() never
#         # sends transaction events to chat clients or vice versa
#         self._feed: list[WebSocket] = []
#         self._chat: list[WebSocket] = []

#     async def connect(self, ws: WebSocket):
#         await ws.accept()
#         self.active.append(ws)

#     def disconnect(self, ws: WebSocket):
#         if ws in self.active:
#             self.active.remove(ws)

#     async def broadcast(self, data: dict):
#         """Send a message to all connected clients."""
#         dead = []
#         for ws in self.active:
#             try:
#                 await ws.send_text(json.dumps(data))
#             except Exception:
#                 dead.append(ws)
#         for ws in dead:
#             self.disconnect(ws)

# # Singleton — imported by feed.py, chat.py, and simulator.py
# ws_manager = WebSocketManager()
from fastapi import WebSocket
import json

class WebSocketManager:
    def __init__(self):
        self._feed: list[WebSocket] = []
        self._chat: list[WebSocket] = []

    async def connect_feed(self, ws: WebSocket):
        await ws.accept()
        self._feed.append(ws)

    async def connect_chat(self, ws: WebSocket):
        await ws.accept()
        self._chat.append(ws)

    def disconnect_feed(self, ws: WebSocket):
        if ws in self._feed:
            self._feed.remove(ws)

    def disconnect_chat(self, ws: WebSocket):
        if ws in self._chat:
            self._chat.remove(ws)

    async def broadcast(self, data: dict):
        dead = []
        for ws in self._feed:
            try:
                await ws.send_text(json.dumps(data))
            except Exception:
                dead.append(ws)

        for ws in dead:
            self.disconnect_feed(ws)

ws_manager = WebSocketManager()