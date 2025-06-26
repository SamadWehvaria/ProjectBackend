# routes/translation.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

TOGETHER_AI_API_KEY = os.getenv("TOGETHER_AI_API_KEY")

class TranslationRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str

class ProviderRequest(BaseModel):
    text: str
    lang: str

@router.post("/translate")
async def translate(request: TranslationRequest):
    if not TOGETHER_AI_API_KEY:
        print("Error: Together AI API key not configured")
        raise HTTPException(status_code=500, detail="Together AI API key not configured")

    lang_map = {
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "ar": "Arabic",
        "ur": "Urdu",
        "zh": "Chinese",
        "hi": "Hindi",
        "pt": "Portuguese"
    }
    target_lang_name = lang_map.get(request.target_lang)
    if not target_lang_name:
        print(f"Error: Unsupported target language {request.target_lang}")
        raise HTTPException(status_code=400, detail="Unsupported target language")

    prompt = (
        f"Translate the following text from {lang_map.get(request.source_lang, 'English')} to {target_lang_name}, "
        f"ensuring the translation is complete and accurate: '{request.text}'"
    )
    try:
        response = requests.post(
            "https://api.together.xyz/v1/completions",  # Updated to correct endpoint
            headers={
                "Authorization": f"Bearer {TOGETHER_AI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
                "prompt": f"<s>[INST] {prompt} [/INST]",
                "max_tokens": 1500,
                "temperature": 0.7,
            },
        )
        response.raise_for_status()
        result = response.json()
        if "choices" not in result or not result["choices"]:
            print("Error: Invalid response format from Together AI")
            raise HTTPException(status_code=500, detail="Invalid response format from Together AI")
        translated_text = result["choices"][0]["text"].strip()
        return {"translated_text": translated_text}
    except requests.RequestException as e:
        print(f"Error in translate: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@router.post("/provider-response")
async def provider_response(request: ProviderRequest):
    if not TOGETHER_AI_API_KEY:
        print("Error: Together AI API key not configured")
        raise HTTPException(status_code=500, detail="Together AI API key not configured")

    lang_name = {
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "ar": "Arabic",
        "ur": "Urdu",
        "zh": "Chinese",
        "hi": "Hindi",
        "pt": "Portuguese"
    }.get(request.lang, "English")

    prompt = (
        f"You are Dr. Martinez, a healthcare expert. Provide a professional, complete response in {lang_name} to the following patient query. "
        f"Ensure the response is complete, and includes all relevant medical advice: '{request.text}'"
    )
    try:
        print(f"Sending request to Together AI: text={request.text}, lang={request.lang}")
        response = requests.post(
            "https://api.together.xyz/v1/completions",  # Updated to correct endpoint
            headers={
                "Authorization": f"Bearer {TOGETHER_AI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
                "prompt": f"<s>[INST] {prompt} [/INST]",
                "max_tokens": 1500,
                "temperature": 0.7,
            },
        )
        response.raise_for_status()
        result = response.json()
        if "choices" not in result or not result["choices"]:
            print("Error: Invalid response format from Together AI")
            raise HTTPException(status_code=500, detail="Invalid response format from Together AI")
        response_text = result["choices"][0]["text"].strip()
        print(f"Received response: {response_text[:100]}...")  # Log first 100 chars
        return {"response": response_text}  # Changed to match frontend expectation
    except requests.RequestException as e:
        print(f"Error in provider_response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI response failed: {str(e)}")