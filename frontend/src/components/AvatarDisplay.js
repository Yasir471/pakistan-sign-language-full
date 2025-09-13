import React, { useRef, useEffect, useState } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Text, OrbitControls } from '@react-three/drei';
import * as THREE from 'three';

// 3D Avatar Component
const SignLanguageAvatar = ({ currentGesture, isAnimating }) => {
  const avatarRef = useRef();
  const leftArmRef = useRef();
  const rightArmRef = useRef();
  const leftHandRef = useRef();
  const rightHandRef = useRef();
  const headRef = useRef();
  const [animationProgress, setAnimationProgress] = useState(0);

  // Debug logging to trace prop changes
  useEffect(() => {
    console.log('🎭 SIGNLANGUAGEAVATAR PROPS CHANGED:', {
      currentGesture,
      isAnimating,
      timestamp: new Date().toISOString()
    });
  }, [currentGesture, isAnimating]);

  // Gesture pose definitions for Pakistani Sign Language
  const gesturePoses = {
    'default': {
      leftArm: { rotation: [0, 0, 0.3], position: [-1.2, 0, 0] },
      rightArm: { rotation: [0, 0, -0.3], position: [1.2, 0, 0] },
      leftHand: { rotation: [0, 0, 0], fingers: 'relaxed' },
      rightHand: { rotation: [0, 0, 0], fingers: 'relaxed' }
    },
    'salam': {
      leftArm: { rotation: [0, 0, 1.2], position: [-0.8, 0.5, 0] },
      rightArm: { rotation: [0, 0, -1.2], position: [0.8, 0.5, 0] },
      leftHand: { rotation: [0, 0, 0.2], fingers: 'open' },
      rightHand: { rotation: [0, 0, -0.2], fingers: 'open' },
      wave: true
    },
    'shukriya': {
      leftArm: { rotation: [0, 0, 0.8], position: [-0.6, 0.3, 0] },
      rightArm: { rotation: [0, 0, -0.8], position: [0.6, 0.3, 0] },
      leftHand: { rotation: [0, 0, 0.1], fingers: 'open' },
      rightHand: { rotation: [0, 0, -0.1], fingers: 'open' }
    },
    'paani': {
      leftArm: { rotation: [0, 0, 0.6], position: [-0.4, 0.2, 0] },
      rightArm: { rotation: [-0.5, 0, -0.6], position: [0.4, 0.4, 0] },
      leftHand: { rotation: [0, 0, 0], fingers: 'cup' },
      rightHand: { rotation: [0.3, 0, 0], fingers: 'pour' }
    },
    'khana': {
      leftArm: { rotation: [0, 0, 0.4], position: [-0.3, 0.1, 0] },
      rightArm: { rotation: [-0.8, 0, -0.4], position: [0.3, 0.3, 0] },
      leftHand: { rotation: [0, 0, 0], fingers: 'open' },
      rightHand: { rotation: [0.5, 0, 0], fingers: 'eating' }
    },
    'ek': {
      leftArm: { rotation: [0, 0, 0.8], position: [-0.5, 0.4, 0] },
      rightArm: { rotation: [0, 0, -0.3], position: [1.0, 0, 0] },
      leftHand: { rotation: [0, 0, 0], fingers: 'one' },
      rightHand: { rotation: [0, 0, 0], fingers: 'fist' }
    },
    'do': {
      leftArm: { rotation: [0, 0, 0.8], position: [-0.5, 0.4, 0] },
      rightArm: { rotation: [0, 0, -0.3], position: [1.0, 0, 0] },
      leftHand: { rotation: [0, 0, 0], fingers: 'two' },
      rightHand: { rotation: [0, 0, 0], fingers: 'fist' }
    },
    'teen': {
      leftArm: { rotation: [0, 0, 0.8], position: [-0.5, 0.4, 0] },
      rightArm: { rotation: [0, 0, -0.3], position: [1.0, 0, 0] },
      leftHand: { rotation: [0, 0, 0], fingers: 'three' },
      rightHand: { rotation: [0, 0, 0], fingers: 'fist' }
    }
  };

  // Animation loop
  useFrame((state, delta) => {
    // Always log the useFrame execution to see if it's running
    if (isAnimating) {
      console.log('🔄 USEFRAME EXECUTING:', {
        currentGesture,
        isAnimating,
        animationProgress,
        delta,
        hasGesture: !!gesturePoses[currentGesture],
        leftArmExists: !!leftArmRef.current,
        rightArmExists: !!rightArmRef.current
      });
    }
    
    if (isAnimating && currentGesture && gesturePoses[currentGesture]) {
      console.log('✅ ANIMATION CONDITIONS MET - Processing frame');
      
      // Update animation progress (hold at 1.0 when reached, don't reset)
      setAnimationProgress(prev => {
        const newProgress = prev + delta * 3; // Faster transition
        const clampedProgress = Math.min(newProgress, 1.0);
        if (prev !== clampedProgress) {
          console.log('📊 Animation progress updated:', prev, '→', clampedProgress);
        }
        return clampedProgress;
      });

      // Apply gesture poses with smooth transition to final position
      const gesture = gesturePoses[currentGesture];
      const t = Math.min(animationProgress, 1.0); // Simple linear interpolation to final pose

      console.log('🎯 APPLYING GESTURE POSE:', {
        gestureName: currentGesture,
        progress: t,
        gesture: gesture
      });

      // Animate arms to gesture position and hold
      if (leftArmRef.current && gesture.leftArm) {
        const newRotationZ = THREE.MathUtils.lerp(0.3, gesture.leftArm.rotation[2], t);
        const newPositionY = THREE.MathUtils.lerp(0, gesture.leftArm.position[1], t);
        
        leftArmRef.current.rotation.x = THREE.MathUtils.lerp(0, gesture.leftArm.rotation[0], t);
        leftArmRef.current.rotation.y = THREE.MathUtils.lerp(0, gesture.leftArm.rotation[1], t);
        leftArmRef.current.rotation.z = newRotationZ;
        leftArmRef.current.position.x = THREE.MathUtils.lerp(-1.2, gesture.leftArm.position[0], t);
        leftArmRef.current.position.y = newPositionY;
        
        console.log('👈 LEFT ARM UPDATED:', {
          rotationZ: newRotationZ,
          positionY: newPositionY,
          progress: t
        });
      }

      if (rightArmRef.current && gesture.rightArm) {
        const newRotationZ = THREE.MathUtils.lerp(-0.3, gesture.rightArm.rotation[2], t);
        const newPositionY = THREE.MathUtils.lerp(0, gesture.rightArm.position[1], t);
        
        rightArmRef.current.rotation.x = THREE.MathUtils.lerp(0, gesture.rightArm.rotation[0], t);
        rightArmRef.current.rotation.y = THREE.MathUtils.lerp(0, gesture.rightArm.rotation[1], t);
        rightArmRef.current.rotation.z = newRotationZ;
        rightArmRef.current.position.x = THREE.MathUtils.lerp(1.2, gesture.rightArm.position[0], t);
        rightArmRef.current.position.y = newPositionY;
        
        console.log('👉 RIGHT ARM UPDATED:', {
          rotationZ: newRotationZ,
          positionY: newPositionY,
          progress: t
        });
      }

      // Special waving animation for greetings (only if fully transitioned)
      if (gesture.wave && headRef.current && t >= 1.0) {
        headRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 3) * 0.1;
        console.log('👋 WAVE ANIMATION APPLIED');
      }
    } else if (!isAnimating && animationProgress > 0) {
      console.log('🔄 RETURNING TO DEFAULT POSE');
      
      // Reset animation progress and return to default pose
      setAnimationProgress(0);
      
      // Return to default pose smoothly
      const defaultGesture = gesturePoses['default'];
      if (leftArmRef.current && defaultGesture.leftArm) {
        leftArmRef.current.rotation.x = THREE.MathUtils.lerp(leftArmRef.current.rotation.x, 0, 0.1);
        leftArmRef.current.rotation.y = THREE.MathUtils.lerp(leftArmRef.current.rotation.y, 0, 0.1);
        leftArmRef.current.rotation.z = THREE.MathUtils.lerp(leftArmRef.current.rotation.z, 0.3, 0.1);
        leftArmRef.current.position.x = THREE.MathUtils.lerp(leftArmRef.current.position.x, -1.2, 0.1);
        leftArmRef.current.position.y = THREE.MathUtils.lerp(leftArmRef.current.position.y, 0, 0.1);
      }
      if (rightArmRef.current && defaultGesture.rightArm) {
        rightArmRef.current.rotation.x = THREE.MathUtils.lerp(rightArmRef.current.rotation.x, 0, 0.1);
        rightArmRef.current.rotation.y = THREE.MathUtils.lerp(rightArmRef.current.rotation.y, 0, 0.1);
        rightArmRef.current.rotation.z = THREE.MathUtils.lerp(rightArmRef.current.rotation.z, -0.3, 0.1);
        rightArmRef.current.position.x = THREE.MathUtils.lerp(rightArmRef.current.position.x, 1.2, 0.1);
        rightArmRef.current.position.y = THREE.MathUtils.lerp(rightArmRef.current.position.y, 0, 0.1);
      }
      
      // Reset head rotation
      if (headRef.current) {
        headRef.current.rotation.y = THREE.MathUtils.lerp(headRef.current.rotation.y, 0, 0.1);
      }
    }
  });

  return (
    <group ref={avatarRef}>
      {/* Head */}
      <group ref={headRef} position={[0, 2.5, 0]}>
        <mesh>
          <sphereGeometry args={[0.3, 16, 16]} />
          <meshStandardMaterial color="#DCAA7B" />
        </mesh>
        {/* Eyes */}
        <mesh position={[-0.1, 0.05, 0.25]}>
          <sphereGeometry args={[0.03, 8, 8]} />
          <meshStandardMaterial color="#000" />
        </mesh>
        <mesh position={[0.1, 0.05, 0.25]}>
          <sphereGeometry args={[0.03, 8, 8]} />
          <meshStandardMaterial color="#000" />
        </mesh>
        {/* Mouth */}
        <mesh position={[0, -0.08, 0.25]} rotation={[0, 0, 0]}>
          <cylinderGeometry args={[0.05, 0.05, 0.02, 8]} />
          <meshStandardMaterial color="#8B4513" />
        </mesh>
      </group>

      {/* Body */}
      <mesh position={[0, 1.5, 0]}>
        <cylinderGeometry args={[0.4, 0.5, 1.5, 8]} />
        <meshStandardMaterial color="#4A90E2" />
      </mesh>

      {/* Left Arm */}
      <group ref={leftArmRef} position={[-1.2, 2, 0]}>
        {/* Upper Arm */}
        <mesh position={[0, -0.3, 0]}>
          <cylinderGeometry args={[0.08, 0.1, 0.6, 8]} />
          <meshStandardMaterial color="#DCAA7B" />
        </mesh>
        {/* Forearm */}
        <mesh position={[0, -0.8, 0]}>
          <cylinderGeometry args={[0.06, 0.08, 0.5, 8]} />
          <meshStandardMaterial color="#DCAA7B" />
        </mesh>
        {/* Left Hand */}
        <group ref={leftHandRef} position={[0, -1.2, 0]}>
          <Hand gesture={currentGesture} side="left" />
        </group>
      </group>

      {/* Right Arm */}
      <group ref={rightArmRef} position={[1.2, 2, 0]}>
        {/* Upper Arm */}
        <mesh position={[0, -0.3, 0]}>
          <cylinderGeometry args={[0.08, 0.1, 0.6, 8]} />
          <meshStandardMaterial color="#DCAA7B" />
        </mesh>
        {/* Forearm */}
        <mesh position={[0, -0.8, 0]}>
          <cylinderGeometry args={[0.06, 0.08, 0.5, 8]} />
          <meshStandardMaterial color="#DCAA7B" />
        </mesh>
        {/* Right Hand */}
        <group ref={rightHandRef} position={[0, -1.2, 0]}>
          <Hand gesture={currentGesture} side="right" />
        </group>
      </group>

      {/* Legs */}
      <mesh position={[-0.2, 0.5, 0]}>
        <cylinderGeometry args={[0.12, 0.15, 1, 8]} />
        <meshStandardMaterial color="#2C3E50" />
      </mesh>
      <mesh position={[0.2, 0.5, 0]}>
        <cylinderGeometry args={[0.12, 0.15, 1, 8]} />
        <meshStandardMaterial color="#2C3E50" />
      </mesh>

      {/* Feet */}
      <mesh position={[-0.2, -0.1, 0.1]}>
        <boxGeometry args={[0.15, 0.1, 0.25]} />
        <meshStandardMaterial color="#000" />
      </mesh>
      <mesh position={[0.2, -0.1, 0.1]}>
        <boxGeometry args={[0.15, 0.1, 0.25]} />
        <meshStandardMaterial color="#000" />
      </mesh>
    </group>
  );
};

// Hand Component with finger gestures
const Hand = ({ gesture, side }) => {
  const handRef = useRef();

  const fingerConfigs = {
    'relaxed': { spread: 0.1, curl: 0.3 },
    'open': { spread: 0.2, curl: 0 },
    'fist': { spread: 0, curl: 1 },
    'one': { spread: 0.1, curl: 0.8, index: true },
    'two': { spread: 0.15, curl: 0.8, index: true, middle: true },
    'three': { spread: 0.15, curl: 0.8, index: true, middle: true, ring: true },
    'cup': { spread: 0.05, curl: 0.4 },
    'pour': { spread: 0.1, curl: 0.2 },
    'eating': { spread: 0.08, curl: 0.5 }
  };

  const getFingerConfig = () => {
    const poses = {
      'salam': 'open',
      'shukriya': 'open', 
      'paani': side === 'left' ? 'cup' : 'pour',
      'khana': side === 'left' ? 'open' : 'eating',
      'ek': side === 'left' ? 'one' : 'fist',
      'do': side === 'left' ? 'two' : 'fist',
      'teen': side === 'left' ? 'three' : 'fist'
    };
    return fingerConfigs[poses[gesture]] || fingerConfigs['relaxed'];
  };

  const config = getFingerConfig();

  return (
    <group ref={handRef}>
      {/* Palm */}
      <mesh>
        <boxGeometry args={[0.15, 0.08, 0.2]} />
        <meshStandardMaterial color="#DCAA7B" />
      </mesh>
      
      {/* Fingers */}
      {[0, 1, 2, 3].map(i => (
        <group key={i} position={[(-0.06 + i * 0.04), 0, 0.12]}>
          {/* Finger segments */}
          <mesh position={[0, 0, 0.04]} rotation={[config.curl * 0.5, 0, config.spread * (i - 1.5)]}>
            <cylinderGeometry args={[0.015, 0.02, 0.08, 6]} />
            <meshStandardMaterial color="#DCAA7B" />
          </mesh>
          <mesh position={[0, 0, 0.08]} rotation={[config.curl, 0, config.spread * (i - 1.5)]}>
            <cylinderGeometry args={[0.01, 0.015, 0.06, 6]} />
            <meshStandardMaterial color="#DCAA7B" />
          </mesh>
        </group>
      ))}
      
      {/* Thumb */}
      <group position={[0.08, 0, 0.05]} rotation={[0, 0, side === 'left' ? 0.5 : -0.5]}>
        <mesh>
          <cylinderGeometry args={[0.015, 0.02, 0.07, 6]} />
          <meshStandardMaterial color="#DCAA7B" />
        </mesh>
      </group>
    </group>
  );
};

// Main Avatar Display Component
const AvatarDisplay = ({ currentGesture, isAnimating, gestureInfo }) => {
  return (
    <div className="bg-gradient-to-b from-blue-50 to-indigo-100 rounded-lg p-4 h-96 relative overflow-hidden shadow-lg border-2 border-blue-200">
      {/* 3D Canvas */}
      <Canvas
        camera={{ position: [0, 2, 8], fov: 45 }}
        style={{ width: '100%', height: '100%' }}
        gl={{ antialias: true, alpha: true }}
      >
        {/* Lighting */}
        <ambientLight intensity={0.6} />
        <directionalLight position={[10, 10, 5]} intensity={0.8} />
        <directionalLight position={[-10, 10, 5]} intensity={0.4} />

        {/* 3D Avatar */}
        <SignLanguageAvatar currentGesture={currentGesture} isAnimating={isAnimating} />

        {/* Camera Controls */}
        <OrbitControls 
          enablePan={false} 
          enableZoom={true} 
          enableRotate={true}
          maxPolarAngle={Math.PI / 2}
          minDistance={5}
          maxDistance={12}
        />

        {/* Background */}
        <mesh position={[0, 0, -5]} scale={[20, 20, 1]}>
          <planeGeometry />
          <meshBasicMaterial color="#E3F2FD" transparent opacity={0.3} />
        </mesh>
      </Canvas>

      {/* Gesture Info Overlay */}
      <div className="absolute top-4 left-4 bg-white bg-opacity-90 rounded-lg p-3 shadow-md">
        <div className="text-sm font-semibold text-gray-800">
          {isAnimating ? '🎭 Animating' : '👤 Avatar Ready'}
        </div>
        {gestureInfo && (
          <div className="mt-1">
            <div className="text-xs text-gray-600">Gesture: <span className="font-medium">{gestureInfo.name}</span></div>
            <div className="text-xs text-gray-600">Meaning: <span className="font-medium">{gestureInfo.meaning}</span></div>
          </div>
        )}
      </div>

      {/* Pakistani Flag */}
      <div className="absolute top-4 right-4 flex items-center space-x-1">
        <div className="w-4 h-3 bg-green-600 rounded-sm"></div>
        <div className="w-1 h-3 bg-white rounded-sm"></div>
        <span className="text-xs text-gray-600">🇵🇰 Pakistani SL</span>
      </div>
    </div>
  );
};

export default AvatarDisplay;