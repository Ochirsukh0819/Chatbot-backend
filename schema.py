from pydantic import BaseModel
import uuid

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(UserCreate):
    id: uuid.UUID
    disabled: bool = False

class MessageRequest(BaseModel):
    message: str
    historyId:str