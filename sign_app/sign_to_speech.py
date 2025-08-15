#!/usr/bin/env python3
"""
Real-time Sign Language to Speech Detection
Uses YOLOv5 for Pakistani gesture recognition with camera feed
"""

import cv2
import torch
import json
import pyttsx3
import threading
import time
import numpy as np
from pathlib import Path
import argparse

class SignToSpeech:
    def __init__(self, model_path="best.pt", labels_path="labels.json"):
        """Initialize YOLOv5 model and TTS engine"""
        print("🚀 Loading YOLOv5 model for Pakistani Sign Language...")
        
        # Load YOLOv5 model
        try:
            self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path)
            self.model.conf = 0.6  # Confidence threshold
            self.model.iou = 0.4   # IoU threshold
            print("✅ YOLOv5 model loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading YOLOv5 model: {e}")
            print("📝 Make sure 'best.pt' model file exists")
            exit(1)
        
        # Load gesture labels
        try:
            with open(labels_path, 'r', encoding='utf-8') as f:
                self.labels = json.load(f)
            print(f"✅ Loaded {len(self.labels)} gesture labels")
        except Exception as e:
            print(f"❌ Error loading labels: {e}")
            # Create default labels if file doesn't exist
            self.create_default_labels()
        
        # Initialize text-to-speech engine
        try:
            self.tts_engine = pyttsx3.init()
            # Set voice properties
            voices = self.tts_engine.getProperty('voices')
            if voices:
                self.tts_engine.setProperty('voice', voices[0].id)
            self.tts_engine.setProperty('rate', 150)  # Speaking rate
            self.tts_engine.setProperty('volume', 0.8)  # Volume level
            print("✅ TTS engine initialized")
        except Exception as e:
            print(f"⚠️ Warning: TTS engine error: {e}")
            self.tts_engine = None
        
        # Detection variables
        self.last_detection = ""
        self.last_detection_time = 0
        self.detection_cooldown = 2.0  # seconds
        self.speaking = False
    
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
        
        # Save default labels
        with open("labels.json", 'w', encoding='utf-8') as f:
            json.dump(self.labels, f, ensure_ascii=False, indent=2)
        print("📝 Created default labels.json file")
    
    def detect_gesture(self, frame):
        """Detect gesture in frame using YOLOv5"""
        try:
            # Run YOLOv5 inference
            results = self.model(frame)
            
            # Parse results
            detections = results.pandas().xyxy[0]
            
            if len(detections) > 0:
                # Get highest confidence detection
                best_detection = detections.loc[detections['confidence'].idxmax()]
                
                class_id = int(best_detection['class'])
                confidence = float(best_detection['confidence'])
                
                if class_id in self.labels and confidence > 0.6:
                    gesture_info = self.labels[class_id]
                    
                    # Draw bounding box
                    x1, y1, x2, y2 = map(int, [best_detection['xmin'], best_detection['ymin'], 
                                               best_detection['xmax'], best_detection['ymax']])
                    
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    # Add label
                    label = f"{gesture_info['name']}: {confidence:.2f}"
                    cv2.putText(frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    return gesture_info, confidence
                    
        except Exception as e:
            print(f"⚠️ Detection error: {e}")
        
        return None, 0
    
    def speak_gesture(self, gesture_info):
        """Convert gesture to speech"""
        if self.speaking or not self.tts_engine:
            return
        
        current_time = time.time()
        gesture_name = gesture_info['name']
        
        # Check cooldown to avoid repeated speech
        if (gesture_name == self.last_detection and 
            current_time - self.last_detection_time < self.detection_cooldown):
            return
        
        self.last_detection = gesture_name
        self.last_detection_time = current_time
        
        # Create speech text
        speech_text = f"Detected gesture: {gesture_info['english']}. In Urdu: {gesture_info['urdu']}. In Pashto: {gesture_info['pashto']}"
        
        # Speak in separate thread to avoid blocking
        def speak():
            try:
                self.speaking = True
                self.tts_engine.say(speech_text)
                self.tts_engine.runAndWait()
                self.speaking = False
            except Exception as e:
                print(f"⚠️ TTS error: {e}")
                self.speaking = False
        
        threading.Thread(target=speak, daemon=True).start()
        print(f"🗣️ Speaking: {speech_text}")
    
    def run_detection(self):
        """Main detection loop with camera feed"""
        print("📹 Starting camera feed...")
        print("🎯 Point hand gestures at the camera")
        print("🔊 Detected gestures will be spoken aloud")
        print("❌ Press 'q' to quit")
        
        # Initialize camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Error: Could not open camera")
            return
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        print("✅ Camera started successfully")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("❌ Error reading frame")
                    break
                
                # Flip frame horizontally (mirror effect)
                frame = cv2.flip(frame, 1)
                
                # Detect gesture
                gesture_info, confidence = self.detect_gesture(frame)
                
                # If gesture detected, speak it
                if gesture_info and confidence > 0.7:
                    self.speak_gesture(gesture_info)
                
                # Add info overlay
                cv2.putText(frame, "Pakistani Sign Language Detection", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, f"Model: YOLOv5 | Gestures: {len(self.labels)}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(frame, "Press 'q' to quit", (10, 450), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                
                # Show frame
                cv2.imshow('Sign to Speech - Pakistani Gestures', frame)
                
                # Check for quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            print("\n🛑 Detection stopped by user")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("👋 Camera released. Goodbye!")

def main():
    parser = argparse.ArgumentParser(description='Pakistani Sign Language to Speech Detection')
    parser.add_argument('--model', default='best.pt', help='Path to YOLOv5 model file')
    parser.add_argument('--labels', default='labels.json', help='Path to labels file')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🤟 PAKISTANI SIGN LANGUAGE TO SPEECH DETECTOR")
    print("=" * 60)
    print("🧠 AI: YOLOv5 + Computer Vision")
    print("🇵🇰 Languages: Urdu, Pashto, English")
    print("📹 Input: Real-time camera feed")
    print("🔊 Output: Text-to-speech")
    print("=" * 60)
    
    # Create detector instance
    detector = SignToSpeech(model_path=args.model, labels_path=args.labels)
    
    # Start detection
    detector.run_detection()

if __name__ == "__main__":
    main()