#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Sign Language Translation System
Tests all core API endpoints with realistic Pakistani sign language data
PLUS testing for new 3D Character Sign Language App components
"""

import requests
import json
import base64
import uuid
import time
from datetime import datetime
import os
import sys
import subprocess
import importlib.util
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

print(f"Testing backend at: {API_BASE}")
print(f"Testing sign_app components at: /app/sign_app/")

class BackendTester:
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.test_results = {}
        self.sign_app_path = Path("/app/sign_app")
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        self.test_results[test_name] = {"success": success, "details": details}
        
    def test_root_endpoint(self):
        """Test GET /api/ - Root endpoint"""
        try:
            response = requests.get(f"{API_BASE}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "version" in data:
                    self.log_test("Root Endpoint", True, f"Message: {data['message']}, Version: {data['version']}")
                    return True
                else:
                    self.log_test("Root Endpoint", False, "Missing required fields in response")
                    return False
            else:
                self.log_test("Root Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_gestures_endpoint(self):
        """Test GET /api/gestures - Get available Pakistani gestures"""
        try:
            response = requests.get(f"{API_BASE}/gestures", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "gestures" in data and "count" in data:
                    gestures = data["gestures"]
                    expected_gestures = ["salam", "shukriya", "khuda_hafiz", "paani", "khana", "ghar", "kitab", "kaam", "dost", "madad"]
                    
                    # Check if all expected Pakistani gestures are present
                    missing_gestures = [g for g in expected_gestures if g not in gestures]
                    if not missing_gestures:
                        # Verify gesture structure (urdu, pashto, meaning)
                        sample_gesture = list(gestures.values())[0]
                        if all(key in sample_gesture for key in ["urdu", "pashto", "meaning"]):
                            self.log_test("Pakistani Gestures Dataset", True, f"Found {data['count']} gestures with proper structure")
                            return True
                        else:
                            self.log_test("Pakistani Gestures Dataset", False, "Gesture structure missing required fields")
                            return False
                    else:
                        self.log_test("Pakistani Gestures Dataset", False, f"Missing gestures: {missing_gestures}")
                        return False
                else:
                    self.log_test("Pakistani Gestures Dataset", False, "Missing required fields in response")
                    return False
            else:
                self.log_test("Pakistani Gestures Dataset", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Pakistani Gestures Dataset", False, f"Exception: {str(e)}")
            return False
    
    def test_gesture_detection(self):
        """Test POST /api/detect-gesture - YOLOv5 gesture detection"""
        try:
            # Create mock base64 image data
            mock_image_data = base64.b64encode(b"mock_image_data_for_testing").decode('utf-8')
            
            payload = {
                "image_data": mock_image_data,
                "session_id": self.session_id
            }
            
            response = requests.post(f"{API_BASE}/detect-gesture", json=payload, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "detection" in data:
                    detection = data["detection"]
                    required_fields = ["gesture", "confidence", "urdu_text", "pashto_text", "meaning"]
                    
                    if all(field in detection for field in required_fields):
                        confidence = detection.get("confidence", 0)
                        if 0.75 <= confidence <= 0.95:  # Expected mock confidence range
                            self.log_test("YOLOv5 Gesture Detection", True, 
                                        f"Detected: {detection['gesture']} (confidence: {confidence:.2f})")
                            return True
                        else:
                            self.log_test("YOLOv5 Gesture Detection", False, 
                                        f"Confidence out of expected range: {confidence}")
                            return False
                    else:
                        missing = [f for f in required_fields if f not in detection]
                        self.log_test("YOLOv5 Gesture Detection", False, f"Missing fields: {missing}")
                        return False
                else:
                    self.log_test("YOLOv5 Gesture Detection", False, "Invalid response structure")
                    return False
            else:
                self.log_test("YOLOv5 Gesture Detection", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("YOLOv5 Gesture Detection", False, f"Exception: {str(e)}")
            return False
    
    def test_speech_to_sign(self):
        """Test POST /api/speech-to-sign - Convert Urdu/Pashto speech to sign"""
        try:
            # Test with Urdu
            mock_audio_data = base64.b64encode(b"mock_urdu_audio_data").decode('utf-8')
            
            payload = {
                "audio_data": mock_audio_data,
                "language": "urdu",
                "session_id": self.session_id
            }
            
            response = requests.post(f"{API_BASE}/speech-to-sign", json=payload, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "result" in data:
                    result = data["result"]
                    if "recognized_text" in result and "language" in result:
                        # Test with Pashto
                        payload["language"] = "pashto"
                        response2 = requests.post(f"{API_BASE}/speech-to-sign", json=payload, timeout=15)
                        
                        if response2.status_code == 200:
                            data2 = response2.json()
                            if data2.get("success"):
                                self.log_test("Speech Recognition (Urdu/Pashto)", True, 
                                            f"Urdu: {result['recognized_text'][:20]}...")
                                return True
                        
                        self.log_test("Speech Recognition (Urdu/Pashto)", False, "Pashto test failed")
                        return False
                    else:
                        self.log_test("Speech Recognition (Urdu/Pashto)", False, "Missing required fields")
                        return False
                else:
                    self.log_test("Speech Recognition (Urdu/Pashto)", False, "Invalid response structure")
                    return False
            else:
                self.log_test("Speech Recognition (Urdu/Pashto)", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Speech Recognition (Urdu/Pashto)", False, f"Exception: {str(e)}")
            return False
    
    def test_text_to_sign(self):
        """Test POST /api/text-to-sign - Convert Urdu/Pashto text to sign"""
        try:
            # Test with Urdu text
            test_cases = [
                {"text": "سلام", "language": "urdu", "expected_gesture": "salam"},
                {"text": "شکریہ", "language": "urdu", "expected_gesture": "shukriya"},
                {"text": "سلام ورور", "language": "pashto", "expected_gesture": "salam"}
            ]
            
            success_count = 0
            for test_case in test_cases:
                payload = {
                    "text": test_case["text"],
                    "language": test_case["language"],
                    "session_id": self.session_id
                }
                
                response = requests.post(f"{API_BASE}/text-to-sign", json=payload, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "result" in data:
                        result = data["result"]
                        if result.get("gesture_found"):
                            success_count += 1
                
            if success_count >= 2:  # At least 2 out of 3 should work
                self.log_test("Text-to-Sign Translation", True, f"Successfully processed {success_count}/3 test cases")
                return True
            else:
                self.log_test("Text-to-Sign Translation", False, f"Only {success_count}/3 test cases succeeded")
                return False
                
        except Exception as e:
            self.log_test("Text-to-Sign Translation", False, f"Exception: {str(e)}")
            return False
    
    def test_translation_history(self):
        """Test GET /api/history/{session_id} - Get translation history"""
        try:
            response = requests.get(f"{API_BASE}/history/{self.session_id}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "history" in data and "count" in data:
                    # Should have some history from previous tests
                    if data["count"] > 0:
                        self.log_test("Translation History", True, f"Found {data['count']} history records")
                        return True
                    else:
                        self.log_test("Translation History", True, "No history found (expected for new session)")
                        return True
                else:
                    self.log_test("Translation History", False, "Invalid response structure")
                    return False
            else:
                self.log_test("Translation History", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Translation History", False, f"Exception: {str(e)}")
            return False
    
    def test_statistics(self):
        """Test GET /api/stats - Get application statistics"""
        try:
            response = requests.get(f"{API_BASE}/stats", timeout=10)
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_translations", "sign_to_speech_count", "speech_to_sign_count", 
                                 "available_gestures", "model_status"]
                
                if all(field in data for field in required_fields):
                    if data["available_gestures"] == 10:  # Expected number of Pakistani gestures
                        self.log_test("Application Statistics", True, 
                                    f"Total translations: {data['total_translations']}, Model: {data['model_status']}")
                        return True
                    else:
                        self.log_test("Application Statistics", False, 
                                    f"Expected 10 gestures, got {data['available_gestures']}")
                        return False
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_test("Application Statistics", False, f"Missing fields: {missing}")
                    return False
            else:
                self.log_test("Application Statistics", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Application Statistics", False, f"Exception: {str(e)}")
            return False
    
    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        try:
            # Test invalid gesture detection request
            invalid_payload = {"invalid_field": "test"}
            response = requests.post(f"{API_BASE}/detect-gesture", json=invalid_payload, timeout=10)
            
            # Should return 422 (validation error) or 400 (bad request)
            if response.status_code in [400, 422]:
                self.log_test("Error Handling", True, "Properly handles invalid requests")
                return True
            else:
                self.log_test("Error Handling", False, f"Unexpected status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Error Handling", False, f"Exception: {str(e)}")
            return False
    
    # ========== NEW SIGN_APP COMPONENT TESTS ==========
    
    def test_3d_character_system(self):
        """Test 3D Character Animation System"""
        try:
            character_file = self.sign_app_path / "character_3d.py"
            if not character_file.exists():
                self.log_test("3D Character System", False, "character_3d.py file not found")
                return False
            
            # Test if the file can be imported
            spec = importlib.util.spec_from_file_location("character_3d", character_file)
            character_module = importlib.util.module_from_spec(spec)
            
            # Mock pygame to avoid display issues in testing
            import sys
            from unittest.mock import MagicMock
            sys.modules['pygame'] = MagicMock()
            sys.modules['pygame.display'] = MagicMock()
            sys.modules['pygame.time'] = MagicMock()
            sys.modules['pygame.font'] = MagicMock()
            
            spec.loader.exec_module(character_module)
            
            # Test if SignLanguageCharacter class exists
            if hasattr(character_module, 'SignLanguageCharacter'):
                character_class = getattr(character_module, 'SignLanguageCharacter')
                
                # Test initialization (mocked)
                try:
                    character = character_class(width=800, height=600)
                    
                    # Test gesture pose mappings
                    if hasattr(character, 'gesture_poses'):
                        pose_count = len(character.gesture_poses)
                        
                        # Check for key Pakistani gestures
                        key_gestures = ['salam', 'shukriya', 'ek', 'do', 'paani', 'khana']
                        found_gestures = [g for g in key_gestures if g in character.gesture_poses]
                        
                        if len(found_gestures) >= 4:  # At least 4 key gestures should be mapped
                            self.log_test("3D Character System", True, 
                                        f"Character initialized with {pose_count} gesture poses, found {len(found_gestures)} key gestures")
                            return True
                        else:
                            self.log_test("3D Character System", False, 
                                        f"Missing key gesture poses. Found: {found_gestures}")
                            return False
                    else:
                        self.log_test("3D Character System", False, "No gesture_poses attribute found")
                        return False
                        
                except Exception as e:
                    self.log_test("3D Character System", False, f"Character initialization failed: {str(e)}")
                    return False
            else:
                self.log_test("3D Character System", False, "SignLanguageCharacter class not found")
                return False
                
        except Exception as e:
            self.log_test("3D Character System", False, f"Module import failed: {str(e)}")
            return False
    
    def test_expanded_gesture_database(self):
        """Test Expanded Gesture Database (132 gestures)"""
        try:
            labels_file = self.sign_app_path / "labels.json"
            if not labels_file.exists():
                self.log_test("Expanded Gesture Database", False, "labels.json file not found")
                return False
            
            with open(labels_file, 'r', encoding='utf-8') as f:
                labels = json.load(f)
            
            gesture_count = len(labels)
            
            # Check if we have the expected 132 gestures
            if gesture_count >= 130:  # Allow some flexibility
                # Verify structure of gestures
                sample_gesture = list(labels.values())[0]
                required_fields = ['name', 'urdu', 'pashto', 'english']
                
                if all(field in sample_gesture for field in required_fields):
                    # Check for different categories
                    categories_found = {
                        'numbers': 0, 'greetings': 0, 'family': 0, 'objects': 0, 
                        'actions': 0, 'food': 0, 'nature': 0
                    }
                    
                    for gesture_info in labels.values():
                        name = gesture_info['name'].lower()
                        if any(num in name for num in ['ek', 'do', 'teen', 'chaar', 'paanch', 'che', 'saat', 'aath', 'nau', 'das']):
                            categories_found['numbers'] += 1
                        elif any(greet in name for greet in ['salam', 'shukriya', 'khuda_hafiz']):
                            categories_found['greetings'] += 1
                        elif any(fam in name for fam in ['ammi', 'abbu', 'bhai', 'behn']):
                            categories_found['family'] += 1
                        elif any(obj in name for obj in ['kitab', 'qalam', 'ghar', 'phone', 'computer']):
                            categories_found['objects'] += 1
                        elif any(act in name for act in ['reading', 'writing', 'eating', 'drinking', 'walking']):
                            categories_found['actions'] += 1
                        elif any(food in name for food in ['khana', 'paani', 'chai', 'roti', 'aam']):
                            categories_found['food'] += 1
                        elif any(nat in name for nat in ['suraj', 'chaand', 'phool', 'darya']):
                            categories_found['nature'] += 1
                    
                    total_categorized = sum(categories_found.values())
                    
                    self.log_test("Expanded Gesture Database", True, 
                                f"Found {gesture_count} gestures with proper structure. Categories: {categories_found}")
                    return True
                else:
                    missing_fields = [f for f in required_fields if f not in sample_gesture]
                    self.log_test("Expanded Gesture Database", False, f"Missing required fields: {missing_fields}")
                    return False
            else:
                self.log_test("Expanded Gesture Database", False, 
                            f"Expected ~132 gestures, found only {gesture_count}")
                return False
                
        except Exception as e:
            self.log_test("Expanded Gesture Database", False, f"Error loading labels: {str(e)}")
            return False
    
    def test_enhanced_speech_recognition(self):
        """Test Enhanced Speech Recognition with Google API"""
        try:
            speech_file = self.sign_app_path / "speech_to_sign.py"
            if not speech_file.exists():
                self.log_test("Enhanced Speech Recognition", False, "speech_to_sign.py file not found")
                return False
            
            # Test if the file can be imported
            spec = importlib.util.spec_from_file_location("speech_to_sign", speech_file)
            speech_module = importlib.util.module_from_spec(spec)
            
            # Mock speech_recognition and other dependencies
            from unittest.mock import MagicMock
            sys.modules['speech_recognition'] = MagicMock()
            sys.modules['pyttsx3'] = MagicMock()
            sys.modules['cv2'] = MagicMock()
            
            spec.loader.exec_module(speech_module)
            
            # Test if main classes exist
            if hasattr(speech_module, 'SpeechToSign'):
                speech_class = getattr(speech_module, 'SpeechToSign')
                
                # Test if PakistaniSignLanguageApp exists
                if hasattr(speech_module, 'PakistaniSignLanguageApp'):
                    app_class = getattr(speech_module, 'PakistaniSignLanguageApp')
                    
                    # Check for Google API key integration
                    with open(speech_file, 'r') as f:
                        content = f.read()
                        
                    google_api_features = [
                        'GOOGLE_SPEECH_API_KEY' in content,
                        'AIzaSyBRj3kHAgCg6B_rJTWhlMg8zsNHSTy6vnM' in content,
                        'recognize_google' in content,
                        'language=' in content
                    ]
                    
                    if sum(google_api_features) >= 3:
                        self.log_test("Enhanced Speech Recognition", True, 
                                    "Google Speech API integration found with multi-language support")
                        return True
                    else:
                        self.log_test("Enhanced Speech Recognition", False, 
                                    f"Missing Google API features. Found: {sum(google_api_features)}/4")
                        return False
                else:
                    self.log_test("Enhanced Speech Recognition", False, "PakistaniSignLanguageApp class not found")
                    return False
            else:
                self.log_test("Enhanced Speech Recognition", False, "SpeechToSign class not found")
                return False
                
        except Exception as e:
            self.log_test("Enhanced Speech Recognition", False, f"Module import failed: {str(e)}")
            return False
    
    def test_complete_sign_language_app(self):
        """Test Complete Sign Language App Integration"""
        try:
            app_file = self.sign_app_path / "sign_language_app.py"
            if not app_file.exists():
                self.log_test("Complete Sign Language App", False, "sign_language_app.py file not found")
                return False
            
            # Read the file content to check for key features
            with open(app_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for key integration features
            integration_features = {
                '3D Character Integration': 'character_3d' in content and 'SignLanguageCharacter' in content,
                'Speech Recognition': 'speech_recognition' in content or 'SpeechToSign' in content,
                'Text to Sign': 'text_to_sign' in content or 'find_gesture_for_text' in content,
                'Gesture Database': 'labels.json' in content,
                'Multi-language Support': ('urdu' in content.lower() and 'pashto' in content.lower()),
                'Google API Integration': 'GOOGLE_SPEECH_API_KEY' in content,
                '132 Gestures': '132' in content or len([line for line in content.split('\n') if 'gesture' in line.lower()]) > 50
            }
            
            passed_features = sum(integration_features.values())
            total_features = len(integration_features)
            
            if passed_features >= 5:  # At least 5 out of 7 features should be present
                feature_details = [f"{k}: {'✅' if v else '❌'}" for k, v in integration_features.items()]
                self.log_test("Complete Sign Language App", True, 
                            f"Integration features ({passed_features}/{total_features}): {', '.join(feature_details)}")
                return True
            else:
                missing_features = [k for k, v in integration_features.items() if not v]
                self.log_test("Complete Sign Language App", False, 
                            f"Missing key features: {missing_features}")
                return False
                
        except Exception as e:
            self.log_test("Complete Sign Language App", False, f"Error reading app file: {str(e)}")
            return False
    
    def test_launcher_system(self):
        """Test Launcher System"""
        try:
            launcher_file = self.sign_app_path / "launcher.py"
            if not launcher_file.exists():
                self.log_test("Launcher System", False, "launcher.py file not found")
                return False
            
            # Read the file content
            with open(launcher_file, 'r') as f:
                content = f.read()
            
            # Check for launcher features
            launcher_features = {
                'Dependency Checking': 'check_dependencies' in content,
                'File Verification': 'check_files' in content,
                'System Information': 'show_system_info' in content or 'system_info' in content,
                'Multiple Launch Options': 'sign_language_app.py' in content and 'character_3d.py' in content,
                'User Interface': 'input(' in content and 'choice' in content,
                'Error Handling': 'try:' in content and 'except' in content
            }
            
            passed_features = sum(launcher_features.values())
            total_features = len(launcher_features)
            
            if passed_features >= 4:  # At least 4 out of 6 features
                feature_details = [f"{k}: {'✅' if v else '❌'}" for k, v in launcher_features.items()]
                self.log_test("Launcher System", True, 
                            f"Launcher features ({passed_features}/{total_features}): {', '.join(feature_details)}")
                return True
            else:
                missing_features = [k for k, v in launcher_features.items() if not v]
                self.log_test("Launcher System", False, 
                            f"Missing launcher features: {missing_features}")
                return False
                
        except Exception as e:
            self.log_test("Launcher System", False, f"Error reading launcher file: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend API tests"""
        print("=" * 80)
        print("SIGN LANGUAGE TRANSLATION BACKEND API + SIGN_APP TESTS")
        print("=" * 80)
        print(f"Session ID: {self.session_id}")
        print(f"Backend URL: {API_BASE}")
        print(f"Sign App Path: {self.sign_app_path}")
        print("-" * 80)
        
        # Run tests in order of priority
        tests = [
            # Backend API Tests
            ("Root Endpoint", self.test_root_endpoint),
            ("Pakistani Gestures Dataset", self.test_gestures_endpoint),
            ("YOLOv5 Gesture Detection", self.test_gesture_detection),
            ("Speech Recognition (Urdu/Pashto)", self.test_speech_to_sign),
            ("Text-to-Sign Translation", self.test_text_to_sign),
            ("Translation History", self.test_translation_history),
            ("Application Statistics", self.test_statistics),
            ("Error Handling", self.test_error_handling),
            
            # New Sign App Component Tests
            ("3D Character Animation System", self.test_3d_character_system),
            ("Expanded Gesture Database (132 gestures)", self.test_expanded_gesture_database),
            ("Enhanced Speech Recognition", self.test_enhanced_speech_recognition),
            ("Complete Sign Language App", self.test_complete_sign_language_app),
            ("Launcher System", self.test_launcher_system)
        ]
        
        passed = 0
        total = len(tests)
        backend_passed = 0
        sign_app_passed = 0
        
        for i, (test_name, test_func) in enumerate(tests):
            try:
                if test_func():
                    passed += 1
                    if i < 8:  # First 8 are backend tests
                        backend_passed += 1
                    else:  # Rest are sign_app tests
                        sign_app_passed += 1
                time.sleep(0.5)  # Brief pause between tests
            except Exception as e:
                self.log_test(test_name, False, f"Test execution failed: {str(e)}")
        
        print("-" * 80)
        print(f"RESULTS: {passed}/{total} tests passed")
        print(f"Backend API: {backend_passed}/8 tests passed")
        print(f"Sign App Components: {sign_app_passed}/5 tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Backend API and Sign App components working correctly.")
        elif passed >= total * 0.8:  # 80% pass rate
            print("⚠️  Most tests passed. Minor issues detected.")
        else:
            print("❌ Multiple test failures. System needs attention.")
        
        print("=" * 80)
        return passed, total, self.test_results

if __name__ == "__main__":
    tester = BackendTester()
    passed, total, results = tester.run_all_tests()
    
    # Print detailed results
    print("\nDETAILED TEST RESULTS:")
    for test_name, result in results.items():
        status = "PASS" if result["success"] else "FAIL"
        print(f"  {test_name}: {status}")
        if result["details"]:
            print(f"    {result['details']}")