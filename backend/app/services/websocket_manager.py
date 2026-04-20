import json
from typing import Dict
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self._connections: Dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self._connections[session_id] = websocket

    def disconnect(self, session_id: str):
        self._connections.pop(session_id, None)

    async def broadcast(self, session_id: str, data: dict):
        ws = self._connections.get(session_id)
        if ws:
            try:
                await ws.send_text(json.dumps(data))
            except Exception:
                self.disconnect(session_id)

    async def send_to_all(self, data: dict):
        for session_id in list(self._connections.keys()):
            await self.broadcast(session_id, data)


manager = ConnectionManager()
