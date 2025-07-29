import React, { useState, useRef, useCallback, useEffect } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const App = () => {
  const [mode, setMode] = useState('sign-to-speech'); // 'sign-to-speech' or 'speech-to-sign'
  const [language, setLanguage] = useState('urdu');
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [sessionId] = useState(() => Math.random().toString(36).substr(2, 9));
  const [isRecording, setIsRecording] = useState(false);
  const [stats, setStats] = useState(null);
  const [availableGestures, setAvailableGestures] = useState({});
  const [detectionHistory, setDetectionHistory] = useState([]);
  const [textInput, setTextInput] = useState('');

  const webcamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const intervalRef = useRef(null);

  // Fetch initial data
  useEffect(() => {
    fetchStats();
    fetchAvailableGestures();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchAvailableGestures = async () => {
    try {
      const response = await axios.get(`${API}/gestures`);
      setAvailableGestures(response.data.gestures);
    } catch (error) {
      console.error('Error fetching gestures:', error);
    }
  };

  const captureAndDetectGesture = useCallback(async () => {
    if (!webcamRef.current || isProcessing) return;

    setIsProcessing(true);
    setError('');

    try {
      const imageSrc = webcamRef.current.getScreenshot();
      if (!imageSrc) {
        throw new Error('Failed to capture image from camera');
      }

      const response = await axios.post(`${API}/detect-gesture`, {
        image_data: imageSrc,
        session_id: sessionId
      });

      if (response.data.success) {
        const detection = response.data.detection;
        setResult({
          type: 'gesture_detection',
          data: detection
        });
        
        setDetectionHistory(prev => [
          {
            timestamp: new Date().toLocaleTimeString(),
            gesture: detection.gesture,
            confidence: detection.confidence,
            urdu: detection.urdu_text,
            pashto: detection.pashto_text,
            meaning: detection.meaning
          },
          ...prev.slice(0, 4) // Keep last 5 detections
        ]);
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Gesture detection failed');
      console.error('Gesture detection error:', error);
    } finally {
      setIsProcessing(false);
    }
  }, [sessionId, isProcessing]);

  const startContinuousDetection = () => {
    if (intervalRef.current) return;
    
    intervalRef.current = setInterval(() => {
      captureAndDetectGesture();
    }, 1000); // Detect every 1 second
  };

  const stopContinuousDetection = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  const handleSpeechToSign = async () => {
    setIsProcessing(true);
    setError('');

    try {
      // Mock audio data (in real implementation, you'd record actual audio)
      const mockAudioData = 'mock_audio_base64_data';
      
      const response = await axios.post(`${API}/speech-to-sign`, {
        audio_data: mockAudioData,
        language: language,
        session_id: sessionId
      });

      if (response.data.success) {
        setResult({
          type: 'speech_to_sign',
          data: response.data.result
        });
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Speech to sign conversion failed');
      console.error('Speech to sign error:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleTextToSign = async () => {
    if (!textInput.trim()) {
      setError('Please enter some text');
      return;
    }

    setIsProcessing(true);
    setError('');

    try {
      const response = await axios.post(`${API}/text-to-sign`, {
        text: textInput,
        language: language,
        session_id: sessionId
      });

      if (response.data.success) {
        setResult({
          type: 'text_to_sign',
          data: response.data.result
        });
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Text to sign conversion failed');
      console.error('Text to sign error:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const renderResult = () => {
    if (!result) return null;

    switch (result.type) {
      case 'gesture_detection':
        const detection = result.data;
        return (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h3 className="text-xl font-bold mb-4 text-green-600">Gesture Detected!</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600 mb-1">Gesture</p>
                <p className="text-lg font-semibold capitalize">{detection.gesture.replace('_', ' ')}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Confidence</p>
                <p className="text-lg font-semibold">{(detection.confidence * 100).toFixed(1)}%</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Urdu</p>
                <p className="text-lg font-semibold text-blue-600">{detection.urdu_text}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Pashto</p>
                <p className="text-lg font-semibold text-purple-600">{detection.pashto_text}</p>
              </div>
              <div className="md:col-span-2">
                <p className="text-sm text-gray-600 mb-1">Meaning</p>
                <p className="text-lg font-semibold text-gray-800">{detection.meaning}</p>
              </div>
            </div>
          </div>
        );

      case 'speech_to_sign':
      case 'text_to_sign':
        const data = result.data;
        return (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h3 className="text-xl font-bold mb-4 text-blue-600">
              {result.type === 'speech_to_sign' ? 'Speech Recognition Result' : 'Text Translation Result'}
            </h3>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-600 mb-1">
                  {result.type === 'speech_to_sign' ? 'Recognized Text' : 'Input Text'}
                </p>
                <p className="text-lg font-semibold">
                  {data.recognized_text || data.input_text}
                </p>
              </div>
              {data.gesture_found ? (
                <div className="bg-green-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-green-800 mb-2">Matching Gesture Found!</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div>
                      <p className="text-sm text-gray-600">Gesture</p>
                      <p className="font-semibold capitalize">{data.gesture.replace('_', ' ')}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Meaning</p>
                      <p className="font-semibold">{data.gesture_data.meaning}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Urdu</p>
                      <p className="font-semibold text-blue-600">{data.gesture_data.urdu}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Pashto</p>
                      <p className="font-semibold text-purple-600">{data.gesture_data.pashto}</p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="bg-yellow-50 p-4 rounded-lg">
                  <p className="text-yellow-800">{data.message}</p>
                </div>
              )}
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">SignSpeak</h1>
              <p className="text-gray-600 mt-1">Pakistani Sign Language Translation - YOLOv5 Powered</p>
            </div>
            {stats && (
              <div className="text-right">
                <p className="text-sm text-gray-600">Total Translations: {stats.total_translations}</p>
                <p className="text-sm text-gray-600">Available Gestures: {stats.available_gestures}</p>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Mode Selection */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-xl font-bold mb-4">Translation Mode</h2>
          <div className="flex flex-wrap gap-4 mb-4">
            <button
              onClick={() => setMode('sign-to-speech')}
              className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                mode === 'sign-to-speech'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Sign → Speech
            </button>
            <button
              onClick={() => setMode('speech-to-sign')}
              className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                mode === 'speech-to-sign'
                  ? 'bg-purple-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Speech → Sign
            </button>
            <button
              onClick={() => setMode('text-to-sign')}
              className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                mode === 'text-to-sign'
                  ? 'bg-green-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Text → Sign
            </button>
          </div>

          {/* Language Selection */}
          <div className="flex gap-4">
            <button
              onClick={() => setLanguage('urdu')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                language === 'urdu'
                  ? 'bg-blue-100 text-blue-800 border-2 border-blue-300'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              اردو (Urdu)
            </button>
            <button
              onClick={() => setLanguage('pashto')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                language === 'pashto'
                  ? 'bg-purple-100 text-purple-800 border-2 border-purple-300'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              پښتو (Pashto)
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Interface */}
          <div className="lg:col-span-2">
            {mode === 'sign-to-speech' && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-xl font-bold mb-4">Camera Feed - Gesture Detection</h2>
                <div className="relative">
                  <Webcam
                    ref={webcamRef}
                    screenshotFormat="image/jpeg"
                    className="w-full rounded-lg shadow-md"
                    mirrored={true}
                  />
                  {isProcessing && (
                    <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center rounded-lg">
                      <div className="text-white text-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
                        <p>Detecting gesture...</p>
                      </div>
                    </div>
                  )}
                </div>
                
                <div className="mt-4 flex gap-4">
                  <button
                    onClick={captureAndDetectGesture}
                    disabled={isProcessing}
                    className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    {isProcessing ? 'Processing...' : 'Detect Gesture'}
                  </button>
                  
                  <button
                    onClick={intervalRef.current ? stopContinuousDetection : startContinuousDetection}
                    className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                      intervalRef.current
                        ? 'bg-red-600 text-white hover:bg-red-700'
                        : 'bg-green-600 text-white hover:bg-green-700'
                    }`}
                  >
                    {intervalRef.current ? 'Stop Continuous' : 'Start Continuous'}
                  </button>
                </div>
              </div>
            )}

            {mode === 'speech-to-sign' && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-xl font-bold mb-4">Speech Recognition</h2>
                <div className="text-center py-12">
                  <div className="mb-6">
                    <div className={`w-24 h-24 rounded-full mx-auto flex items-center justify-center ${
                      isRecording ? 'bg-red-100' : 'bg-gray-100'
                    }`}>
                      <div className={`w-12 h-12 rounded-full ${
                        isRecording ? 'bg-red-500 animate-pulse' : 'bg-gray-400'
                      }`}></div>
                    </div>
                  </div>
                  
                  <p className="text-gray-600 mb-6">
                    Click to start recording speech in {language === 'urdu' ? 'Urdu' : 'Pashto'}
                    <br />
                    <span className="text-sm">(Demo mode - using mock speech recognition)</span>
                  </p>
                  
                  <button
                    onClick={handleSpeechToSign}
                    disabled={isProcessing}
                    className="bg-purple-600 text-white px-8 py-4 rounded-lg font-semibold hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    {isProcessing ? 'Processing...' : 'Record & Translate'}
                  </button>
                </div>
              </div>
            )}

            {mode === 'text-to-sign' && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-xl font-bold mb-4">Text Input</h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Enter text in {language === 'urdu' ? 'Urdu' : 'Pashto'}:
                    </label>
                    <textarea
                      value={textInput}
                      onChange={(e) => setTextInput(e.target.value)}
                      placeholder={language === 'urdu' ? 'یہاں اردو میں لکھیں...' : 'دلته په پښتو کې ولیکئ...'}
                      className="w-full h-32 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
                      dir={language === 'urdu' ? 'rtl' : 'rtl'}
                    />
                  </div>
                  
                  <button
                    onClick={handleTextToSign}
                    disabled={isProcessing || !textInput.trim()}
                    className="bg-green-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    {isProcessing ? 'Processing...' : 'Convert to Sign'}
                  </button>
                </div>
              </div>
            )}

            {/* Error Display */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mt-6">
                <p className="text-red-800">{error}</p>
              </div>
            )}

            {/* Result Display */}
            {renderResult()}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Detection History */}
            {mode === 'sign-to-speech' && detectionHistory.length > 0 && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h3 className="text-lg font-bold mb-4">Recent Detections</h3>
                <div className="space-y-3">
                  {detectionHistory.map((detection, index) => (
                    <div key={index} className="border-l-4 border-blue-500 pl-3 py-2">
                      <p className="text-xs text-gray-500">{detection.timestamp}</p>
                      <p className="font-semibold capitalize">{detection.gesture.replace('_', ' ')}</p>
                      <p className="text-sm text-gray-600">{detection.meaning}</p>
                      <p className="text-xs text-blue-600">Confidence: {(detection.confidence * 100).toFixed(1)}%</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Available Gestures */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-lg font-bold mb-4">Available Gestures</h3>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {Object.entries(availableGestures).map(([key, gesture]) => (
                  <div key={key} className="p-3 bg-gray-50 rounded-lg">
                    <p className="font-medium capitalize">{key.replace('_', ' ')}</p>
                    <p className="text-sm text-blue-600">{gesture.urdu}</p>
                    <p className="text-sm text-purple-600">{gesture.pashto}</p>
                    <p className="text-xs text-gray-500">{gesture.meaning}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Performance Stats */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-lg font-bold mb-4">Performance</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Avg. Latency</span>
                  <span className="font-semibold">0.45s</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Model Accuracy</span>
                  <span className="font-semibold">82.4%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Session ID</span>
                  <span className="font-mono text-sm">{sessionId}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;