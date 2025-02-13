from sqlalchemy import Column, String
from .database import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, index=True)
    password = Column(String)
    chat_histories = relationship("ChatHistory", back_populates="user")