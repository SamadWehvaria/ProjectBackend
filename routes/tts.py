# routes/tts.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import logging

router = APIRouter()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    lang: str = Field(..., pattern="^(en|es|fr|ar|ur|zh)$")

class TTSResponse(BaseModel):
    text: str
    lang: str

@router.get("/text-to-speech/test", response_model=TTSResponse)
async def test_tts_connection():
    """
    Test endpoint for TTS service
    """
    try:
        return TTSResponse(
            text="Test successful",
            lang="en-US"
        )
    except Exception as e:
        logger.error(f"Error testing TTS connection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error testing TTS connection: {str(e)}"
        )

@router.post("/text-to-speech", response_model=TTSResponse)
async def text_to_speech(request: TTSRequest):
    """
    Validate text and language for browser-based TTS
    """
    try:
        logger.info(f"Received TTS request - Text: {request.text[:50]}..., Language: {request.lang}")
        
        # Language code mapping for Web Speech API
        lang_codes = {
            'en': 'en-US',
            'es': 'es-ES',
            'fr': 'fr-FR',
            'ar': 'ar-SA',
            'ur': 'ur-PK',
            'zh': 'zh-CN'
        }
        
        # Get the full language code
        lang_code = lang_codes.get(request.lang)
        if not lang_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported language: {request.lang}"
            )

        return TTSResponse(
            text=request.text,
            lang=lang_code
        )

    except Exception as e:
        logger.error(f"Error processing TTS request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/text-to-speech/{text}")
async def text_to_speech_get(text: str, lang: str = "en"):
    """
    GET endpoint for text-to-speech conversion
    """
    request = TTSRequest(text=text, lang=lang)
    return await text_to_speech(request)
