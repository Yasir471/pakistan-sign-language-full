from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import cv2
import numpy as np
import torch
from ultralytics import YOLO
import base64
import io
from PIL import Image
import json
import random
import speech_recognition as sr
import pyttsx3
from gtts import gTTS
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize thread pool for blocking operations
executor = ThreadPoolExecutor(max_workers=4)

# Mock Pakistani Sign Language Dataset
MOCK_GESTURES = {
    "salam": {"urdu": "سلام", "pashto": "سلام ورور", "meaning": "Hello/Greetings"},
    "shukriya": {"urdu": "شکریہ", "pashto": "مننه", "meaning": "Thank you"},
    "khuda_hafiz": {"urdu": "خدا حافظ", "pashto": "خدای پامان", "meaning": "Goodbye"},
    "paani": {"urdu": "پانی", "pashto": "اوبه", "meaning": "Water"},
    "khana": {"urdu": "کھانا", "pashto": "خواړه", "meaning": "Food"},
    "ghar": {"urdu": "گھر", "pashto": "کور", "meaning": "Home"},
    "kitab": {"urdu": "کتاب", "pashto": "کتاب", "meaning": "Book"},
    "kaam": {"urdu": "کام", "pashto": "کار", "meaning": "Work"},
    "dost": {"urdu": "دوست", "pashto": "ملګری", "meaning": "Friend"},
    "madad": {"urdu": "مدد", "pashto": "مرسته", "meaning": "Help"}
}

# Mock gesture detection confidence
MOCK_DETECTION_RESULTS = list(MOCK_GESTURES.keys())

class GestureRecognitionService:
    def __init__(self):
        self.model_loaded = False
        self.gesture_classes = list(MOCK_GESTURES.keys())
        
    def load_model(self):
        """Mock YOLOv5 model loading"""
        self.model_loaded = True
        return True
    
    def detect_gesture(self, image_data: str) -> Dict[str, Any]:
        """Mock gesture detection using YOLOv5"""
        try:
            # Simulate processing time
            import time
            time.sleep(0.1)  # Mock inference time
            
            # Mock detection results
            detected_gesture = random.choice(self.gesture_classes)
            confidence = random.uniform(0.75, 0.95)
            
            return {
                "gesture": detected_gesture,
                "confidence": confidence,
                "bbox": [100, 100, 200, 200],  # Mock bounding box
                "urdu_text": MOCK_GESTURES[detected_gesture]["urdu"],
                "pashto_text": MOCK_GESTURES[detected_gesture]["pashto"],
                "meaning": MOCK_GESTURES[detected_gesture]["meaning"]
            }
        except Exception as e:
            return {"error": str(e)}

class SpeechService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        try:
            self.tts_engine = pyttsx3.init()
        except Exception as e:
            logger.warning(f"TTS engine initialization failed: {e}. Using mock TTS.")
            self.tts_engine = None
        
    def speech_to_text(self, audio_data: bytes, language: str = "ur") -> str:
        """Mock speech recognition for Urdu/Pashto"""
        try:
            # Mock speech recognition results
            mock_sentences = {
                "ur": [
                    "سلام علیکم", "آپ کیسے ہیں؟", "شکریہ", "خدا حافظ",
                    "مجھے مدد چاہیے", "یہ کیا ہے؟", "میں سمجھ گیا"
                ],
                "ps": [
                    "سلام ورور", "تاسو څنګه یاست؟", "مننه", "خدای پامان",
                    "زه مرستې ته اړتیا لرم", "دا څه دي؟", "زه پوه شوم"
                ]
            }
            
            # Return random mock sentence
            lang_code = "ps" if language == "pashto" else "ur"
            return random.choice(mock_sentences.get(lang_code, mock_sentences["ur"]))
            
        except Exception as e:
            return f"Error in speech recognition: {str(e)}"
    
    def text_to_speech(self, text: str, language: str = "ur") -> str:
        """Mock text-to-speech conversion"""
        try:
            # Return base64 audio data (mock)
            return "mock_audio_base64_data"
        except Exception as e:
            return f"Error in TTS: {str(e)}"
    
    def find_gesture_for_text(self, text: str, language: str = "ur") -> Optional[Dict]:
        """Find corresponding gesture for spoken text"""
        # Simple keyword matching for demo
        text_lower = text.lower()
        
        for gesture_key, gesture_data in MOCK_GESTURES.items():
            if language == "pashto":
                if gesture_data["pashto"].lower() in text_lower:
                    return {
                        "gesture": gesture_key,
                        "data": gesture_data
                    }
            else:  # Urdu
                if gesture_data["urdu"].lower() in text_lower:
                    return {
                        "gesture": gesture_key,
                        "data": gesture_data
                    }
        
        return None

# Initialize services
gesture_service = GestureRecognitionService()
speech_service = SpeechService()

# Models
class GestureDetectionRequest(BaseModel):
    image_data: str  # Base64 encoded image
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
class SpeechToSignRequest(BaseModel):
    audio_data: str  # Base64 encoded audio
    language: str = "urdu"  # "urdu" or "pashto"
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class TextToSignRequest(BaseModel):
    text: str
    language: str = "urdu"  # "urdu" or "pashto"
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class TranslationHistory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    translation_type: str  # "sign_to_speech" or "speech_to_sign"
    input_data: str
    output_data: str
    language: str
    confidence: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Sign Language Translation API - Ready!", "version": "1.0"}

@api_router.get("/gestures")
async def get_available_gestures():
    """Get list of available gestures in the dataset"""
    return {
        "gestures": MOCK_GESTURES,
        "count": len(MOCK_GESTURES)
    }

@api_router.post("/detect-gesture")
async def detect_gesture(request: GestureDetectionRequest):
    """Detect gesture from camera image using YOLOv5"""
    try:
        # Load model if not loaded
        if not gesture_service.model_loaded:
            gesture_service.load_model()
        
        # Detect gesture
        result = gesture_service.detect_gesture(request.image_data)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Save to history
        history = TranslationHistory(
            session_id=request.session_id,
            translation_type="sign_to_speech",
            input_data="image_data",
            output_data=json.dumps(result),
            language="both",
            confidence=result.get("confidence")
        )
        
        await db.translation_history.insert_one(history.dict())
        
        return {
            "success": True,
            "detection": result,
            "session_id": request.session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gesture detection failed: {str(e)}")

@api_router.post("/speech-to-sign")
async def speech_to_sign(request: SpeechToSignRequest):
    """Convert speech to sign language gestures"""
    try:
        # Convert audio to text
        text = speech_service.speech_to_text(
            request.audio_data.encode(), 
            request.language
        )
        
        if not text or "Error" in text:
            raise HTTPException(status_code=400, detail="Speech recognition failed")
        
        # Find corresponding gesture
        gesture_match = speech_service.find_gesture_for_text(text, request.language)
        
        result = {
            "recognized_text": text,
            "language": request.language,
            "gesture_found": gesture_match is not None
        }
        
        if gesture_match:
            result.update({
                "gesture": gesture_match["gesture"],
                "gesture_data": gesture_match["data"]
            })
        else:
            result["message"] = "No matching gesture found for this speech"
        
        # Save to history
        history = TranslationHistory(
            session_id=request.session_id,
            translation_type="speech_to_sign",
            input_data=text,
            output_data=json.dumps(result),
            language=request.language
        )
        
        await db.translation_history.insert_one(history.dict())
        
        return {
            "success": True,
            "result": result,
            "session_id": request.session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech to sign conversion failed: {str(e)}")

@api_router.post("/text-to-sign")
async def text_to_sign(request: TextToSignRequest):
    """Convert text to sign language gestures"""
    try:
        # Find corresponding gesture
        gesture_match = speech_service.find_gesture_for_text(request.text, request.language)
        
        result = {
            "input_text": request.text,
            "language": request.language,
            "gesture_found": gesture_match is not None
        }
        
        if gesture_match:
            result.update({
                "gesture": gesture_match["gesture"],
                "gesture_data": gesture_match["data"]
            })
        else:
            result["message"] = "No matching gesture found for this text"
        
        # Save to history
        history = TranslationHistory(
            session_id=request.session_id,
            translation_type="text_to_sign",
            input_data=request.text,
            output_data=json.dumps(result),
            language=request.language
        )
        
        await db.translation_history.insert_one(history.dict())
        
        return {
            "success": True,
            "result": result,
            "session_id": request.session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text to sign conversion failed: {str(e)}")

@api_router.get("/history/{session_id}")
async def get_translation_history(session_id: str):
    """Get translation history for a session"""
    try:
        history = await db.translation_history.find(
            {"session_id": session_id}
        ).to_list(100)
        
        return {
            "success": True,
            "history": history,
            "count": len(history)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")

@api_router.get("/stats")
async def get_stats():
    """Get application statistics"""
    try:
        total_translations = await db.translation_history.count_documents({})
        sign_to_speech = await db.translation_history.count_documents({"translation_type": "sign_to_speech"})
        speech_to_sign = await db.translation_history.count_documents({"translation_type": "speech_to_sign"})
        
        return {
            "total_translations": total_translations,
            "sign_to_speech_count": sign_to_speech,
            "speech_to_sign_count": speech_to_sign,
            "available_gestures": len(MOCK_GESTURES),
            "model_status": "loaded" if gesture_service.model_loaded else "not_loaded"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Sign Language Translation API")
    gesture_service.load_model()
    logger.info("YOLOv5 model loaded successfully")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()