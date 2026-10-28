from fastapi import APIRouter
from datetime import datetime

router = APIRouter(
    prefix="/intrusions",
    tags=["Intrusions"]
)

# Temporary in-memory storage
# Replace with PostgreSQL later
events = []


@router.get("/")
def get_intrusions():
    return events


@router.get("/{event_id}")
def get_intrusion(event_id: int):

    for event in events:
        if event["id"] == event_id:
            return event

    return {"message": "Event not found"}


@router.post("/")
def create_intrusion(
    image_path: str,
    video_path: str
):

    event = {
        "id": len(events) + 1,
        "image_path": image_path,
        "video_path": video_path,
        "timestamp": datetime.utcnow()
    }

    events.append(event)

    return {
        "message": "Intrusion stored",
        "event": event
    }


@router.delete("/{event_id}")
def delete_intrusion(event_id: int):

    global events

    events = [
        event
        for event in events
        if event["id"] != event_id
    ]

    return {"message": "Deleted"}