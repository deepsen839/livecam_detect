import asyncio
import time

import cv2
import numpy as np

from app.services.detector import HumanDetector
from app.services.alert_service import AlertService
from app.services.recorder import recorder
from app.services import camera

from app.utils.zone_utils import (
    bbox_intersects_zone,
    get_zone,
)

detector = HumanDetector()

last_alert = {}
ALERT_COOLDOWN = 5

polygon = np.array(
    list(get_zone().exterior.coords),
    dtype=np.int32,
)


async def process_video():

    print("Waiting for browser camera...")

    while True:

        async with camera.frame_lock:

            if camera.latest_frame is None:
                frame = None
            else:
                frame = camera.latest_frame.copy()

        if frame is None:
            await asyncio.sleep(0.01)
            continue

        overlay = frame.copy()

        cv2.fillPoly(
            overlay,
            [polygon],
            (0, 0, 255),
        )

        frame = cv2.addWeighted(
            overlay,
            0.2,
            frame,
            0.8,
            0,
        )

        cv2.polylines(
            frame,
            [polygon],
            True,
            (0, 0, 255),
            2,
        )

        cv2.putText(
            frame,
            "Restricted Zone",
            (200, 140),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2,
        )

        tracked_persons = await asyncio.to_thread(
            detector.track,
            frame,
        )

        intrusion_found = False

        for person in tracked_persons:

            x1 = person["x1"]
            y1 = person["y1"]
            x2 = person["x2"]
            y2 = person["y2"]

            track_id = person["track_id"]

            confidence = person.get(
                "confidence",
                0.0,
            )

            intrusion = bbox_intersects_zone(
                x1,
                y1,
                x2,
                y2,
            )

            if intrusion:

                intrusion_found = True

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 0, 255),
                    3,
                )

                cv2.putText(
                    frame,
                    f"INTRUDER #{track_id}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2,
                )

                should_alert = (
                    track_id not in last_alert
                    or (
                        time.time()
                        - last_alert[track_id]
                    ) > ALERT_COOLDOWN
                )

                if should_alert:

                    last_alert[track_id] = time.time()

                    clip_path = recorder.start_recording()

                    await AlertService.trigger_intrusion(
                        frame.copy(),
                        camera_name="Browser Camera",
                        clip_path=clip_path,
                    )

            else:

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2,
                )

                cv2.putText(
                    frame,
                    f"Person #{track_id} {confidence:.2f}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )

        if intrusion_found:

            cv2.rectangle(
                frame,
                (0, 0),
                (frame.shape[1], 70),
                (0, 0, 255),
                -1,
            )

            cv2.putText(
                frame,
                "INTRUSION DETECTED",
                (20, 45),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2,
            )

        recorder.update(frame)

        async with camera.frame_lock:
            camera.processed_frame = frame.copy()

        await asyncio.sleep(0.001)