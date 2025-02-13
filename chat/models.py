from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from auth.database import Base


class ChatHistory(Base):
    __tablename__= "chat_history"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    history_id = Column(String, index=True)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)

    user = relationship("User", back_populates="chat_histories")