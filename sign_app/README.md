# 🤟 Pakistani Sign Language Translation App with 3D Character

Real-time Pakistani Sign Language detection and translation system using **YOLOv5**, **Google Speech API**, and **3D Animated Character**, supporting **Urdu**, **Pashto**, and **English** languages.

## 🎯 NEW FEATURES

### 🎭 3D Animated Character
- **Interactive 3D Character**: Animated avatar that demonstrates Pakistani sign language gestures
- **Real-time Animation**: Smooth character movements with gesture-specific hand positions
- **Visual Learning**: Perfect for visual learners who want to see how gestures are performed
- **Pakistani Cultural Elements**: Character designed with Pakistani cultural representation
- **Story Integration**: Character tells classic Pakistani stories with sign language demonstrations

### 🧠 Enhanced AI Features
- **132 Pakistani Gestures**: Comprehensive gesture dataset covering daily conversation needs
- **Google Speech API Integration**: Advanced speech recognition for Urdu, Pashto, and English
- **YOLOv5 Real-time Detection**: Fast and accurate hand gesture recognition
- **Bidirectional Translation**: Sign ↔ Speech ↔ Text with 3D demonstrations
- **Interactive Storytelling**: Learn sign language through classic tales like "انگور تو کھٹے ہیں"

## 🚀 Quick Start

### Prerequisites

```bash
# Install Python dependencies
pip install ultralytics torch torchvision opencv-python
pip install speechrecognition pyttsx3 pillow numpy pyaudio
pip install mediapipe pygame PyOpenGL python-dotenv
```

### 1. 🎭 Complete App with 3D Character

**The main application with all features:**

```bash
python sign_language_app.py
```

**Features:**
- 🎤 **Speech to Sign**: Speak in Urdu/Pashto/English → 3D character demonstrates gesture
- ✏️ **Text to Sign**: Type text → 3D character demonstrates gesture  
- 📋 **Browse Gestures**: View all 132 available Pakistani gestures
- 🎭 **Character Demo**: Watch character demonstrate various gestures
- 📚 **Pakistani Story Mode**: Learn through interactive storytelling (انگور تو کھٹے ہیں)

### 2. 📹 Real-time Sign Detection

```bash
python sign_to_speech.py
```

**What it does:**
- Opens camera feed
- Detects Pakistani hand gestures using YOLOv5
- Speaks the detected gesture in English/Urdu/Pashto
- Shows real-time bounding boxes and confidence scores

### 3. 🎤 Speech to Sign with Character

```bash
python speech_to_sign.py
```

**What it does:**
- Listens to microphone input
- Recognizes speech in Urdu/Pashto/English using Google Speech API
- Shows 3D animated character demonstrating the gesture
- Provides audio feedback

### 4. 🎭 3D Character Demo Only

```bash
python character_3d.py
```

**What it does:**
- Standalone 3D character demonstration
- Shows various Pakistani sign language gestures
- Interactive character animation

## 📊 Supported Gestures (132 Total)

### Numbers (10)
| Gesture | Urdu | Pashto | English |
|---------|------|--------|---------|
| ek | ایک | یو | One |
| do | دو | دوه | Two |
| teen | تین | درې | Three |
| chaar | چار | څلور | Four |
| paanch | پانچ | پنځه | Five |
| che | چھ | شپږ | Six |
| saat | سات | اووه | Seven |
| aath | آٹھ | اتے | Eight |
| nau | نو | نهه | Nine |
| das | دس | لس | Ten |

### Greetings & Social (10)
| Gesture | Urdu | Pashto | English |
|---------|------|--------|---------|
| salam | سلام | سلام ورور | Hello |
| shukriya | شکریہ | مننه | Thank you |
| khuda_hafiz | خدا حافظ | خدای پامان | Goodbye |
| haan | ہاں | هو | Yes |
| nahin | نہیں | نه | No |
| madad | مدد | مرسته | Help |
| dost | دوست | ملګری | Friend |
| mohabbat | محبت | مینه | Love |
| khushi | خوشی | خوښۍ | Happy |
| gham | غم | خپګان | Sad |

### Family (6)
| Gesture | Urdu | Pashto | English |
|---------|------|--------|---------|
| ammi | امی | مور | Mother |
| abbu | ابو | پلار | Father |
| bhai | بھائی | ورور | Brother |
| behn | بہن | خور | Sister |

### Daily Objects & Needs (20)
| Gesture | Urdu | Pashto | English |
|---------|------|--------|---------|
| paani | پانی | اوبه | Water |
| khana | کھانا | خواړه | Food |
| ghar | گھر | کور | Home |
| kitab | کتاب | کتاب | Book |
| qalam | قلم | قلم | Pen |
| school | اسکول | ښوونځی | School |
| hospital | ہسپتال | روغتون | Hospital |

### Actions (15)
| Gesture | Urdu | Pashto | English |
|---------|------|--------|---------|
| reading | پڑھنا | لوستل | Reading |
| writing | لکھنا | لیکل | Writing |
| eating | کھانا | خوړل | Eating |
| drinking | پینا | څښل | Drinking |
| listening | سننا | اورېدل | Listening |
| speaking | بولنا | ویل | Speaking |
| sleeping | سونا | ویده کېدل | Sleeping |
| walking | چلنا | ګرځېدل | Walking |
| running | دوڑنا | منډه | Running |

### Food & Fruits (15)
| Gesture | Urdu | Pashto | English |
|---------|------|--------|---------|
| aam | آم | آم | Mango |
| kela | کیلا | کیله | Banana |
| seb | سیب | مڼه | Apple |
| doodh | دودھ | شیدې | Milk |
| chai | چائے | چای | Tea |
| roti | روٹی | ډوډۍ | Bread |
| chawal | چاول | وریجې | Rice |

### Nature & Weather (15)
| Gesture | Urdu | Pashto | English |
|---------|------|--------|---------|
| suraj | سورج | لمر | Sun |
| chaand | چاند | سپوږمۍ | Moon |
| sitara | ستارہ | ستوری | Star |
| baarish | بارش | باران | Rain |
| hawa | ہوا | باد | Wind |
| phool | پھول | ګل | Flower |
| darakht | درخت | ونه | Tree |

### Technology & Modern Life (20)
| Gesture | Urdu | Pashto | English |
|---------|------|--------|---------|
| phone | فون | ټیلیفون | Phone |
| mobile | موبائل | ګرځنده | Mobile |
| computer | کمپیوٹر | کمپیوټر | Computer |
| tv | ٹی وی | تلویزون | Television |
| camera | کیمرا | کامره | Camera |

### Transportation (10)
| Gesture | Urdu | Pashto | English |
|---------|------|--------|---------|
| gaadi | گاڑی | موټر | Car |
| bus | بس | بس | Bus |
| train | ریل گاڑی | اورګاډی | Train |

### Others (21)
Including emotions, adjectives, time, places, and more daily conversation words.

## 🎭 3D Character Features

### Visual Design
- **Realistic Human Character**: Proportioned body with head, torso, arms, and legs
- **Pakistani Elements**: Cultural representation with appropriate styling
- **Smooth Animation**: Fluid movement between gestures with easing functions
- **Hand Detail**: Specific finger positions for each gesture type

### Animation Types
- **Open Hand**: For greetings like "salam" (hello)
- **Number Gestures**: Finger counting from 1-5 and beyond
- **Pointing**: For directions and references
- **Fist**: For emphasis gestures
- **Specialized**: Unique poses for context-specific words

### Interactive Features
- **Real-time Response**: Character animates immediately when gesture is detected
- **Educational Display**: Shows Urdu, Pashto, and English translations
- **Pakistani Flag**: Visual elements representing Pakistani culture
- **Progress Animation**: Smooth transitions between poses

## 🛠️ How It Works

### 1. Speech Recognition Pipeline  
```
Microphone Input → Google Speech API → Text Processing → Gesture Matching → 3D Character Animation
```

### 2. Text Processing Pipeline
```
Text Input → Language Detection → Gesture Database Lookup → 3D Character Animation
```

### 3. Sign Detection Pipeline (YOLOv5)
```
Camera Input → YOLOv5 Processing → Gesture Classification → Text-to-Speech Output
```

### 4. 3D Character Animation Pipeline
```
Gesture Name → Pose Lookup → Hand Position Calculation → Smooth Animation → Visual Display
```

## 🎓 Training Your Own YOLOv5 Model

### Step 1: Prepare Dataset

Create dataset structure:
```bash
pakistani_sign_dataset/
├── train/
│   ├── images/        # Training images
│   └── labels/        # YOLO format labels
└── val/
    ├── images/        # Validation images  
    └── labels/        # YOLO format labels
```

### Step 2: Use Google Colab Training Script

```python
# Upload train_yolov5_colab.py to Google Colab
# Follow the training instructions in the script
python train_yolov5_colab.py
```

### Step 3: Download Trained Model

After training completes, download `best.pt` and replace the existing model.

## 🔧 Configuration

### Google Speech API Setup

1. **API Key**: The app uses Google Speech API key: `AIzaSyBRj3kHAgCg6B_rJTWhlMg8zsNHSTy6vnM`
2. **Languages Supported**: English (`en`), Urdu (`ur`), Farsi/Pashto (`fa`)
3. **Fallback**: Free Google Speech Recognition if API key fails

### Camera Settings
```python
# In sign_to_speech.py
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)
```

### YOLOv5 Detection Thresholds
```python
# In sign_to_speech.py
model.conf = 0.6  # Confidence threshold
model.iou = 0.4   # IoU threshold
```

### 3D Character Settings
```python
# In character_3d.py
character = SignLanguageCharacter(width=900, height=700)  # Window size
animation_speed = 2.0  # Animation speed
```

## 📱 Usage Examples

### Example 1: Speech to 3D Character
```bash
$ python sign_language_app.py
# Choose option 1
🎤 Listening for speech...
🔤 Recognized (Urdu): سلام
🎭 Starting 3D character animation...
🤟 GESTURE: SALAM
🇵🇰 Urdu: سلام | 🇦🇫 Pashto: سلام ورور | 🏴󠁧󠁢󠁥󠁮󠁧󠁿 English: Hello
```

### Example 2: Text to 3D Character
```bash
$ python sign_language_app.py
# Choose option 2
📝 Enter text: thank you
✅ Found gesture: shukriya
🎭 Starting 3D character animation...
🤟 GESTURE: SHUKRIYA
🇵🇰 Urdu: شکریہ | 🇦🇫 Pashto: مننه | 🏴󠁧󠁢󠁥󠁮󠁧󠁿 English: Thank you
```

### Example 3: Real-time Camera Detection
```bash
$ python sign_to_speech.py
📹 Starting camera feed...
🗣️ Speaking: Detected gesture: Hello. In Urdu: سلام. In Pashto: سلام ورور
```

## 🎯 Performance Tips

### For Better Gesture Detection:
- ✅ Use good lighting conditions
- ✅ Keep hand clearly visible in camera
- ✅ Make distinct gesture movements
- ✅ Hold gesture for 1-2 seconds

### For Better Speech Recognition:
- ✅ Speak clearly and slowly
- ✅ Use quiet environment
- ✅ Speak close to microphone
- ✅ Try different languages if recognition fails

### For Better 3D Character Performance:
- ✅ Close unnecessary applications
- ✅ Ensure graphics drivers are updated
- ✅ Use lower resolution if performance is slow

## 🐛 Troubleshooting

### Common Issues:

**"3D Character window not opening"**
```bash
# Install display dependencies
sudo apt-get install python3-tk
# Or try software rendering
export PYGAME_HIDE_SUPPORT_PROMPT=1
```

**"Speech recognition failed"**
```bash
# Check microphone permissions
# Test with different speech API key
# Use text mode instead: option 2
```

**"YOLOv5 model not found"** 
```bash
# Download YOLOv5 weights
cd /app/sign_app
wget https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt
mv yolov5s.pt best.pt
```

**"Gesture images not displaying"**
```bash
# Images are auto-generated
# Check gesture_images/ folder exists
mkdir -p gesture_images/
```

## 🔄 Updates & Improvements

### Version History:
- **v3.0**: Added 3D animated character with 132 gestures
- **v2.0**: Improved speech recognition with Google API
- **v1.0**: Basic YOLOv5 detection + TTS

### Planned Features:
- [ ] More gesture classes (200+ gestures)
- [ ] Better 3D character animations with facial expressions
- [ ] Mobile app version
- [ ] Real-time accuracy improvements
- [ ] Gesture-to-gesture translation
- [ ] Voice training for better Urdu/Pashto recognition

## 📄 License

MIT License - Feel free to use and modify for your projects!

## 🤝 Contributing

1. Fork the repository
2. Add new Pakistani gestures to dataset
3. Improve 3D character animations
4. Create pull request

## 📞 Support

- 📧 **Issues**: Create an issue on GitHub
- 📖 **Documentation**: See code comments and this README
- 🎥 **Demo**: Run the character demo mode

## 🙏 Acknowledgments

- **YOLOv5** by Ultralytics for object detection
- **Pakistani Deaf Community** for gesture references
- **Google Speech Recognition** for voice processing
- **Pygame** for 3D character animation
- **PyTorch** for deep learning framework
- **OpenCV** for computer vision

---

**🇵🇰 Made with ❤️ for Pakistani Sign Language Community**

*Bridging communication barriers through AI, 3D animation, and computer vision*

## 🎮 Quick Demo Commands

```bash
# Complete app with all features
python sign_language_app.py

# Camera-based gesture detection
python sign_to_speech.py

# Speech recognition with 3D character
python speech_to_sign.py

# 3D character demo only
python character_3d.py
```

**🎭 Experience the magic of 3D sign language learning! 🤟**