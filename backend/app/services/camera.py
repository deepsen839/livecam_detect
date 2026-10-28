import asyncio

# Latest frame received from browser
latest_frame = None

# Latest processed frame (with boxes)
processed_frame = None

# Lock to avoid race conditions
frame_lock = asyncio.Lock()