from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime

from sqlalchemy.orm import declarative_base

Base = declarative_base()

class IntrusionEvent(Base):
    __tablename__ = "intrusion_events"

    id = Column(Integer, primary_key=True, index=True)
    camera_name = Column(String)
    image_path = Column(String)

    video_path = Column(String)

    timestamp = Column(DateTime)