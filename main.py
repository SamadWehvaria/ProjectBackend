from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Healthcare Translator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Keep for local development
        "https://healthtranslate.vercel.app",  # Add your Vercel frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Healthcare Translator API is running"}

from routes.translation import router as translation_router
from routes.tts import router as tts_router
from routes.auth import router as auth_router
from routes.chat_history import router as chat_history_router

app.include_router(translation_router)
app.include_router(tts_router)
app.include_router(auth_router)
app.include_router(chat_history_router)
