from datetime import datetime, timezone
from uuid import uuid4
 
from sqlalchemy import Column, String, DateTime
 
from database import Base
 
 
class Message(Base):
    __tablename__ = "messages"
 
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    role = Column(String, nullable=False)        # "user" 또는 "assistant"
    content = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
 