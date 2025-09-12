#!/usr/bin/env python3
"""
Pakistani Sign Language Translation App with 3D Character
Complete application with Speech-to-Sign, Text-to-Sign, and 3D animated character
"""

import argparse
import json
import time
import threading
import os
from pathlib import Path
import speech_recognition as sr
import pyttsx3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PakistaniSignLanguageApp:
    def __init__(self, labels_path="labels.json", images_path="gesture_images/"):
        """Initialize the complete sign language application"""
        print("🚀 Initializing Pakistani Sign Language Translation App...")
        
        # Load gesture labels and mappings
        try:
            with open(labels_path, 'r', encoding='utf-8') as f:
                self.labels = json.load(f)
            print(f"✅ Loaded {len(self.labels)} gesture labels")
        except Exception as e:
            print(f"❌ Error loading labels: {e}")
            return
        
        # Create reverse mapping for text to gesture lookup
        self.create_text_mappings()
        
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        try:
            self.microphone = sr.Microphone()
            
            # Adjust for ambient noise
            print("🔧 Calibrating microphone for ambient noise...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            print("✅ Microphone calibrated")
        except Exception as e:
            print(f"⚠️ Microphone not available: {e}")
            self.microphone = None
        
        # Initialize TTS for feedback
        try:
            self.tts = pyttsx3.init()
            self.tts.setProperty('rate', 150)
            self.tts.setProperty('volume', 0.8)
            print("✅ Text-to-speech initialized")
        except:
            self.tts = None
            print("⚠️ TTS not available")
        
        # Gesture images path
        self.images_path = Path(images_path)
        self.images_path.mkdir(exist_ok=True)
        
        # Create sample gesture images if they don't exist
        self.ensure_gesture_images()
        
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
            
            # Map Urdu and Pashto text
            self.text_to_gesture[gesture_info['urdu']] = gesture_info
            self.text_to_gesture[gesture_info['pashto']] = gesture_info
    
    def ensure_gesture_images(self):
        """Create sample gesture images if they don't exist"""
        from PIL import Image, ImageDraw, ImageFont
        
        for class_id, gesture_info in self.labels.items():
            image_path = self.images_path / f"{gesture_info['name']}.jpg"
            
            if not image_path.exists():
                self.create_sample_gesture_image(gesture_info, image_path)
    
    def create_sample_gesture_image(self, gesture_info, image_path):
        """Create a sample gesture demonstration image"""
        from PIL import Image, ImageDraw, ImageFont
        
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
        
        # Instructions
        draw.text((200, 250), "3D Character will demonstrate this gesture", fill='gray', 
                 font=font_small, anchor="mt")
        
        # Save image
        img.save(image_path)
        print(f"📷 Created sample image: {image_path}")
    
    def speech_to_sign(self):
        """Convert speech input to sign language gestures"""
        if not self.microphone:
            print("❌ Microphone not available for speech recognition")
            return
            
        print("🎤 Speech to Sign Language Mode")
        print("🗣️ Speak words in Urdu, Pashto, or English")
        print("🤟 The 3D character will demonstrate the gestures")
        print("❌ Press Ctrl+C to return to main menu")
        
        try:
            while True:
                print("\n" + "="*60)
                print("🎤 Listening... (speak now)")
                
                recognized_text = self.listen_for_speech()
                
                if recognized_text:
                    print(f"🔤 You said: '{recognized_text}'")
                    
                    # Find matching gesture
                    gesture_info = self.find_gesture_for_text(recognized_text)
                    
                    if gesture_info:
                        print(f"✅ Found gesture: {gesture_info['name']}")
                        self.display_gesture_with_character(gesture_info)
                    else:
                        print("❌ Sorry, no gesture found for that speech")
                        print("💡 Try saying: hello, thank you, water, food, help, one, two, three")
                        
                        if self.tts:
                            self.tts.say("Sorry, no matching gesture found. Try different words.")
                            self.tts.runAndWait()
                else:
                    print("🔄 No speech recognized. Please try again.")
                
                time.sleep(0.5)  # Brief pause before next iteration
                
        except KeyboardInterrupt:
            print("\n🔙 Returning to main menu...")
    
    def text_to_sign(self):
        """Convert text input to sign language gestures"""
        print("✏️ Text to Sign Language Mode")
        print("📝 Type words in Urdu, Pashto, or English")
        print("🤟 The 3D character will demonstrate the gestures")
        print("❌ Type 'quit' or 'exit' to return to main menu")
        
        while True:
            try:
                print("\n" + "="*60)
                text_input = input("📝 Enter text: ").strip()
                
                if text_input.lower() in ['quit', 'exit', 'q']:
                    print("🔙 Returning to main menu...")
                    break
                    
                if not text_input:
                    continue
                
                print(f"🔤 Processing: '{text_input}'")
                
                # Find matching gesture
                gesture_info = self.find_gesture_for_text(text_input)
                
                if gesture_info:
                    print(f"✅ Found gesture: {gesture_info['name']}")
                    self.display_gesture_with_character(gesture_info)
                else:
                    print("❌ Sorry, no gesture found for that text")
                    print("💡 Try typing: hello, thank you, water, food, help, one, two, three")
                    
                    if self.tts:
                        self.tts.say("Sorry, no matching gesture found. Try different words.")
                        self.tts.runAndWait()
                        
            except KeyboardInterrupt:
                print("\n🔙 Returning to main menu...")
                break
    
    def listen_for_speech(self):
        """Listen for speech input using Google Speech API"""
        try:
            with self.microphone as source:
                # Listen for speech
                audio = self.recognizer.listen(source, timeout=8, phrase_time_limit=5)
                
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
                    audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=3)
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
            if isinstance(keyword, str):
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
    
    def display_gesture_with_character(self, gesture_info):
        """Display the gesture using 3D animated character"""
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
            print("🎮 The animated character will now demonstrate the gesture!")
            print("🎮 Press ESC or close the window when done watching")
            
            character = SignLanguageCharacter(width=900, height=700)
            
            # Animate the gesture
            success = character.run_animation_loop(gesture_info['name'], duration=5.0)
            character.cleanup()
            
            if success:
                print("✅ 3D animation completed successfully!")
            else:
                print("⚠️ 3D animation was closed by user")
                
        except Exception as e:
            print(f"⚠️ Could not display 3D character: {e}")
            print("📱 The animated character feature requires a display")
            
        # Provide TTS feedback
        if self.tts:
            try:
                feedback = f"Gesture demonstrated: {gesture_info['english']}. In Urdu: {gesture_info['urdu']}. In Pashto: {gesture_info['pashto']}"
                print("🔊 Speaking gesture information...")
                self.tts.say(feedback)
                self.tts.runAndWait()
            except Exception as e:
                print(f"⚠️ TTS error: {e}")
    
    def show_available_gestures(self):
        """Show all available gestures"""
        print("\n🤟 Available Pakistani Sign Language Gestures:")
        print("=" * 80)
        
        categories = {
            "Numbers": ["ek", "do", "teen", "chaar", "paanch", "che", "saat", "aath", "nau", "das"],
            "Greetings": ["salam", "shukriya", "khuda_hafiz"],
            "Family": ["ammi", "abbu", "bhai", "behn"],
            "Basic Needs": ["paani", "khana", "madad"],
            "Actions": ["reading", "writing", "listening", "speaking", "eating", "drinking"],
            "Objects": ["kitab", "qalam", "ghar", "school", "hospital"],
            "Emotions": ["khushi", "gham", "mohabbat"]
        }
        
        for category, gestures in categories.items():
            print(f"\n📂 {category}:")
            for gesture in gestures:
                if gesture in [info['name'] for info in self.labels.values()]:
                    # Find the gesture info
                    for info in self.labels.values():
                        if info['name'] == gesture:
                            print(f"  🤟 {gesture:<12} | {info['english']:<15} | {info['urdu']:<10} | {info['pashto']}")
                            break
        
        print(f"\n📊 Total gestures available: {len(self.labels)}")
        print("💡 You can use any of these gestures in speech or text mode!")
    
    def run(self):
        """Run the main application"""
        print("\n" + "=" * 70)
        print("🇵🇰 PAKISTANI SIGN LANGUAGE TRANSLATION APP WITH 3D CHARACTER")
        print("=" * 70)
        print("🧠 AI: YOLOv5 + Speech Recognition + 3D Animation")
        print("🌐 Languages: Urdu, Pashto, English")
        print("🎭 Features: 3D Animated Character Demonstrations")
        print("🤟 Gestures: 132 Pakistani Sign Language gestures")
        print("=" * 70)
        
        while True:
            try:
                print("\n🎯 Choose an option:")
                print("1. 🎤 Speech to Sign Language (with 3D character)")
                print("2. ✏️  Text to Sign Language (with 3D character)")
                print("3. 📋 Show Available Gestures")
                print("4. 🎭 Demo 3D Character")
                print("5. 📚 Pakistani Story Mode (انگور تو کھٹے ہیں)")
                print("6. ❌ Exit")
                
                choice = input("\n👉 Enter your choice (1-6): ").strip()
                
                if choice == '1':
                    self.speech_to_sign()
                elif choice == '2':
                    self.text_to_sign()
                elif choice == '3':
                    self.show_available_gestures()
                elif choice == '4':
                    self.demo_character()
                elif choice == '5':
                    self.run_story_mode()
                elif choice == '6':
                    print("👋 Thank you for using Pakistani Sign Language App!")
                    print("🇵🇰 Goodbye! خدا حافظ! خدای پامان!")
                    break
                else:
                    print("❌ Invalid choice. Please enter 1-6.")
                    
            except KeyboardInterrupt:
                print("\n👋 Application terminated by user")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
    
    def demo_character(self):
        """Demo the 3D character with sample gestures"""
        print("\n🎭 3D Character Demo")
        print("🎮 The animated character will demonstrate various gestures")
        print("⏰ Each gesture will be shown for a few seconds")
        print("❌ Press ESC or close window to stop demo")
        
        demo_gestures = [
            'salam', 'shukriya', 'khuda_hafiz',
            'ek', 'do', 'teen', 'chaar', 'paanch',
            'paani', 'khana', 'madad', 'ammi', 'abbu',
            'reading', 'writing', 'listening', 'speaking'
        ]
        
        try:
            from character_3d import SignLanguageCharacter
            character = SignLanguageCharacter(width=900, height=700)
            
            for gesture in demo_gestures:
                # Find gesture info
                gesture_info = None
                for info in self.labels.values():
                    if info['name'] == gesture:
                        gesture_info = info
                        break
                
                if gesture_info:
                    print(f"🎭 Demonstrating: {gesture} ({gesture_info['english']})")
                    if not character.run_animation_loop(gesture, 3.0):
                        break
                    time.sleep(0.5)
                    
            character.cleanup()
            print("✅ Demo completed!")
            
        except Exception as e:
            print(f"❌ Could not run character demo: {e}")
    
    def pakistani_story_mode(self):
        """Interactive Pakistani story mode with sign language"""
        print("\n📚 Pakistani Story Mode: انگور تو کھٹے ہیں (The Grapes are Sour)")
        print("=" * 70)
        print("🦊 A classic Aesop's fable in Pakistani context")
        print("🤟 Watch the story unfold with sign language gestures")
        print("🎭 3D character will demonstrate key words and phrases")
        print("❌ Press ESC or close window to exit story mode")
        print("=" * 70)
        
        # Story segments with corresponding gestures
        story_segments = [
            {
                "text": "ایک دن، ایک بھوکا لومڑی باغ میں گھوم رہا تھا۔",
                "english": "One day, a hungry fox was wandering in the garden.",
                "gestures": ["ek", "khana", "ghar"]
            },
            {
                "text": "اس نے اونچی بیل پر لٹکے ہوئے انگور دیکھے۔",
                "english": "He saw grapes hanging on a high vine.",
                "gestures": ["paani", "khushi"]
            },
            {
                "text": "لومڑی نے کہا: 'یہ انگور بہت مزیدار لگ رہے ہیں!'",
                "english": "The fox said: 'These grapes look very delicious!'",
                "gestures": ["speaking", "khushi"]
            },
            {
                "text": "اس نے اچھلنے کی کوشش کی لیکن انگور تک نہیں پہنچ سکا۔",
                "english": "He tried to jump but couldn't reach the grapes.",
                "gestures": ["madad", "gham"]
            },
            {
                "text": "بار بار کوشش کے بعد، لومڑی تھک گیا۔",
                "english": "After trying many times, the fox got tired.",
                "gestures": ["gham", "madad"]
            },
            {
                "text": "آخر میں اس نے کہا: 'یہ انگور تو کھٹے ہیں!'",
                "english": "Finally he said: 'These grapes are sour!'",
                "gestures": ["speaking", "gham"]
            },
            {
                "text": "اور وہ واپس چلا گیا۔",
                "english": "And he went back.",
                "gestures": ["khuda_hafiz"]
            }
        ]
        
        moral = {
            "urdu": "سبق: جو چیز ہمیں نہیں مل سکتی، ہم اسے برا کہہ دیتے ہیں۔",
            "english": "Moral: We often despise what we cannot have.",
            "gestures": ["kitab", "mohabbat"]
        }
        
        try:
            from character_3d import SignLanguageCharacter
            character = SignLanguageCharacter(width=900, height=700)
            
            print("\n🎬 Story begins...")
            time.sleep(2)
            
            for i, segment in enumerate(story_segments, 1):
                print(f"\n📖 Part {i}:")
                print(f"🇵🇰 {segment['text']}")
                print(f"🏴󠁧󠁢󠁥󠁮󠁧󠁿 {segment['english']}")
                
                # Demonstrate key gestures for this segment
                print("🤟 Key gestures for this part:")
                for gesture_name in segment['gestures']:
                    # Find gesture info
                    gesture_info = None
                    for info in self.labels.values():
                        if info['name'] == gesture_name:
                            gesture_info = info
                            break
                    
                    if gesture_info:
                        print(f"  🎭 Demonstrating: {gesture_name} ({gesture_info['english']})")
                        if not character.run_animation_loop(gesture_name, 2.0):
                            character.cleanup()
                            return
                        time.sleep(0.5)
                
                # Pause between segments
                input("\n⏸️  Press Enter to continue to next part...")
            
            # Show moral of the story
            print("\n" + "=" * 50)
            print("📚 MORAL OF THE STORY:")
            print(f"🇵🇰 {moral['urdu']}")
            print(f"🏴󠁧󠁢󠁥󠁮󠁧󠁿 {moral['english']}")
            print("=" * 50)
            
            # Demonstrate moral gestures
            print("🤟 Final gestures:")
            for gesture_name in moral['gestures']:
                gesture_info = None
                for info in self.labels.values():
                    if info['name'] == gesture_name:
                        gesture_info = info
                        break
                
                if gesture_info:
                    print(f"  🎭 Demonstrating: {gesture_name} ({gesture_info['english']})")
                    if not character.run_animation_loop(gesture_name, 3.0):
                        break
                    time.sleep(0.5)
            
            character.cleanup()
            print("\n✅ Story completed! Thank you for watching!")
            print("🎓 You learned sign language through storytelling!")
            
            # TTS feedback
            if self.tts:
                self.tts.say("Story completed! You learned Pakistani sign language through the tale of the fox and grapes.")
                self.tts.runAndWait()
                
        except Exception as e:
            print(f"❌ Could not run story mode: {e}")
            print("📱 Story mode requires a display for 3D character")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Pakistani Sign Language Translation with 3D Character')
    parser.add_argument('--labels', default='labels.json', help='Path to labels file')
    parser.add_argument('--images', default='gesture_images/', help='Path to gesture images directory')
    
    args = parser.parse_args()
    
    # Create and run the application
    app = PakistaniSignLanguageApp(labels_path=args.labels, images_path=args.images)
    app.run()

if __name__ == "__main__":
    main()