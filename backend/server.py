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

# Configure logging early
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

# Mock Pakistani Sign Language Dataset - 100 Gestures
MOCK_GESTURES = {
    # Basic Greetings & Social
    "salam": {"urdu": "سلام", "pashto": "سلام ورور", "meaning": "Hello/Greetings"},
    "shukriya": {"urdu": "شکریہ", "pashto": "مننه", "meaning": "Thank you"},
    "khuda_hafiz": {"urdu": "خدا حافظ", "pashto": "خدای پامان", "meaning": "Goodbye"},
    "maaf_karna": {"urdu": "معاف کرنا", "pashto": "بخښنه غواړم", "meaning": "Sorry"},
    "kya_hal": {"urdu": "کیا حال", "pashto": "څه خبره", "meaning": "How are you"},
    "khush_amadeed": {"urdu": "خوش آمدید", "pashto": "ښه راغلاست", "meaning": "Welcome"},
    "allah_hafiz": {"urdu": "اللہ حافظ", "pashto": "اللہ دی پامان", "meaning": "May Allah protect you"},
    
    # Family Members
    "ammi": {"urdu": "امی", "pashto": "مور", "meaning": "Mother"},
    "abbu": {"urdu": "ابو", "pashto": "پلار", "meaning": "Father"},
    "bhai": {"urdu": "بھائی", "pashto": "ورور", "meaning": "Brother"},
    "behn": {"urdu": "بہن", "pashto": "خور", "meaning": "Sister"},
    "dada": {"urdu": "دادا", "pashto": "نیکه", "meaning": "Grandfather"},
    "dadi": {"urdu": "دادی", "pashto": "انا", "meaning": "Grandmother"},
    "chacha": {"urdu": "چاچا", "pashto": "تره", "meaning": "Uncle"},
    "khala": {"urdu": "خالہ", "pashto": "ترور", "meaning": "Aunt"},
    "beta": {"urdu": "بیٹا", "pashto": "زوی", "meaning": "Son"},
    "beti": {"urdu": "بیٹی", "pashto": "لور", "meaning": "Daughter"},
    
    # Basic Needs & Objects  
    "paani": {"urdu": "پانی", "pashto": "اوبه", "meaning": "Water"},
    "khana": {"urdu": "کھانا", "pashto": "خواړه", "meaning": "Food"},
    "ghar": {"urdu": "گھر", "pashto": "کور", "meaning": "Home"},
    "kitab": {"urdu": "کتاب", "pashto": "کتاب", "meaning": "Book"},
    "qalam": {"urdu": "قلم", "pashto": "قلم", "meaning": "Pen"},
    "kaam": {"urdu": "کام", "pashto": "کار", "meaning": "Work"},
    "dost": {"urdu": "دوست", "pashto": "ملګری", "meaning": "Friend"},
    "madad": {"urdu": "مدد", "pashto": "مرسته", "meaning": "Help"},
    "kamra": {"urdu": "کمرہ", "pashto": "کوټه", "meaning": "Room"},
    "darwaza": {"urdu": "دروازہ", "pashto": "دروازه", "meaning": "Door"},
    
    # Food Items
    "roti": {"urdu": "روٹی", "pashto": "ډوډۍ", "meaning": "Bread"},
    "chawal": {"urdu": "چاول", "pashto": "وریژې", "meaning": "Rice"},
    "gosht": {"urdu": "گوشت", "pashto": "غوښه", "meaning": "Meat"},
    "dudh": {"urdu": "دودھ", "pashto": "شیدې", "meaning": "Milk"},
    "chai": {"urdu": "چائے", "pashto": "چای", "meaning": "Tea"},
    "phal": {"urdu": "پھل", "pashto": "میوه", "meaning": "Fruit"},
    "sabzi": {"urdu": "سبزی", "pashto": "سابه", "meaning": "Vegetable"},
    "namak": {"urdu": "نمک", "pashto": "مالګه", "meaning": "Salt"},
    "cheeni": {"urdu": "چینی", "pashto": "شکره", "meaning": "Sugar"},
    "tel": {"urdu": "تیل", "pashto": "غوړ", "meaning": "Oil"},
    
    # Body Parts
    "sar": {"urdu": "سر", "pashto": "سر", "meaning": "Head"},
    "ankh": {"urdu": "آنکھ", "pashto": "سترګه", "meaning": "Eye"},
    "kaan": {"urdu": "کان", "pashto": "غوږ", "meaning": "Ear"},
    "naak": {"urdu": "ناک", "pashto": "پزه", "meaning": "Nose"},
    "munh": {"urdu": "منہ", "pashto": "خوله", "meaning": "Mouth"},
    "haath": {"urdu": "ہاتھ", "pashto": "لاس", "meaning": "Hand"},
    "pair": {"urdu": "پیر", "pashto": "پښه", "meaning": "Foot"},
    "dil": {"urdu": "دل", "pashto": "زړه", "meaning": "Heart"},
    "pet": {"urdu": "پیٹ", "pashto": "خیټه", "meaning": "Stomach"},
    "tang": {"urdu": "ٹانگ", "pashto": "پښه", "meaning": "Leg"},
    
    # Colors
    "safed": {"urdu": "سفید", "pashto": "سپین", "meaning": "White"},
    "kala": {"urdu": "کالا", "pashto": "تور", "meaning": "Black"},
    "lal": {"urdu": "لال", "pashto": "سور", "meaning": "Red"},
    "hara": {"urdu": "ہرا", "pashto": "شین", "meaning": "Green"},
    "neela": {"urdu": "نیلا", "pashto": "شین", "meaning": "Blue"},
    "peela": {"urdu": "پیلا", "pashto": "ژیړ", "meaning": "Yellow"},
    "gulabi": {"urdu": "گلابی", "pashto": "ګلابي", "meaning": "Pink"},
    "narangi": {"urdu": "نارنگی", "pashto": "نارنجي", "meaning": "Orange"},
    
    # Numbers 1-10
    "ek": {"urdu": "ایک", "pashto": "یو", "meaning": "One"},
    "do": {"urdu": "دو", "pashto": "دوه", "meaning": "Two"},
    "teen": {"urdu": "تین", "pashto": "درې", "meaning": "Three"},
    "chaar": {"urdu": "چار", "pashto": "څلور", "meaning": "Four"},
    "paanch": {"urdu": "پانچ", "pashto": "پنځه", "meaning": "Five"},
    "che": {"urdu": "چھ", "pashto": "شپږ", "meaning": "Six"},
    "saat": {"urdu": "سات", "pashto": "اووه", "meaning": "Seven"},
    "aath": {"urdu": "آٹھ", "pashto": "اته", "meaning": "Eight"},
    "nau": {"urdu": "نو", "pashto": "نهه", "meaning": "Nine"},
    "das": {"urdu": "دس", "pashto": "لس", "meaning": "Ten"},
    
    # Emotions & States
    "khush": {"urdu": "خوش", "pashto": "خوښ", "meaning": "Happy"},
    "udaas": {"urdu": "اداس", "pashto": "خپه", "meaning": "Sad"},
    "gussa": {"urdu": "غصہ", "pashto": "قهر", "meaning": "Angry"},
    "dar": {"urdu": "ڈر", "pashto": "ویره", "meaning": "Fear"},
    "mohabbat": {"urdu": "محبت", "pashto": "مینه", "meaning": "Love"},
    "thak_gaya": {"urdu": "تھک گیا", "pashto": "ستړی یم", "meaning": "Tired"},
    "beemar": {"urdu": "بیمار", "pashto": "ناروغ", "meaning": "Sick"},
    "sehat_mand": {"urdu": "صحت مند", "pashto": "روغ", "meaning": "Healthy"},
    
    # Daily Activities
    "uthna": {"urdu": "اٹھنا", "pashto": "پاڅیدل", "meaning": "Wake up"},
    "sona": {"urdu": "سونا", "pashto": "ویده کیدل", "meaning": "Sleep"},
    "khana_khana": {"urdu": "کھانا کھانا", "pashto": "خواړه خوړل", "meaning": "Eat food"},
    "paani_peena": {"urdu": "پانی پینا", "pashto": "اوبه څښل", "meaning": "Drink water"},
    "nahana": {"urdu": "نہانا", "pashto": "حمام کول", "meaning": "Take bath"},
    "parhna": {"urdu": "پڑھنا", "pashto": "لوستل", "meaning": "Read"},
    "likhna": {"urdu": "لکھنا", "pashto": "لیکل", "meaning": "Write"},
    "chalna": {"urdu": "چلنا", "pashto": "تلل", "meaning": "Walk"},
    "daura": {"urdu": "دوڑنا", "pashto": "منډه کول", "meaning": "Run"},
    "baitna": {"urdu": "بیٹھنا", "pashto": "کښیناستل", "meaning": "Sit"},
    
    # Education & Learning
    "school": {"urdu": "اسکول", "pashto": "ښوونځی", "meaning": "School"},
    "teacher": {"urdu": "استاد", "pashto": "ښوونکی", "meaning": "Teacher"},
    "student": {"urdu": "طالب علم", "pashto": "زده کوونکی", "meaning": "Student"},
    "exam": {"urdu": "امتحان", "pashto": "ازموینه", "meaning": "Examination"},
    "homework": {"urdu": "گھر کا کام", "pashto": "د کور کار", "meaning": "Homework"},
    "lesson": {"urdu": "سبق", "pashto": "درس", "meaning": "Lesson"},
    "university": {"urdu": "یونیورسٹی", "pashto": "پوهنتون", "meaning": "University"},  
    "degree": {"urdu": "ڈگری", "pashto": "سند", "meaning": "Degree"},
    
    # Professional & Work
    "doctor": {"urdu": "ڈاکٹر", "pashto": "ډاکټر", "meaning": "Doctor"},
    "engineer": {"urdu": "انجینیر", "pashto": "انجنیر", "meaning": "Engineer"},
    "lawyer": {"urdu": "وکیل", "pashto": "وکیل", "meaning": "Lawyer"},
    "police": {"urdu": "پولیس", "pashto": "پولیس", "meaning": "Police"},
    "driver": {"urdu": "ڈرائیور", "pashto": "موټر چلوونکی", "meaning": "Driver"},
    "shopkeeper": {"urdu": "دکاندار", "pashto": "دکاندار", "meaning": "Shopkeeper"},
    "farmer": {"urdu": "کسان", "pashto": "بزګر", "meaning": "Farmer"},
    "office": {"urdu": "دفتر", "pashto": "دفتر", "meaning": "Office"},
    
    # Transportation
    "gari": {"urdu": "گاڑی", "pashto": "موټر", "meaning": "Car"},
    "bus": {"urdu": "بس", "pashto": "بس", "meaning": "Bus"},
    "rickshaw": {"urdu": "رکشہ", "pashto": "رکشا", "meaning": "Rickshaw"},
    "cycle": {"urdu": "سائیکل", "pashto": "بایسکل", "meaning": "Bicycle"},
    "train": {"urdu": "ریل گاڑی", "pashto": "اورګاډی", "meaning": "Train"},
    "plane": {"urdu": "ہوائی جہاز", "pashto": "الوتکه", "meaning": "Airplane"},
    
    # Time & Weather
    "waqt": {"urdu": "وقت", "pashto": "وخت", "meaning": "Time"},
    "din": {"urdu": "دن", "pashto": "ورځ", "meaning": "Day"},
    "raat": {"urdu": "رات", "pashto": "شپه", "meaning": "Night"},
    "subah": {"urdu": "صبح", "pashto": "سهار", "meaning": "Morning"},
    "shaam": {"urdu": "شام", "pashto": "ماښام", "meaning": "Evening"},
    "saal": {"urdu": "سال", "pashto": "کال", "meaning": "Year"},
    "mahina": {"urdu": "مہینہ", "pashto": "میاشت", "meaning": "Month"},
    "hafta": {"urdu": "ہفتہ", "pashto": "اونۍ", "meaning": "Week"},
    "barish": {"urdu": "بارش", "pashto": "باران", "meaning": "Rain"},
    "dhoop": {"urdu": "دھوپ", "pashto": "لمر", "meaning": "Sunshine"},
    
    # Religious Terms
    "namaz": {"urdu": "نماز", "pashto": "لمونځ", "meaning": "Prayer"},
    "quran": {"urdu": "قرآن", "pashto": "قرآن", "meaning": "Quran"},
    "masjid": {"urdu": "مسجد", "pashto": "جومات", "meaning": "Mosque"},
    "roza": {"urdu": "روزہ", "pashto": "روژه", "meaning": "Fast"},  
    "zakat": {"urdu": "زکات", "pashto": "زکات", "meaning": "Charity"},
    "hajj": {"urdu": "حج", "pashto": "حج", "meaning": "Pilgrimage"},
    "eid": {"urdu": "عید", "pashto": "اختر", "meaning": "Festival"},
    
    # Common Verbs
    "jana": {"urdu": "جانا", "pashto": "تلل", "meaning": "Go"},
    "ana": {"urdu": "آنا", "pashto": "راتلل", "meaning": "Come"},
    "karna": {"urdu": "کرنا", "pashto": "کول", "meaning": "Do"},
    "dekhna": {"urdu": "دیکھنا", "pashto": "کتل", "meaning": "See"},
    "sunna": {"urdu": "سننا", "pashto": "اورېدل", "meaning": "Listen"},
    "bolna": {"urdu": "بولنا", "pashto": "ویل", "meaning": "Speak"},
    "samjhna": {"urdu": "سمجھنا", "pashto": "پوهیدل", "meaning": "Understand"},
    "dena": {"urdu": "دینا", "pashto": "ورکول", "meaning": "Give"},
    "lena": {"urdu": "لینا", "pashto": "اخیستل", "meaning": "Take"},
    "kharidna": {"urdu": "خریدنا", "pashto": "اخیستل", "meaning": "Buy"}
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
        history_cursor = db.translation_history.find(
            {"session_id": session_id}
        ).limit(100)
        
        history = []
        async for doc in history_cursor:
            # Convert ObjectId to string and handle datetime serialization
            doc["_id"] = str(doc["_id"])
            if "timestamp" in doc and hasattr(doc["timestamp"], "isoformat"):
                doc["timestamp"] = doc["timestamp"].isoformat()
            history.append(doc)
        
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

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Sign Language Translation API")
    gesture_service.load_model()
    logger.info("YOLOv5 model loaded successfully")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()