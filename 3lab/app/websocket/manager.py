from typing import Dict
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, email: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[email] = websocket
        print(f"🔌 WebSocket подключён для: {email}")

    def disconnect(self, email: str):
        self.active_connections.pop(email, None)
        print(f"❌ WebSocket отключён для: {email}")

    async def send_to_user(self, email: str, message: dict):
        websocket = self.active_connections.get(email)
        if websocket:
            await websocket.send_json(message)
            print(f"📤 Отправлено {email}: {message}")
        else:
            print(f"⚠️ Нет активного соединения для: {email}")

manager = ConnectionManager()
