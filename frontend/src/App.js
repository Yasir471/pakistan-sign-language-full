import React, { useState, useRef, useCallback, useEffect } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const App = () => {
  const [mode, setMode] = useState('sign-to-speech'); // 'sign-to-speech', 'speech-to-sign', 'text-to-sign', or 'story'
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
  const [isContinuousMode, setIsContinuousMode] = useState(false);

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
        
        // Only add to history if a real gesture was detected
        if (detection.gesture !== "no_hand_detected") {
          setDetectionHistory(prev => [
            {
              timestamp: new Date().toLocaleTimeString(),
              gesture: detection.gesture,
              confidence: detection.confidence,
              urdu: detection.urdu_text,
              pashto: detection.pashto_text,
              meaning: detection.meaning,
              detection_method: detection.detection_method || "YOLOv5 + Hand Tracking",
              landmarks_detected: detection.landmarks_detected || false
            },
            ...prev.slice(0, 4) // Keep last 5 detections
          ]);
        }
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
    
    setIsContinuousMode(true);
    intervalRef.current = setInterval(() => {
      captureAndDetectGesture();
    }, 1500); // Detect every 1.5 seconds for better performance
  };

  const stopContinuousDetection = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
      setIsContinuousMode(false);
    }
  };

  const handleSpeechToSign = async () => {
    setIsProcessing(true);
    setError('');
    setResult(null);

    try {
      const response = await axios.post(`${API}/speech-to-sign`, {
        language: language,
        session_id: sessionId
      });
      
      // If we get a valid gesture response, launch 3D character
      if (response.data && response.data.gesture) {
        const characterResponse = await launch3DCharacterForGesture({
          gesture: response.data.gesture
        });
        
        // Combine the speech recognition result with 3D character launch
        setResult({
          ...response.data,
          character: characterResponse,
          character_launched: characterResponse.status === 'success'
        });
      } else {
        setResult(response.data);
      }
    } catch (error) {
      setError(error.response?.data?.error || 'Speech recognition failed');
    } finally {
      setIsProcessing(false);
    }
  };

  const launch3DCharacterForGesture = async (gestureData) => {
    try {
      const response = await axios.post(`${API}/launch-3d-character`, {
        mode: 'gesture',
        gesture: gestureData.gesture || 'salam',
        language: language
      });
      
      return response.data;
    } catch (error) {
      console.error('3D Character launch error:', error);
      return { 
        status: 'error', 
        message: 'Failed to launch 3D character',
        fallback: 'Character animation not available in web environment' 
      };
    }
  };

  const handleTextToSign = async () => {
    if (!textInput.trim()) return;

    setIsProcessing(true);
    setError('');
    setResult(null);

    try {
      const response = await axios.post(`${API}/text-to-sign`, {
        text: textInput,
        language: language,
        session_id: sessionId
      });
      
      // If we get a valid gesture response, launch 3D character
      if (response.data && response.data.gesture) {
        const characterResponse = await launch3DCharacterForGesture({
          gesture: response.data.gesture
        });
        
        // Combine the text-to-sign result with 3D character launch
        setResult({
          ...response.data,
          character: characterResponse,
          character_launched: characterResponse.status === 'success',
          original_text: textInput
        });
      } else {
        setResult(response.data);
      }
    } catch (error) {
      setError(error.response?.data?.error || 'Text to sign conversion failed');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleStoryMode = async (storyLanguage) => {
    setIsProcessing(true);
    setError('');
    setResult(null);

    try {
      // Actually launch the 3D character story mode
      const response = await axios.post(`${API}/launch-3d-character`, {
        mode: 'story',
        language: storyLanguage,
        gesture: 'story'
      });
      
      if (response.data.status === 'success') {
        setResult({
          type: 'story',
          language: storyLanguage,
          story: {
            title: storyLanguage === 'urdu' ? 'انگور تو کھٹے ہیں' : 
                   storyLanguage === 'pashto' ? 'انګور خو تروې دي' : 'The Sour Grapes',
            message: response.data.message,
            instructions: response.data.instructions,
            pid: response.data.pid,
            status: 'launched'
          }
        });
      } else {
        setError(response.data.message || 'Failed to launch 3D character');
      }
    } catch (error) {
      setError(error.response?.data?.message || 'Story mode failed to start. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const renderResult = () => {
    if (!result) return null;

    switch (result.type) {
      case 'gesture_detection':
        const detection = result.data;
        
        // Handle no hand detection case
        if (detection.gesture === "no_hand_detected") {
          return (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-6">
              <h3 className="text-xl font-bold mb-4 text-yellow-700">No Hand Detected</h3>
              <div className="text-center">
                <div className="text-6xl mb-4">🤚</div>
                <p className="text-gray-600 mb-2">Place your hand in front of the camera</p>
                <p className="text-sm text-gray-500">Make sure your hand is clearly visible and well-lit</p>
                {detection.detection_method && (
                  <p className="text-xs text-blue-600 mt-2">
                    Detection Method: {detection.detection_method}
                  </p>
                )}
              </div>
            </div>
          );
        }
        
        return (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h3 className="text-xl font-bold mb-4 text-green-600">✋ Real Hand Gesture Detected!</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600 mb-1">Gesture</p>
                <p className="text-lg font-semibold capitalize">{detection.gesture.replace('_', ' ')}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Confidence</p>
                <div className="flex items-center">
                  <p className="text-lg font-semibold mr-2">{(detection.confidence * 100).toFixed(1)}%</p>
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-500 h-2 rounded-full transition-all duration-300" 
                      style={{width: `${detection.confidence * 100}%`}}
                    ></div>
                  </div>
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Urdu</p>
                <p className="text-lg font-semibold text-blue-600 urdu-text">{detection.urdu_text}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Pashto</p>
                <p className="text-lg font-semibold text-purple-600 pashto-text">{detection.pashto_text}</p>
              </div>
              <div className="md:col-span-2">
                <p className="text-sm text-gray-600 mb-1">Meaning</p>
                <p className="text-lg font-semibold text-gray-800">{detection.meaning}</p>
              </div>
              {detection.detection_method && (
                <div className="md:col-span-2 bg-blue-50 p-3 rounded-lg">
                  <p className="text-sm text-blue-800">
                    <span className="font-medium">Detection Engine:</span> {detection.detection_method}
                  </p>
                  {detection.landmarks_detected && (
                    <p className="text-xs text-blue-600 mt-1">
                      ✓ Hand tracking successfully detected and analyzed
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
        );

      case 'speech_to_sign':
      case 'text_to_sign':
        const data = result.data;
        return (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h3 className="text-xl font-bold mb-4 text-blue-600">
              {result.type === 'speech_to_sign' ? '🎤 Speech Recognition Result' : '📝 Text Translation Result'}
            </h3>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-600 mb-1">
                  {result.type === 'speech_to_sign' ? 'Recognized Text' : 'Input Text'}
                </p>
                <p className="text-lg font-semibold p-3 bg-gray-50 rounded-lg">
                  {data.recognized_text || data.input_text}
                </p>
              </div>
              {data.gesture_found ? (
                <div className="bg-green-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-green-800 mb-2">🎯 Matching Gesture Found!</h4>
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
                      <p className="font-semibold text-blue-600 urdu-text">{data.gesture_data.urdu}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Pashto</p>
                      <p className="font-semibold text-purple-600 pashto-text">{data.gesture_data.pashto}</p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="bg-yellow-50 p-4 rounded-lg">
                  <p className="text-yellow-800">⚠️ {data.message}</p>
                  <p className="text-sm text-yellow-600 mt-1">Try different words or check the available gestures list</p>
                </div>
              )}
            </div>
          </div>
        );

      case 'story':
        const story = result.story;
        return (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h3 className="text-xl font-bold mb-4 text-orange-600">🎭 Pakistani Story Mode</h3>
            <div className="space-y-4">
              <div className="bg-gradient-to-r from-orange-100 to-amber-100 p-4 rounded-lg">
                <h4 className="text-lg font-bold mb-2">{story.title}</h4>
                <p className="text-sm text-gray-700 mb-3">Language: {result.language}</p>
                <div className="bg-white p-3 rounded-lg">
                  <p className="text-gray-800">{story.message}</p>
                </div>
              </div>
              <div className="bg-blue-50 p-4 rounded-lg">
                <h5 className="font-semibold text-blue-800 mb-2">📋 Instructions:</h5>
                <p className="text-sm text-blue-700">{story.instructions}</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <h5 className="font-semibold text-green-800 mb-2">✨ Story Features:</h5>
                <ul className="text-sm text-green-700 space-y-1">
                  <li>• 3D animated character with Pakistani sign language gestures</li>
                  <li>• Interactive storytelling with moral lessons</li>
                  <li>• Cultural context and traditional Pakistani tales</li>
                  <li>• Educational sign language vocabulary building</li>
                </ul>
              </div>
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
              <h1 className="text-3xl font-bold text-gray-900">🤟 SignSpeak</h1>
              <p className="text-gray-600 mt-1">Pakistani Sign Language Translation - YOLOv5 + Speech Recognition</p>
            </div>
            {stats && (
              <div className="text-right">
                <p className="text-sm text-gray-600">Total Translations: {stats.total_translations}</p>
                <p className="text-sm text-gray-600">Available Gestures: {stats.available_gestures}</p>
                <p className="text-xs text-green-600 font-medium">✅ {stats.technology_engine}</p>
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
              👋 Sign → Speech
            </button>
            <button
              onClick={() => setMode('speech-to-sign')}
              className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                mode === 'speech-to-sign'
                  ? 'bg-purple-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              🎤 Speech → Sign
            </button>
            <button
              onClick={() => setMode('text-to-sign')}
              className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                mode === 'text-to-sign'
                  ? 'bg-green-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              📝 Text → Sign
            </button>
            <button
              onClick={() => setMode('story')}
              className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                mode === 'story'
                  ? 'bg-orange-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              📚 Pakistani Story
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
                <h2 className="text-xl font-bold mb-4">📹 Real-time Hand Gesture Detection</h2>
                <div className="relative">
                  <Webcam
                    ref={webcamRef}
                    screenshotFormat="image/jpeg"
                    className="w-full rounded-lg shadow-md"
                    mirrored={true}
                    width={640}
                    height={480}
                  />
                  {isProcessing && (
                    <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center rounded-lg">
                      <div className="text-white text-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
                        <p>🔍 Analyzing hand movement...</p>
                        <p className="text-sm mt-1">YOLOv5 Processing</p>
                      </div>
                    </div>
                  )}
                  {isContinuousMode && !isProcessing && (
                    <div className="absolute top-4 right-4 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-medium animate-pulse">
                      🔴 LIVE
                    </div>
                  )}
                </div>
                
                <div className="mt-4 flex gap-4 flex-wrap">
                  <button
                    onClick={captureAndDetectGesture}
                    disabled={isProcessing}
                    className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    {isProcessing ? '🔄 Processing...' : '📸 Detect Hand Gesture'}
                  </button>
                  
                  <button
                    onClick={isContinuousMode ? stopContinuousDetection : startContinuousDetection}
                    className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                      isContinuousMode
                        ? 'bg-red-600 text-white hover:bg-red-700'
                        : 'bg-green-600 text-white hover:bg-green-700'
                    }`}
                  >
                    {isContinuousMode ? '⏹️ Stop Live Detection' : '▶️ Start Live Detection'}
                  </button>
                </div>

                <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-semibold text-blue-800 mb-2">💡 Tips for Best Results:</h4>
                  <ul className="text-sm text-blue-700 space-y-1">
                    <li>• Place your hand clearly in front of the camera</li>
                    <li>• Ensure good lighting conditions</li>
                    <li>• Make distinct hand gestures</li>
                    <li>• Keep your hand steady for a moment</li>
                  </ul>
                </div>
              </div>
            )}

            {mode === 'speech-to-sign' && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-xl font-bold mb-4">🎤 Speech Recognition</h2>
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

                  </p>
                  
                  <button
                    onClick={handleSpeechToSign}
                    disabled={isProcessing}
                    className="bg-purple-600 text-white px-8 py-4 rounded-lg font-semibold hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    {isProcessing ? '🎧 Processing...' : '🎤 Record & Translate'}
                  </button>
                </div>
              </div>
            )}

            {mode === 'text-to-sign' && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-xl font-bold mb-4">📝 Text Input</h2>
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
                    {isProcessing ? '⚙️ Processing...' : '🔄 Convert to Sign'}
                  </button>
                </div>
              </div>
            )}

            {/* Story Mode */}
            {mode === 'story' && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-xl font-bold mb-4">📚 Pakistani Story: انگور تو کھٹے ہیں</h2>
                <div className="space-y-4">
                  <div className="bg-gradient-to-r from-orange-100 to-amber-100 p-4 rounded-lg">
                    <h3 className="font-bold text-lg mb-2">🦊 The Sour Grapes (انگور تو کھٹے ہیں)</h3>
                    <p className="text-sm text-gray-700 mb-3">Classic Pakistani story with 3D sign language character demonstrations</p>
                    
                    <div className="space-y-2 mb-4">
                      <p className="text-sm">🇵🇰 <strong>Urdu:</strong> انگور تو کھٹے ہیں</p>
                      <p className="text-sm">🇦🇫 <strong>Pashto:</strong> انګور خو تروې دي</p>
                      <p className="text-sm">🏴󠁧󠁢󠁥󠁮󠁧󠁿 <strong>English:</strong> The Sour Grapes</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                      <button
                        onClick={() => handleStoryMode('urdu')}
                        disabled={isProcessing}
                        className="bg-green-600 text-white px-4 py-3 rounded-lg font-semibold hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all text-sm"
                      >
                        🇵🇰 Urdu Story with 3D Character
                      </button>
                      <button
                        onClick={() => handleStoryMode('pashto')}
                        disabled={isProcessing}
                        className="bg-blue-600 text-white px-4 py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all text-sm"
                      >
                        🇦🇫 Pashto Story with 3D Character
                      </button>
                      <button
                        onClick={() => handleStoryMode('english')}
                        disabled={isProcessing}
                        className="bg-purple-600 text-white px-4 py-3 rounded-lg font-semibold hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all text-sm"
                      >
                        🏴󠁧󠁢󠁥󠁮󠁧󠁿 English Story with 3D Character
                      </button>
                    </div>
                  </div>

                  <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
                    <h4 className="font-bold text-sm mb-2">🎭 Story Features:</h4>
                    <ul className="text-sm space-y-1 text-gray-700">
                      <li>• Interactive 3D animated character demonstrates story gestures</li>
                      <li>• Learn Pakistani sign language through classic tales</li>
                      <li>• Available in Urdu, Pashto, and English languages</li>
                      <li>• Educational moral lessons with sign language integration</li>
                      <li>• Story-related gesture vocabulary building</li>
                    </ul>
                  </div>

                  {isProcessing && (
                    <div className="bg-orange-50 border border-orange-200 p-4 rounded-lg text-center">
                      <div className="animate-spin inline-block w-6 h-6 border-4 border-orange-600 border-t-transparent rounded-full mb-2"></div>
                      <p className="text-orange-800 font-medium">🎭 Starting 3D character story demonstration...</p>
                      <p className="text-sm text-orange-600">The animated character will now tell the Pakistani story with sign language gestures!</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Error Display */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mt-6">
                <p className="text-red-800">❌ {error}</p>
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
                <h3 className="text-lg font-bold mb-4">🕒 Recent Real Detections</h3>
                <div className="space-y-3 max-h-64 overflow-y-auto custom-scrollbar">
                  {detectionHistory.map((detection, index) => (
                    <div key={index} className="border-l-4 border-green-500 pl-3 py-2 bg-green-50 rounded-r-lg">
                      <p className="text-xs text-gray-500">{detection.timestamp}</p>
                      <p className="font-semibold capitalize">{detection.gesture.replace('_', ' ')}</p>
                      <p className="text-sm text-gray-600">{detection.meaning}</p>
                      <div className="flex items-center text-xs text-green-600 mt-1">
                        <span>Confidence: {(detection.confidence * 100).toFixed(1)}%</span>
                        {detection.landmarks_detected && <span className="ml-2">✓ Landmarks</span>}
                      </div>
                      <p className="text-xs text-blue-500">{detection.detection_method}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Available Gestures */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-lg font-bold mb-4">📋 Available Gestures ({Object.keys(availableGestures).length})</h3>
              <div className="space-y-2 max-h-96 overflow-y-auto custom-scrollbar">
                {Object.entries(availableGestures).map(([key, gesture]) => (
                  <div key={key} className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                    <p className="font-medium capitalize">{key.replace('_', ' ')}</p>
                    <p className="text-sm text-blue-600 urdu-text">{gesture.urdu}</p>
                    <p className="text-sm text-purple-600 pashto-text">{gesture.pashto}</p>
                    <p className="text-xs text-gray-500">{gesture.meaning}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Performance Stats */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-lg font-bold mb-4">⚡ Technology Performance</h3>
              <div className="space-y-3">
                {stats && (
                  <>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Technology Engine</span>
                      <span className="font-semibold text-green-600">{stats.technology_engine}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Detection Method</span>
                      <span className="font-semibold text-blue-600">{stats.detection_method}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Model Status</span>
                      <span className={`font-semibold ${stats.model_status === 'loaded' ? 'text-green-600' : 'text-red-600'}`}>
                        {stats.model_status === 'loaded' ? '✅ Loaded' : '❌ Not Loaded'}
                      </span>
                    </div>

                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;