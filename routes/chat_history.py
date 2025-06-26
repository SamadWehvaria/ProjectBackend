from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from .auth import get_current_user

load_dotenv()
router = APIRouter()

MONGO_URI = os.getenv("MONGO_URI")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY").encode()
fernet = Fernet(ENCRYPTION_KEY)

client = AsyncIOMotorClient(MONGO_URI)
db = client.healthcare_db
chat_collection = db.chat_history

class ChatHistory(BaseModel):
    messages: list

def encrypt_message(message: dict) -> dict:
    message_str = str(message)
    encrypted = fernet.encrypt(message_str.encode()).decode()
    return {"encrypted_message": encrypted}

def decrypt_message(encrypted_message: dict) -> dict:
    decrypted = fernet.decrypt(encrypted_message["encrypted_message"].encode()).decode()
    return eval(decrypted) # Safely parse string back to dict

@router.post("/chat-history")
async def save_chat_history(chat: ChatHistory, user: dict = Depends(get_current_user)):
    encrypted_messages = [encrypt_message(msg) for msg in chat.messages]
    await chat_collection.update_one(
        {"user_email": user["email"]},
        {"$set": {"messages": encrypted_messages}},
        upsert=True
    )
    return {"status": "Chat history saved"}

@router.get("/chat-history")
async def get_chat_history(user: dict = Depends(get_current_user)):
    chat_doc = await chat_collection.find_one({"user_email": user["email"]})
    if not chat_doc:
        return {"messages": []}
    decrypted_messages = [decrypt_message(msg) for msg in chat_doc["messages"]]
    return {"messages": decrypted_messages}