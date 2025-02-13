from fastapi import FastAPI, HTTPException, Depends ,Header
from fastapi.middleware.cors import CORSMiddleware
from schema import UserCreate, UserResponse , MessageRequest
from auth.crud import get_user_by_username, create_user
from auth.database import engine, SessionLocal
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from utils.authentication import verify_password
import jwt
import os
import auth.models
from chat.chat import get_gemini_response, get_chat_history, get_chat_history_by_historyId

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = 60

auth.models.Base.metadata.create_all(bind=engine)




app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.get("/")
async def root():
    return {"message": "My simple chatbot application"}


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/signup", response_model=UserResponse)
def signupUser(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    
    new_user = create_user(db=db, user=user)
    return new_user

@app.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, user.username)
    if(db_user == None):
        raise HTTPException(status_code=400, detail="User not found")
    if not user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Username or password incorrect")

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode({"sub": db_user.username,  "user_id": str(db_user.id), "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)



    return {"access_token": token, "token_type": "bearer", "expireIn": expire}

@app.post("/chat")
def chat(request: MessageRequest,  db: Session = Depends(get_db), authorization: str = Header(None)):
    user_id = None
    print("gg: ", request)
    if authorization:
        try:
            token = authorization.split(" ")[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("user_id")
            print("userId: ", user_id)
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.DecodeError:
            raise HTTPException(status_code=401, detail="Invalid token")

    response_text = get_gemini_response(request.message, request.historyId, db , user_id)
    return {"response": response_text}


@app.get("/chat/history")
def get_history(db: Session = Depends(get_db), authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization token is missing")

    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token")

    history = get_chat_history(db, user_id)
    
    return {"history": [{"history_id": h.history_id, "user_message": h.user_message, "bot_response": h.bot_response} for h in history]}


@app.get("/chat/history/{history_id}")
def get_history(history_id: str, db: Session = Depends(get_db), authorization: str = Header(None)):


    print("historyId: ", history_id)
   
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization token is missing")

    try:
        token = authorization.split(" ")[1]  # Assuming "Bearer <token>"
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token")

   
    history = get_chat_history_by_historyId(db, history_id)
    

    return {"history": [{"history_id": h.history_id, "user_message": h.user_message, "bot_response": h.bot_response} for h in history]}