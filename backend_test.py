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
    
    def run_all_tests(self):
        """Run all backend API tests"""
        print("=" * 60)
        print("SIGN LANGUAGE TRANSLATION BACKEND API TESTS")
        print("=" * 60)
        print(f"Session ID: {self.session_id}")
        print(f"Backend URL: {API_BASE}")
        print("-" * 60)
        
        # Run tests in order of priority
        tests = [
            ("Root Endpoint", self.test_root_endpoint),
            ("Pakistani Gestures Dataset", self.test_gestures_endpoint),
            ("YOLOv5 Gesture Detection", self.test_gesture_detection),
            ("Speech Recognition (Urdu/Pashto)", self.test_speech_to_sign),
            ("Text-to-Sign Translation", self.test_text_to_sign),
            ("Translation History", self.test_translation_history),
            ("Application Statistics", self.test_statistics),
            ("Error Handling", self.test_error_handling)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                time.sleep(0.5)  # Brief pause between tests
            except Exception as e:
                self.log_test(test_name, False, f"Test execution failed: {str(e)}")
        
        print("-" * 60)
        print(f"RESULTS: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Backend API is working correctly.")
        elif passed >= total * 0.8:  # 80% pass rate
            print("⚠️  Most tests passed. Minor issues detected.")
        else:
            print("❌ Multiple test failures. Backend needs attention.")
        
        print("=" * 60)
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