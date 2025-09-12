#!/usr/bin/env python3
"""
Speech to Sign Language Conversion
Converts Urdu/Pashto speech to corresponding hand gesture demonstrations
"""

import speech_recognition as sr
import json
import cv2
import numpy as np
import os
import time
import threading
from pathlib import Path
import argparse
from PIL import Image, ImageDraw, ImageFont
import pyttsx3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SpeechToSign:
    def __init__(self, labels_path="labels.json", images_path="gesture_images/"):
        """Initialize speech recognition and gesture display"""
        print("🎤 Initializing Speech to Sign converter...")
        
        # Load gesture labels and mappings
        try:
            with open(labels_path, 'r', encoding='utf-8') as f:
                self.labels = json.load(f)
            print(f"✅ Loaded {len(self.labels)} gesture labels")
        except Exception as e:
            print(f"❌ Error loading labels: {e}")
            self.create_default_labels()
        
        # Create reverse mapping for text to gesture lookup
        self.create_text_mappings()
        
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        try:
            self.microphone = sr.Microphone()
            
            # Test microphone availability
            print("🔧 Testing microphone...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("✅ Microphone working correctly")
        except Exception as e:
            print(f"⚠️ Microphone issue: {e}")
            print("💡 Microphone may not be available - text mode will work")
            self.microphone = None
        
        # Initialize TTS for feedback
        try:
            self.tts = pyttsx3.init()
            self.tts.setProperty('rate', 150)
            self.tts.setProperty('volume', 0.8)
        except:
            self.tts = None
            print("⚠️ TTS not available")
        
        # Gesture images path
        self.images_path = Path(images_path)
        self.images_path.mkdir(exist_ok=True)
        
        # Create sample gesture images if they don't exist
        self.ensure_gesture_images()
    
    def create_default_labels(self):
        """Create default Pakistani Sign Language labels"""
        self.labels = {
            0: {"name": "salam", "urdu": "سلام", "pashto": "سلام ورور", "english": "Hello"},
            1: {"name": "shukriya", "urdu": "شکریہ", "pashto": "مننه", "english": "Thank you"},
            2: {"name": "khuda_hafiz", "urdu": "خدا حافظ", "pashto": "خدای پامان", "english": "Goodbye"},
            3: {"name": "paani", "urdu": "پانی", "pashto": "اوبه", "english": "Water"},
            4: {"name": "khana", "urdu": "کھانا", "pashto": "خواړه", "english": "Food"},
            5: {"name": "madad", "urdu": "مدد", "pashto": "مرسته", "english": "Help"},
            6: {"name": "ek", "urdu": "ایک", "pashto": "یو", "english": "One"},
            7: {"name": "do", "urdu": "دو", "pashto": "دوه", "english": "Two"},
            8: {"name": "teen", "urdu": "تین", "pashto": "درې", "english": "Three"},
            9: {"name": "ghar", "urdu": "گھر", "pashto": "کور", "english": "Home"}
        }
        
        with open("labels.json", 'w', encoding='utf-8') as f:
            json.dump(self.labels, f, ensure_ascii=False, indent=2)
        print("📝 Created default labels.json file")
    
    def create_text_mappings(self):
        """Create mappings from text to gestures"""
        self.text_to_gesture = {}
        
        for class_id, gesture_info in self.labels.items():
            # Map English words
            english_words = gesture_info['english'].lower().split()
            for word in english_words:
                self.text_to_gesture[word] = gesture_info
            
            # Map gesture name
            self.text_to_gesture[gesture_info['name'].lower()] = gesture_info
            
            # Map Urdu text (simplified - in real app you'd use proper Urdu processing)
            urdu_keywords = {
                'سلام': 'salam',
                'شکریہ': 'shukriya', 
                'خدا حافظ': 'khuda_hafiz',
                'پانی': 'paani',
                'کھانا': 'khana',
                'مدد': 'madad',
                'ایک': 'ek',
                'دو': 'do', 
                'تین': 'teen',
                'گھر': 'ghar'
            }
            
            # Map Pashto text (simplified)
            pashto_keywords = {
                'سلام ورور': 'salam',
                'مننه': 'shukriya',
                'خدای پامان': 'khuda_hafiz', 
                'اوبه': 'paani',
                'خواړه': 'khana',
                'مرسته': 'madad',
                'یو': 'ek',
                'دوه': 'do',
                'درې': 'teen', 
                'کور': 'ghar'
            }
            
            # Add mappings
            for text, gesture_name in urdu_keywords.items():
                if gesture_info['name'] == gesture_name:
                    self.text_to_gesture[text] = gesture_info
            
            for text, gesture_name in pashto_keywords.items():
                if gesture_info['name'] == gesture_name:
                    self.text_to_gesture[text] = gesture_info
    
    def ensure_gesture_images(self):
        """Create sample gesture images if they don't exist"""
        for class_id, gesture_info in self.labels.items():
            image_path = self.images_path / f"{gesture_info['name']}.jpg"
            
            if not image_path.exists():
                self.create_sample_gesture_image(gesture_info, image_path)
    
    def create_sample_gesture_image(self, gesture_info, image_path):
        """Create a sample gesture demonstration image"""
        # Create a 400x300 image
        img = Image.new('RGB', (400, 300), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to load a font (fallback to default if not available)
        try:
            font_large = ImageFont.truetype("arial.ttf", 24)
            font_medium = ImageFont.truetype("arial.ttf", 18)
            font_small = ImageFont.truetype("arial.ttf", 14)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Draw gesture information
        y_pos = 50
        
        # Gesture name
        draw.text((200, y_pos), gesture_info['name'].upper(), fill='black', 
                 font=font_large, anchor="mt")
        y_pos += 40
        
        # English meaning
        draw.text((200, y_pos), gesture_info['english'], fill='blue', 
                 font=font_medium, anchor="mt")
        y_pos += 30
        
        # Urdu text
        draw.text((200, y_pos), gesture_info['urdu'], fill='green', 
                 font=font_medium, anchor="mt")
        y_pos += 30
        
        # Pashto text  
        draw.text((200, y_pos), gesture_info['pashto'], fill='purple', 
                 font=font_medium, anchor="mt")
        y_pos += 50
        
        # Simple hand drawing (basic representation)
        self.draw_simple_hand_gesture(draw, gesture_info['name'])
        
        # Instructions
        draw.text((200, 250), "Show this gesture to camera", fill='gray', 
                 font=font_small, anchor="mt")
        
        # Save image
        img.save(image_path)
        print(f"📷 Created sample image: {image_path}")
    
    def draw_simple_hand_gesture(self, draw, gesture_name):
        """Draw a simple hand representation based on gesture"""
        center_x, center_y = 200, 160
        
        if gesture_name == "salam":
            # Open palm
            draw.ellipse([center_x-40, center_y-30, center_x+40, center_y+30], 
                        outline='black', width=3)
            # Fingers
            for i in range(5):
                x = center_x - 30 + (i * 15)
                draw.line([x, center_y-30, x, center_y-50], fill='black', width=2)
        
        elif gesture_name == "ek":
            # One finger (index)
            draw.ellipse([center_x-30, center_y-20, center_x+30, center_y+20], 
                        outline='black', width=2)
            draw.line([center_x, center_y-20, center_x, center_y-45], fill='black', width=3)
        
        elif gesture_name == "do":
            # Two fingers (index and middle)
            draw.ellipse([center_x-30, center_y-20, center_x+30, center_y+20], 
                        outline='black', width=2)
            draw.line([center_x-5, center_y-20, center_x-5, center_y-45], fill='black', width=3)
            draw.line([center_x+5, center_y-20, center_x+5, center_y-45], fill='black', width=3)
        
        else:
            # Default hand
            draw.ellipse([center_x-35, center_y-25, center_x+35, center_y+25], 
                        outline='black', width=2, fill='lightgray')
    
    def listen_for_speech(self):
        """Listen for speech input using Google Speech API"""
        print("🎤 Listening for speech... (Say something in Urdu, Pashto, or English)")
        
        try:
            with self.microphone as source:
                # Listen for speech
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=5)
                
            print("🔄 Processing speech...")
            
            # Get Google API key from environment
            google_api_key = os.getenv('GOOGLE_SPEECH_API_KEY')
            
            recognized_text = None
            
            # Try to recognize speech in multiple languages with API key
            try:
                # Try English first with API key
                text = self.recognizer.recognize_google(audio, key=google_api_key, language='en')
                print(f"🔤 Recognized (English): {text}")
                recognized_text = text.lower()
            except:
                pass
            
            # If English failed, try Urdu
            if not recognized_text:
                try:
                    text = self.recognizer.recognize_google(audio, key=google_api_key, language='ur')
                    print(f"🔤 Recognized (Urdu): {text}")
                    recognized_text = text
                except:
                    pass
            
            # If both failed, try Pashto (use Farsi as closest match)
            if not recognized_text:
                try:
                    text = self.recognizer.recognize_google(audio, key=google_api_key, language='fa')
                    print(f"🔤 Recognized (Farsi/Pashto): {text}")
                    recognized_text = text
                except:
                    pass
                    
            # If all specific languages failed, try general recognition
            if not recognized_text:
                try:
                    text = self.recognizer.recognize_google(audio, key=google_api_key)
                    print(f"🔤 Recognized (Auto): {text}")
                    recognized_text = text.lower()
                except:
                    pass
            
            return recognized_text
            
        except sr.WaitTimeoutError:
            print("⏰ No speech detected within timeout")
            return None
        except sr.UnknownValueError:
            print("❓ Could not understand speech")
            return None
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            # Fallback to free Google Speech Recognition
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
                text = self.recognizer.recognize_google(audio)
                print(f"🔤 Recognized (Fallback): {text}")
                return text.lower()
            except:
                print("❌ Fallback recognition also failed")
                return None
    
    def find_gesture_for_text(self, text):
        """Find matching gesture for recognized text"""
        if not text:
            return None
        
        text = text.lower().strip()
        print(f"🔍 Searching for gestures matching: '{text}'")
        
        # Direct match
        if text in self.text_to_gesture:
            return self.text_to_gesture[text]
        
        # Partial word matching
        for keyword, gesture_info in self.text_to_gesture.items():
            if keyword in text or text in keyword:
                print(f"✅ Found partial match: '{keyword}' in '{text}'")
                return gesture_info
        
        # Check individual words
        words = text.split()
        for word in words:
            if word in self.text_to_gesture:
                return self.text_to_gesture[word]
        
        print("❌ No matching gesture found")
        return None
    
    def display_gesture(self, gesture_info):
        """Display the gesture with 3D animated character"""
        print("=" * 50)
        print(f"🤟 GESTURE: {gesture_info['name'].upper()}")
        print(f"🏴󠁧󠁢󠁥󠁮󠁧󠁿 English: {gesture_info['english']}")
        print(f"🇵🇰 Urdu: {gesture_info['urdu']}")
        print(f"🇦🇫 Pashto: {gesture_info['pashto']}")
        print("=" * 50)
        
        # Import and create 3D character
        try:
            from character_3d import SignLanguageCharacter
            
            print("🎭 Starting 3D character animation...")
            character = SignLanguageCharacter()
            
            # Animate the gesture
            success = character.run_animation_loop(gesture_info['name'], duration=4.0)
            character.cleanup()
            
            if success:
                print("✅ 3D animation completed successfully!")
            else:
                print("⚠️ 3D animation interrupted by user")
                
        except Exception as e:
            print(f"⚠️ Could not display 3D character: {e}")
            print("📱 Falling back to image display...")
            
            # Fallback to image display
            image_path = self.images_path / f"{gesture_info['name']}.jpg"
            
            if image_path.exists():
                try:
                    img = cv2.imread(str(image_path))
                    if img is not None:
                        # Resize for display
                        img = cv2.resize(img, (600, 450))
                        
                        # Add text overlays
                        cv2.putText(img, f"Gesture: {gesture_info['name']}", (20, 30), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        cv2.putText(img, f"English: {gesture_info['english']}", (20, 70), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                        cv2.putText(img, "Press any key to continue", (20, 420), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        
                        cv2.imshow(f"Pakistani Sign Language - {gesture_info['name']}", img)
                        cv2.waitKey(0)  # Wait for key press
                        cv2.destroyAllWindows()
                        
                except Exception as e:
                    print(f"❌ Error displaying image: {e}")
        
        # Provide TTS feedback
        if self.tts:
            try:
                feedback = f"Gesture for {gesture_info['english']}. The animated character showed how to sign this."
                self.tts.say(feedback)
                self.tts.runAndWait()
            except:
                pass
    
    def run_conversion(self):
        """Main conversion loop"""
        print("\n🎤 Speech to Sign Language Mode")
        print("🗣️ Speak words in Urdu, Pashto, or English")
        print("🤟 The 3D character will demonstrate the gestures")
        print("❌ Press Ctrl+C to return to main menu")
        
        if not self.microphone:
            print("⚠️ Microphone not available - switching to text input mode")
            return self.text_input_mode()
        
        try:
            while True:
                print("\n" + "="*60)
                print("🎯 Choose input method:")
                print("1. 🎤 Voice Input (Microphone)")
                print("2. ✏️  Text Input")
                print("3. 🔙 Return to Main Menu")
                
                choice = input("👉 Enter choice (1-3): ").strip()
                
                if choice == '1':
                    self.voice_input_mode()
                elif choice == '2':
                    self.text_input_mode()
                elif choice == '3':
                    break
                else:
                    print("❌ Invalid choice. Please enter 1-3.")
                    
        except KeyboardInterrupt:
            print("\n🛑 Speech to Sign converter stopped by user")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        finally:
            print("👋 Goodbye!")
    
    def voice_input_mode(self):
        """Voice input mode with microphone"""
        print("\n🎤 Voice Input Mode Active")
        print("🗣️ Speak clearly into the microphone...")
        
        try:
            for i in range(3):  # Try 3 times
                print(f"\n🎯 Attempt {i+1}/3")
                
                # Listen for speech
                recognized_text = self.listen_for_speech()
                
                if recognized_text:
                    print(f"✅ You said: '{recognized_text}'")
                    
                    # Find matching gesture
                    gesture_info = self.find_gesture_for_text(recognized_text)
                    
                    if gesture_info:
                        self.display_gesture(gesture_info)
                        return
                    else:
                        print("❌ Sorry, no gesture found for that speech")
                        print("💡 Try saying: hello, thank you, water, food, help, one, two, three")
                else:
                    print("🔄 No speech recognized. Please try again.")
                    
            print("⚠️ Voice recognition failed after 3 attempts. Switching to text mode.")
            self.text_input_mode()
            
        except Exception as e:
            print(f"❌ Voice input error: {e}")
            print("💡 Switching to text mode...")
            self.text_input_mode()
    
    def text_input_mode(self):
        """Text input mode as fallback"""
        print("\n✏️ Text Input Mode")
        print("📝 Type words in Urdu, Pashto, or English")
        
        while True:
            try:
                text_input = input("\n👉 Enter text (or 'quit' to exit): ").strip()
                
                if text_input.lower() in ['quit', 'exit', 'q']:
                    break
                    
                if not text_input:
                    continue
                
                print(f"✅ Processing: '{text_input}'")
                
                # Find matching gesture
                gesture_info = self.find_gesture_for_text(text_input)
                
                if gesture_info:
                    self.display_gesture(gesture_info)
                else:
                    print("❌ Sorry, no gesture found for that text")
                    print("💡 Try typing: hello, thank you, water, food, help, one, two, three")
                    
            except KeyboardInterrupt:
                print("\n🔙 Returning to main menu...")
                break

def main():
    parser = argparse.ArgumentParser(description='Pakistani Speech to Sign Language Converter')
    parser.add_argument('--labels', default='labels.json', help='Path to labels file')
    parser.add_argument('--images', default='gesture_images/', help='Path to gesture images directory')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎤 PAKISTANI SPEECH TO SIGN LANGUAGE CONVERTER")
    print("=" * 60)
    print("🧠 Technology: Speech Recognition + 3D Animation")
    print("🇵🇰 Languages: Urdu, Pashto, English")
    print("🎤 Input: Voice/Speech")
    print("🤟 Output: Hand gesture demonstrations")
    print("=" * 60)
    
    # Create converter instance
    converter = SpeechToSign(labels_path=args.labels, images_path=args.images)
    
    # Start conversion
    converter.run_conversion()

if __name__ == "__main__":
    main()