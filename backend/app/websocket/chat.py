from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.manager import ws_manager
from app.agent.agent import run_chat
import json

router = APIRouter()

@router.websocket("/ws/chat")
async def chat_ws(ws: WebSocket):
    """
    Bidirectional chat WebSocket.
    Client sends:  {"message": "how much did I spend on food?"}
    Server sends:  {"type": "chat_response", "message": "..."}
                   {"type": "typing", "value": true/false}
    """
    await ws_manager.connect_chat(ws)      
    history: list[dict] = []

    try:
        while True:
            raw = await ws.receive_text()

            # bad JSON won't crash the connection
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                await ws.send_text(json.dumps({"type": "error", "message": "Invalid JSON"}))
                continue

            user_msg = payload.get("message", "")
            # ensure it's actually a string before calling .strip()
            if not isinstance(user_msg, str) or not user_msg.strip():
                continue
            user_msg = user_msg.strip()

            await ws.send_text(json.dumps({"type": "typing", "value": True}))

            # typing indicator always turns off even if agent errors
            try:
                response = await run_chat(user_msg, history)
                history.append({"role": "user",     "content": user_msg})
                history.append({"role": "assistant", "content": response})
                history = history[-20:]
                await ws.send_text(json.dumps({"type": "chat_response", "message": response}))
            except Exception as e:
                print(f"[Chat error] {e}")
                await ws.send_text(json.dumps({
                    "type":    "chat_response",
                    "message": "Sorry, I ran into an error. Please try again."
                }))
            finally:
                # always turn off typing, even on failure
                await ws.send_text(json.dumps({"type": "typing", "value": False}))

    except WebSocketDisconnect:
        pass
    except Exception as e:                  # catch all other errors
        print(f"[WebSocket error] {e}")
    finally:
        ws_manager.disconnect_chat(ws)