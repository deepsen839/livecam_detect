from contextlib import asynccontextmanager
import asyncio
import base64
import os

import cv2
import numpy as np

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, FileResponse,JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.intrusion import router as intrusion_router
from app.api.websocket import connect, disconnect
from app.services.video_processor import process_video
from app.services import camera

@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Starting Smart Intrusion Detection...")

    os.makedirs("snapshots", exist_ok=True)
    os.makedirs("clips", exist_ok=True)

    # Start background processor
    asyncio.create_task(process_video())

    yield

    print("Shutting down...")


app = FastAPI(
    title="Smart Intrusion Detection",
    lifespan=lifespan,
)

app.include_router(intrusion_router)

# -----------------------------
# Static folders
# -----------------------------

app.mount(
    "/snapshots",
    StaticFiles(directory="snapshots"),
    name="snapshots",
)

app.mount(
    "/clips",
    StaticFiles(directory="clips"),
    name="clips",
)


# @app.get("/")
# async def root():
#     return FileResponse("static/index.html")

# @app.get("/")
# async def root():
#     return JSONResponse({"status": "ok"})
# --------------------------------------------------------
# Existing websocket (alerts)
# --------------------------------------------------------

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await connect(websocket)

    try:

        while True:
            await websocket.receive_text()

    except Exception:
        await disconnect(websocket)


# --------------------------------------------------------
# Browser Camera
# --------------------------------------------------------

@app.websocket("/camera")
async def browser_camera(websocket: WebSocket):

    await websocket.accept()

    print("Camera connected")

    try:

        while True:

            data = await websocket.receive_text()

            jpg = base64.b64decode(data)

            frame = cv2.imdecode(
                np.frombuffer(jpg, np.uint8),
                cv2.IMREAD_COLOR,
            )

            async with camera.frame_lock:
                camera.latest_frame = frame

    except WebSocketDisconnect:

        print("Camera disconnected")


# --------------------------------------------------------
# MJPEG Stream
# --------------------------------------------------------

def generate_frames():

    import time

    while True:

        frame = camera.processed_frame

        if frame is None:
            time.sleep(0.01)
            continue

        ok, buffer = cv2.imencode(".jpg", frame)

        if not ok:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type:image/jpeg\r\n\r\n"
            + buffer.tobytes()
            + b"\r\n"
        )


@app.get("/video")
def video():

    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )

import os

print("Current directory:", os.getcwd())
print("Files:", os.listdir("."))

if os.path.exists("static"):
    print("Static folder:", os.listdir("static"))
else:
    print("static folder NOT FOUND")


app.mount("/", StaticFiles(directory="static", html=True), name="frontend")
