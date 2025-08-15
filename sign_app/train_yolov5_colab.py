#!/usr/bin/env python3
"""
YOLOv5 Training Script for Pakistani Sign Language Detection
Use this script in Google Colab to train your custom model

Instructions:
1. Upload this script to Google Colab
2. Create your dataset with gesture images
3. Run the training process
4. Download the trained model (best.pt)
"""

# GOOGLE COLAB SETUP
"""
Run this in Google Colab first cell:

# Install dependencies
!pip install ultralytics roboflow supervision

# Clone YOLOv5 
!git clone https://github.com/ultralytics/yolov5
%cd yolov5
!pip install -r requirements.txt

"""

import os
import yaml
import zipfile
import requests
from pathlib import Path
import json
import shutil

class PakistaniSignLanguageTrainer:
    def __init__(self):
        """Initialize trainer for Pakistani Sign Language gestures"""
        self.dataset_path = "pakistani_sign_dataset"
        self.classes = [
            'salam', 'shukriya', 'khuda_hafiz', 'paani', 'khana', 
            'madad', 'ek', 'do', 'teen', 'ghar', 'kitab', 'qalam',
            'ammi', 'abbu', 'bhai', 'behn', 'chaar', 'paanch',
            'school', 'doctor'
        ]
        
        # Create dataset structure
        self.setup_dataset_structure()
    
    def setup_dataset_structure(self):
        """Create dataset folder structure"""
        print("📁 Setting up dataset structure...")
        
        # Create main dataset folder
        os.makedirs(self.dataset_path, exist_ok=True)
        
        # Create train/val folders
        for split in ['train', 'val']:
            for folder in ['images', 'labels']:
                path = Path(self.dataset_path) / split / folder
                path.mkdir(parents=True, exist_ok=True)
        
        print("✅ Dataset structure created")
    
    def create_sample_dataset(self):
        """Create sample dataset for demonstration"""
        print("📷 Creating sample dataset...")
        
        # This is where you'd add your real gesture images
        # For now, we'll create placeholder structure
        
        sample_images = {
            'salam': ['salam_1.jpg', 'salam_2.jpg', 'salam_3.jpg'],
            'shukriya': ['shukriya_1.jpg', 'shukriya_2.jpg', 'shukriya_3.jpg'],
            'khuda_hafiz': ['khuda_hafiz_1.jpg', 'khuda_hafiz_2.jpg'],
            'paani': ['paani_1.jpg', 'paani_2.jpg'],
            'khana': ['khana_1.jpg', 'khana_2.jpg'],
        }
        
        print("💡 IMPORTANT: Add your real gesture images to:")
        print(f"   📂 {self.dataset_path}/train/images/")
        print(f"   📂 {self.dataset_path}/val/images/")
        print("💡 Add corresponding YOLO format labels to:")
        print(f"   📂 {self.dataset_path}/train/labels/")
        print(f"   📂 {self.dataset_path}/val/labels/")
        
    def create_yaml_config(self):
        """Create dataset configuration for YOLOv5"""
        print("⚙️ Creating dataset configuration...")
        
        config = {
            'path': os.path.abspath(self.dataset_path),
            'train': 'train/images',
            'val': 'val/images',
            'nc': len(self.classes),
            'names': self.classes
        }
        
        config_path = f"{self.dataset_path}/dataset.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        print(f"✅ Dataset config saved: {config_path}")
        return config_path
    
    def train_model(self, epochs=100, img_size=640, batch_size=16):
        """Train YOLOv5 model"""
        print("🚀 Starting YOLOv5 training...")
        
        config_path = self.create_yaml_config()
        
        # Training command
        train_cmd = f"""
        python train.py \\
            --data {config_path} \\
            --weights yolov5s.pt \\
            --epochs {epochs} \\
            --img {img_size} \\
            --batch-size {batch_size} \\
            --name pakistani_sign_language \\
            --patience 10 \\
            --save-period 10 \\
            --exist-ok
        """
        
        print("💻 Run this command in Google Colab:")
        print(train_cmd)
        
        # In Colab, you would run:
        # os.system(train_cmd)
        
        print("\n📊 Monitor training progress:")
        print("- Tensorboard: runs/train/pakistani_sign_language/")
        print("- Best model: runs/train/pakistani_sign_language/weights/best.pt")
        print("- Last model: runs/train/pakistani_sign_language/weights/last.pt")
    
    def create_labels_json(self):
        """Create labels.json file for the app"""
        labels = {}
        for i, class_name in enumerate(self.classes):
            # Map class names to Pakistani language equivalents
            mappings = {
                'salam': {"urdu": "سلام", "pashto": "سلام ورور", "english": "Hello"},
                'shukriya': {"urdu": "شکریہ", "pashto": "مننه", "english": "Thank you"},
                'khuda_hafiz': {"urdu": "خدا حافظ", "pashto": "خدای پامان", "english": "Goodbye"},
                'paani': {"urdu": "پانی", "pashto": "اوبه", "english": "Water"},
                'khana': {"urdu": "کھانا", "pashto": "خواړه", "english": "Food"},
                'madad': {"urdu": "مدد", "pashto": "مرسته", "english": "Help"},
                'ek': {"urdu": "ایک", "pashto": "یو", "english": "One"},
                'do': {"urdu": "دو", "pashto": "دوه", "english": "Two"},
                'teen': {"urdu": "تین", "pashto": "درې", "english": "Three"},
                'ghar': {"urdu": "گھر", "pashto": "کور", "english": "Home"},
                'kitab': {"urdu": "کتاب", "pashto": "کتاب", "english": "Book"},
                'qalam': {"urdu": "قلم", "pashto": "قلم", "english": "Pen"},
                'ammi': {"urdu": "امی", "pashto": "مور", "english": "Mother"},
                'abbu': {"urdu": "ابو", "pashto": "پلار", "english": "Father"},
                'bhai': {"urdu": "بھائی", "pashto": "ورور", "english": "Brother"},
                'behn': {"urdu": "بہن", "pashto": "خور", "english": "Sister"},
                'chaar': {"urdu": "چار", "pashto": "څلور", "english": "Four"},
                'paanch': {"urdu": "پانچ", "pashto": "پنځه", "english": "Five"},
                'school': {"urdu": "اسکول", "pashto": "ښوونځی", "english": "School"},
                'doctor': {"urdu": "ڈاکٹر", "pashto": "ډاکټر", "english": "Doctor"}
            }
            
            if class_name in mappings:
                labels[str(i)] = {
                    "name": class_name,
                    **mappings[class_name]
                }
            else:
                labels[str(i)] = {
                    "name": class_name,
                    "urdu": class_name,
                    "pashto": class_name,
                    "english": class_name.replace('_', ' ').title()
                }
        
        with open('labels.json', 'w', encoding='utf-8') as f:
            json.dump(labels, f, ensure_ascii=False, indent=2)
        
        print("✅ labels.json created successfully")

def main():
    """Main training pipeline for Google Colab"""
    print("=" * 60)
    print("🇵🇰 PAKISTANI SIGN LANGUAGE YOLOv5 TRAINER")
    print("=" * 60)
    print("🏋️ Use this script in Google Colab for training")
    print("📷 Add your gesture images to the dataset folder")
    print("🤖 Train custom YOLOv5 model for Pakistani gestures")
    print("=" * 60)
    
    trainer = PakistaniSignLanguageTrainer()
    
    # Setup dataset
    trainer.create_sample_dataset()
    
    # Create labels
    trainer.create_labels_json()
    
    # Start training (modify epochs as needed)
    trainer.train_model(epochs=50, img_size=640, batch_size=8)
    
    print("\n🎯 NEXT STEPS:")
    print("1. 📷 Add your Pakistani gesture images to dataset folders")
    print("2. 🏷️ Create YOLO format labels for each image")
    print("3. ▶️ Run the training command in Google Colab")
    print("4. 📥 Download best.pt model when training completes")
    print("5. 🚀 Use best.pt with sign_to_speech.py for detection!")

if __name__ == "__main__":
    # For Google Colab usage
    if 'google.colab' in str(get_ipython()):
        print("🔬 Running in Google Colab environment")
        
        # Install dependencies
        !pip install ultralytics pyyaml
        
        # Clone YOLOv5 if not exists
        if not os.path.exists('yolov5'):
            !git clone https://github.com/ultralytics/yolov5
            %cd yolov5
            !pip install -r requirements.txt
        
        main()
    else:
        print("💻 Run this script in Google Colab for best results")
        main()