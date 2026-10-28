from fastapi import WebSocket

connections = []


async def connect(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)


async def disconnect(websocket: WebSocket):
    if websocket in connections:
        connections.remove(websocket)


async def broadcast(message: dict):
    disconnected = []

    for conn in connections:
        try:
            await conn.send_json(message)
        except Exception:
            disconnected.append(conn)

    for conn in disconnected:
        if conn in connections:
            connections.remove(conn)