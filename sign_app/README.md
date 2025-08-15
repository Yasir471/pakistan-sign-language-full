# 🤟 Pakistani Sign Language Detection with YOLOv5

Real-time Pakistani Sign Language detection and translation system using YOLOv5, supporting **Urdu**, **Pashto**, and **English** languages.

## 🎯 Features

- 🧠 **YOLOv5-powered** real-time hand gesture detection
- 🇵🇰 **Pakistani Sign Language** support (20+ gestures)
- 🔄 **Bidirectional conversion**: Sign ↔ Speech
- 🎤 **Speech recognition** in Urdu, Pashto, and English  
- 🔊 **Text-to-speech** output for detected gestures
- 📹 **Live camera feed** processing
- 🤚 **Real hand tracking** and gesture classification

## 📁 Project Structure

```
sign_app/
├── best.pt                 # Trained YOLOv5 model
├── sign_to_speech.py      # Real-time gesture → speech
├── speech_to_sign.py      # Speech → gesture display
├── labels.json            # Gesture labels (Urdu/Pashto/English)
├── train_yolov5_colab.py  # Training script for Google Colab
├── gesture_images/        # Sample gesture images
│   ├── salam.jpg
│   ├── shukriya.jpg
│   └── ...
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites

```bash
# Install Python dependencies
pip install opencv-python torch torchvision ultralytics
pip install speechrecognition pyttsx3 pillow numpy
pip install pyaudio  # For microphone input
```

### 1. 📹 Sign to Speech Detection

Detects hand gestures from camera and converts to speech:

```bash
python sign_to_speech.py
```

**What it does:**
- Opens camera feed
- Detects Pakistani hand gestures using YOLOv5
- Speaks the detected gesture in English/Urdu/Pashto
- Shows real-time bounding boxes and confidence scores

### 2. 🎤 Speech to Sign Conversion  

Converts spoken words to gesture demonstrations:

```bash
python speech_to_sign.py
```

**What it does:**
- Listens to microphone input
- Recognizes speech in Urdu/Pashto/English
- Shows corresponding hand gesture image
- Displays gesture information in all three languages

### 3. 🏋️ Training Your Own Model

Use Google Colab to train custom YOLOv5 model:

1. Upload `train_yolov5_colab.py` to Google Colab
2. Add your gesture images to dataset folders
3. Run training script
4. Download trained `best.pt` model

## 📊 Supported Gestures

| Gesture | Urdu | Pashto | English |
|---------|------|--------|---------|
| salam | سلام | سلام ورور | Hello |
| shukriya | شکریہ | مننه | Thank you |
| khuda_hafiz | خدا حافظ | خدای پامان | Goodbye |
| paani | پانی | اوبه | Water |
| khana | کھانا | خواړه | Food |
| madad | مدد | مرسته | Help |
| ek | ایک | یو | One |
| do | دو | دوه | Two |
| teen | تین | درې | Three |
| ghar | گھر | کور | Home |
| ... | ... | ... | ... |

*20+ gestures supported (see `labels.json` for complete list)*

## 🛠️ How It Works

### Sign Detection Pipeline
1. **Camera Input** → Capture live video feed
2. **YOLOv5 Processing** → Detect hand gestures in real-time
3. **Classification** → Identify specific Pakistani gestures
4. **Translation** → Convert to Urdu/Pashto/English text
5. **Speech Output** → Text-to-speech announcement

### Speech Recognition Pipeline  
1. **Microphone Input** → Capture spoken words
2. **Speech Recognition** → Convert speech to text (multi-language)
3. **Gesture Matching** → Find corresponding hand gesture
4. **Visual Display** → Show gesture image and information
5. **Audio Feedback** → Confirm gesture found

## 🎓 Training Your Own Model

### Step 1: Prepare Dataset

```bash
# Create dataset structure
pakistani_sign_dataset/
├── train/
│   ├── images/        # Training images
│   └── labels/        # YOLO format labels
└── val/
    ├── images/        # Validation images  
    └── labels/        # YOLO format labels
```

### Step 2: Label Format

YOLO format labels (one `.txt` file per image):
```
class_id x_center y_center width height
0 0.5 0.3 0.4 0.6
```

### Step 3: Train in Google Colab

```python
# Upload train_yolov5_colab.py to Colab
# Run training script
python train_yolov5_colab.py
```

### Step 4: Download Model

After training, download `best.pt` and replace the existing model.

## 🔧 Configuration

### Camera Settings
```python
# In sign_to_speech.py
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)
```

### Detection Thresholds
```python
# In sign_to_speech.py
self.model.conf = 0.6  # Confidence threshold
self.model.iou = 0.4   # IoU threshold
```

### Speech Recognition Languages
```python
# In speech_to_sign.py
# Supported languages: 'en', 'ur', 'auto'
text = recognizer.recognize_google(audio, language='ur')
```

## 📱 Usage Examples

### Example 1: Real-time Detection
```bash
$ python sign_to_speech.py
🚀 Loading YOLOv5 model for Pakistani Sign Language...
✅ YOLOv5 model loaded successfully!
✅ Loaded 20 gesture labels
📹 Starting camera feed...
🗣️ Speaking: Detected gesture: Hello. In Urdu: سلام. In Pashto: سلام ورور
```

### Example 2: Speech Recognition
```bash
$ python speech_to_sign.py  
🎤 Listening for speech...
🔤 Recognized (Urdu): سلام
✅ Found partial match: 'سلام' in 'سلام'
🤟 GESTURE: SALAM
🏴󠁧󠁢󠁥󠁮󠁧󠁿 English: Hello
🇵🇰 Urdu: سلام
🇦🇫 Pashto: سلام ورور
```

## 🎯 Performance Tips

### For Better Detection:
- ✅ Use good lighting conditions
- ✅ Keep hand clearly visible in camera
- ✅ Make distinct gesture movements
- ✅ Hold gesture for 1-2 seconds

### For Better Speech Recognition:
- ✅ Speak clearly and slowly
- ✅ Use quiet environment
- ✅ Speak close to microphone
- ✅ Try different languages if recognition fails

## 🐛 Troubleshooting

### Common Issues:

**"Model not found"**
```bash
# Download YOLOv5 weights
wget https://github.com/ultralytics/yolov5/releases/download/v6.0/yolov5s.pt
# Rename to best.pt or train your own model
```

**"Camera not found"** 
```bash
# Check camera permissions
# Try different camera index: VideoCapture(1)
```

**"Speech recognition failed"**
```bash
# Install pyaudio properly
pip uninstall pyaudio
pip install pyaudio
# Or use conda: conda install pyaudio
```

**"TTS not working"**
```bash
# Install espeak (Linux)
sudo apt-get install espeak espeak-data libespeak1 libespeak-dev

# Install SAPI (Windows) - usually pre-installed
```

## 🔄 Updates & Improvements

### Version History:
- **v1.0**: Basic YOLOv5 detection + TTS
- **v1.1**: Added speech recognition
- **v1.2**: Pakistani language support
- **v1.3**: Improved gesture dataset

### Future Enhancements:
- [ ] More gesture classes (50+ gestures)
- [ ] Better Urdu/Pashto speech recognition
- [ ] Mobile app version  
- [ ] Real-time translation accuracy improvements
- [ ] Gesture-to-gesture translation

## 📄 License

MIT License - Feel free to use and modify for your projects!

## 🤝 Contributing

1. Fork the repository
2. Add new Pakistani gestures to dataset
3. Improve speech recognition accuracy  
4. Create pull request

## 📞 Support

- 📧 Email: Create an issue on GitHub
- 📖 Documentation: See code comments
- 🎥 Demo videos: Record your own using the scripts

## 🙏 Acknowledgments

- **YOLOv5** by Ultralytics for object detection
- **Pakistani Deaf Community** for gesture references
- **Google Speech Recognition** for voice processing
- **OpenCV** for computer vision
- **PyTorch** for deep learning framework

---

**🇵🇰 Made with ❤️ for Pakistani Sign Language Community**

*Bridging communication barriers through AI and computer vision*