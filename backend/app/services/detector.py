from ultralytics import YOLO
from app.config import settings


class HumanDetector:

    def __init__(self):

        self.model = YOLO(
            settings.YOLO_MODEL
        )

    def track(self, frame):

        results = self.model.track(
            source=frame,
            persist=True,
            tracker="bytetrack.yaml",
            classes=[0],      # person only
            conf=0.35,
            verbose=False,
            device="cpu",
        )

        persons = []

        for result in results:

            if result.boxes is None:
                continue

            for box in result.boxes:

                if box.id is None:
                    continue

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0].tolist(),
                )

                persons.append(
                    {
                        "track_id": int(box.id.item()),
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2,
                        "confidence": float(
                            box.conf.item()
                        ),
                    }
                )

        return persons