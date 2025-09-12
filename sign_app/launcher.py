#!/usr/bin/env python3
"""
Pakistani Sign Language App Launcher
Simple launcher script for the complete application
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header():
    """Print application header"""
    print("=" * 80)
    print("🇵🇰 PAKISTANI SIGN LANGUAGE TRANSLATION APP WITH 3D CHARACTER")
    print("=" * 80)
    print("🤟 132 Pakistani Sign Language Gestures")
    print("🎭 Interactive 3D Animated Character")
    print("🧠 AI-Powered: YOLOv5 + Google Speech API")
    print("🌐 Languages: Urdu, Pashto, English")
    print("=" * 80)

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = {
        'pygame': 'pygame',
        'cv2': 'opencv-python',  
        'torch': 'torch',
        'ultralytics': 'ultralytics',
        'speech_recognition': 'speechrecognition',
        'pyttsx3': 'pyttsx3',
        'numpy': 'numpy',
        'PIL': 'pillow',
        'mediapipe': 'mediapipe'
    }
    
    missing_packages = []
    
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n🔧 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def check_files():
    """Check if required files exist"""
    required_files = [
        'sign_language_app.py',
        'character_3d.py', 
        'sign_to_speech.py',
        'speech_to_sign.py',
        'pakistani_story.py',
        'labels.json',
        'best.pt',
        '.env'
    ]
    
    missing_files = []
    current_dir = Path('.')
    
    for file_name in required_files:
        if not (current_dir / file_name).exists():
            missing_files.append(file_name)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_name in missing_files:
            print(f"   - {file_name}")
        
        if 'best.pt' in missing_files:
            print("\n🔧 Download YOLOv5 model:")
            print("   wget https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt")
            print("   mv yolov5s.pt best.pt")
        
        if '.env' in missing_files:
            print("\n🔧 Create .env file with Google Speech API key:")
            print("   echo 'GOOGLE_SPEECH_API_KEY=AIzaSyBRj3kHAgCg6B_rJTWhlMg8zsNHSTy6vnM' > .env")
        
        return False
    
    print("✅ All required files are present!")
    return True

def main():
    """Main launcher function"""
    print_header()
    
    print("\n🔍 Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        return
    print(f"✅ Python {sys.version.split()[0]} is installed")
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check files
    if not check_files():
        return
    
    print("\n🚀 System check completed successfully!")
    print("\n🎯 Choose how to launch the application:")
    print()
    print("1. 🎭 Complete App with 3D Character (Recommended)")
    print("   - Speech to Sign with 3D character animation")
    print("   - Text to Sign with 3D character animation") 
    print("   - Browse all 132 Pakistani gestures")
    print("   - Interactive character demo")
    print()
    print("2. 📹 Real-time Sign Detection (Camera required)")
    print("   - Detects Pakistani gestures from camera")
    print("   - Converts gestures to speech output")
    print("   - Real-time YOLOv5 processing")
    print()
    print("3. 🎤 Speech to Sign Only (Microphone required)")
    print("   - Speech recognition in Urdu/Pashto/English")
    print("   - 3D character demonstrates gestures")
    print("   - Google Speech API integration")
    print()
    print("4. 🎮 3D Character Demo Only")
    print("   - Standalone 3D character animation")
    print("   - Shows various Pakistani gestures")
    print("   - No microphone or camera needed")
    print()
    print("5. 📚 Pakistani Story Mode")
    print("   - Interactive storytelling with 3D character")
    print("   - Classic tale: 'The Sour Grapes' (انگور تو کھٹے ہیں)")
    print("   - Learn sign language through stories")
    print()
    print("6. ❓ System Information")
    print("7. ❌ Exit")
    
    while True:
        try:
            choice = input("\n👉 Enter your choice (1-7): ").strip()
            
            if choice == '1':
                print("\n🎭 Launching complete app with 3D character...")
                subprocess.run([sys.executable, 'sign_language_app.py'])
                break
            elif choice == '2':
                print("\n📹 Launching real-time sign detection...")
                subprocess.run([sys.executable, 'sign_to_speech.py'])
                break
            elif choice == '3':
                print("\n🎤 Launching speech to sign with 3D character...")
                subprocess.run([sys.executable, 'speech_to_sign.py'])
                break
            elif choice == '4':
                print("\n🎮 Launching 3D character demo...")
                subprocess.run([sys.executable, 'character_3d.py'])
                break
            elif choice == '5':
                print("\n📚 Launching Pakistani story mode...")
                subprocess.run([sys.executable, 'pakistani_story.py'])
                break
            elif choice == '6':
                show_system_info()
            elif choice == '7':
                print("\n👋 Thank you for using Pakistani Sign Language App!")
                print("🇵🇰 Goodbye! خدا حافظ! خدای پامان!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-7.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Application terminated by user")
            break

def show_system_info():
    """Show detailed system information"""
    print("\n" + "="*60)
    print("📊 SYSTEM INFORMATION")
    print("="*60)
    
    # Python info
    print(f"🐍 Python Version: {sys.version.split()[0]}")
    print(f"📁 Current Directory: {os.getcwd()}")
    
    # File info
    print(f"\n📂 Project Files:")
    project_files = [
        'sign_language_app.py', 'character_3d.py', 'sign_to_speech.py',
        'speech_to_sign.py', 'pakistani_story.py', 'labels.json', 'best.pt', '.env'
    ]
    
    for file_name in project_files:
        if Path(file_name).exists():
            file_size = Path(file_name).stat().st_size
            print(f"   ✅ {file_name:<20} ({file_size:,} bytes)")
        else:
            print(f"   ❌ {file_name:<20} (missing)")
    
    # Labels info
    try:
        import json
        with open('labels.json', 'r', encoding='utf-8') as f:
            labels = json.load(f)
        print(f"\n🤟 Gesture Labels: {len(labels)} Pakistani gestures loaded")
    except:
        print(f"\n❌ Could not load gesture labels")
    
    # Dependencies info
    print(f"\n📦 Key Dependencies:")
    deps = {
        'pygame': 'pygame',
        'torch': 'torch', 
        'ultralytics': 'ultralytics',
        'cv2': 'opencv-python',
        'speech_recognition': 'speechrecognition'
    }
    
    for import_name, package_name in deps.items():
        try:
            module = __import__(import_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"   ✅ {package_name}: {version}")
        except ImportError:
            print(f"   ❌ {package_name}: not installed")
    
    # Environment info
    print(f"\n🌍 Environment:")
    
    # Load .env file if it exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
        google_key = os.getenv('GOOGLE_SPEECH_API_KEY')
        if google_key:
            print(f"   ✅ Google Speech API Key: {google_key[:10]}...{google_key[-5:]}")
        else:
            print(f"   ⚠️ Google Speech API Key: not found in environment")
    except ImportError:
        print(f"   ⚠️ python-dotenv not available, manually check .env file")
    except Exception as e:
        print(f"   ⚠️ Environment check failed: {e}")
    
    print("="*60)

if __name__ == "__main__":
    main()