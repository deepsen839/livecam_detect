import os
import cv2
from datetime import datetime

from app.api.websocket import broadcast
from app.database import SessionLocal
from app.models.intrusion_event import IntrusionEvent
from app.services.recorder import recorder


class AlertService:

    @staticmethod
    async def trigger_intrusion(
        frame,
        camera_name="Main Gate",
        clip_path=None,
    ):

        os.makedirs("snapshots", exist_ok=True)

        timestamp = datetime.now()

        filename = (
            f"intrusion_"
            f"{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
        )

        # image_path = os.path.join(
        #     "snapshots",
        #     filename,
        # )

        # Save snapshot
        # cv2.imwrite(image_path, frame)

        # Start recording if not already started
        if clip_path is None:
            clip_path = recorder.start_recording()

        event_id = None

        # Save to PostgreSQL
        try:

            db = SessionLocal()

            # event = IntrusionEvent(
            #     camera_name=camera_name,
            #     image_path=image_path,
            #     video_path=clip_path,
            #     timestamp=timestamp,
            # )

            # db.add(event)
            # db.commit()
            # db.refresh(event)

            # event_id = event.id

            # db.close()

        except Exception as e:

            print(
                "Database save failed:",
                e,
            )

        # Broadcast to all WebSocket clients
        try:

            await broadcast(
                {
                    "type": "intrusion",
                    # "event_id": event_id,
                    "event_id":1,
                    "camera": camera_name,
                    # "snapshot": image_path,
                    "video": clip_path,
                    "timestamp": timestamp.isoformat(),
                    "severity": "high",
                }
            )

        except Exception as e:

            print(
                "WebSocket broadcast failed:",
                e,
            )

        print("=" * 60)
        print("🚨 INTRUSION DETECTED")
        print(f"Camera   : {camera_name}")
        # print(f"Snapshot : {image_path}")
        print(f"Video    : {clip_path}")
        print("=" * 60)

        return {
            "event_id": event_id,
            # "snapshot": image_path,
            "video": clip_path,
        }