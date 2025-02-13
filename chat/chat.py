import os
from fastapi import Header, HTTPException
import google.generativeai as genai
from sqlalchemy.orm import Session
from .models import ChatHistory
import jwt

from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def upload_to_gemini(path, mime_type=None):

  file = genai.upload_file(path, mime_type=mime_type)
  print(f"Uploaded file '{file.display_name}' as: {file.uri}")
  return file

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
   "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-pro",
  generation_config=generation_config,
)



chat_session = model.start_chat(history=[])

def save_chat_history(db: Session, user_id: str, historyId:str, user_input: str, model_response: str):
    try:
        print("gggg: ", historyId, user_id)
        chat_entry = ChatHistory(
            user_id=user_id,
            history_id=historyId,
            user_message=user_input,
            bot_response=model_response
        )
        print("chat_entry: ", chat_entry)
        db.add(chat_entry)
        db.commit()
        db.refresh(chat_entry)
        return chat_entry
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save chat history: {str(e)}")


def get_chat_history_by_historyId(db: Session, history_id: str):
    return db.query(ChatHistory).filter(ChatHistory.history_id == history_id).all()


def get_chat_history(db: Session, user_id: str):
  
    histories = db.query(ChatHistory).filter(ChatHistory.user_id == user_id).all()
    unique_histories = {}
    
    for history in histories:
        if history.history_id not in unique_histories:
            unique_histories[history.history_id] = history
    
    return list(unique_histories.values())


def get_gemini_response(user_input: str, historyId:str,  db:Session, user_id:str):
    try:
        print("hi: ", user_id, user_input, historyId)
        response = chat_session.send_message(user_input)
        model_response = response.text

        if user_id:
            save_chat_history(db, user_id, historyId, user_input, model_response)
         


        return model_response

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

# response = chat_session.send_message("INSERT_INPUT_HERE")

