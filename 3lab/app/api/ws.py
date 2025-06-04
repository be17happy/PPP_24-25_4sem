from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.services.auth import decode_token
from app.websocket.manager import ConnectionManager  # если тебе нужен класс


router = APIRouter()
manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        if not email:
            await websocket.close()
            return

        await manager.connect(email, websocket)
        while True:
            await websocket.receive_text()  # просто поддерживаем соединение
    except WebSocketDisconnect:
        manager.disconnect(email)
