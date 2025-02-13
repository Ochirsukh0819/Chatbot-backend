from sqlalchemy.orm import Session
from .models import User
from schema import UserCreate
from utils.authentication import get_password_hash


def get_user_by_username(db:Session, username:str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  
    return db_user


# AIzaSyABEKOi8Y5BB55uPOOP2jByXnshE_FfjYs