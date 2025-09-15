import React, { useRef, useEffect, useState } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Text, OrbitControls } from '@react-three/drei';
import * as THREE from 'three';

// Enhanced 3D Avatar Component based on User's Character Design
const SignLanguageAvatar = ({ currentGesture, isAnimating }) => {
  const avatarRef = useRef();
  const leftArmRef = useRef();
  const rightArmRef = useRef();
  const leftHandRef = useRef();
  const rightHandRef = useRef();
  const headRef = useRef();
  const [animationProgress, setAnimationProgress] = useState(0);
  
  // Use refs to maintain current state values for useFrame
  const currentGestureRef = useRef(currentGesture);
  const isAnimatingRef = useRef(isAnimating);
  
  // Update refs when props change
  useEffect(() => {
    currentGestureRef.current = currentGesture;
    isAnimatingRef.current = isAnimating;
    
    // Force reset animation progress when starting new animation
    if (isAnimating && currentGesture && currentGesture !== 'default') {
      setAnimationProgress(0);
    }
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

  // Animation loop using refs for stable state access
  useFrame((state, delta) => {
    const gesture = currentGestureRef.current;
    const animating = isAnimatingRef.current;
    
    if (animating && gesture && gesturePoses[gesture] && gesture !== 'default') {
      // Update animation progress
      setAnimationProgress(prev => {
        const newProgress = prev + delta * 3;
        return Math.min(newProgress, 1.0);
      });

      // Get current gesture pose
      const gestureData = gesturePoses[gesture];
      const t = Math.min(animationProgress, 1.0);

      // Animate arms to gesture position
      if (leftArmRef.current && gestureData.leftArm) {
        leftArmRef.current.rotation.x = THREE.MathUtils.lerp(0, gestureData.leftArm.rotation[0], t);
        leftArmRef.current.rotation.y = THREE.MathUtils.lerp(0, gestureData.leftArm.rotation[1], t);
        leftArmRef.current.rotation.z = THREE.MathUtils.lerp(0.3, gestureData.leftArm.rotation[2], t);
        leftArmRef.current.position.x = THREE.MathUtils.lerp(-1.2, gestureData.leftArm.position[0], t);
        leftArmRef.current.position.y = THREE.MathUtils.lerp(0, gestureData.leftArm.position[1], t);
        
        // Force matrix update
        leftArmRef.current.updateMatrixWorld();
      }

      if (rightArmRef.current && gestureData.rightArm) {
        rightArmRef.current.rotation.x = THREE.MathUtils.lerp(0, gestureData.rightArm.rotation[0], t);
        rightArmRef.current.rotation.y = THREE.MathUtils.lerp(0, gestureData.rightArm.rotation[1], t);
        rightArmRef.current.rotation.z = THREE.MathUtils.lerp(-0.3, gestureData.rightArm.rotation[2], t);
        rightArmRef.current.position.x = THREE.MathUtils.lerp(1.2, gestureData.rightArm.position[0], t);
        rightArmRef.current.position.y = THREE.MathUtils.lerp(0, gestureData.rightArm.position[1], t);
        
        // Force matrix update
        rightArmRef.current.updateMatrixWorld();
      }

      // Special waving animation for greetings
      if (gestureData.wave && headRef.current && t >= 1.0) {
        headRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 3) * 0.1;
        headRef.current.updateMatrixWorld();
      }
    } else if (!animating && animationProgress > 0) {
      // Return to default pose
      setAnimationProgress(0);
      
      if (leftArmRef.current) {
        leftArmRef.current.rotation.x = THREE.MathUtils.lerp(leftArmRef.current.rotation.x, 0, 0.1);
        leftArmRef.current.rotation.y = THREE.MathUtils.lerp(leftArmRef.current.rotation.y, 0, 0.1);
        leftArmRef.current.rotation.z = THREE.MathUtils.lerp(leftArmRef.current.rotation.z, 0.3, 0.1);
        leftArmRef.current.position.x = THREE.MathUtils.lerp(leftArmRef.current.position.x, -1.2, 0.1);
        leftArmRef.current.position.y = THREE.MathUtils.lerp(leftArmRef.current.position.y, 0, 0.1);
        leftArmRef.current.updateMatrixWorld();
      }
      
      if (rightArmRef.current) {
        rightArmRef.current.rotation.x = THREE.MathUtils.lerp(rightArmRef.current.rotation.x, 0, 0.1);
        rightArmRef.current.rotation.y = THREE.MathUtils.lerp(rightArmRef.current.rotation.y, 0, 0.1);
        rightArmRef.current.rotation.z = THREE.MathUtils.lerp(rightArmRef.current.rotation.z, -0.3, 0.1);
        rightArmRef.current.position.x = THREE.MathUtils.lerp(rightArmRef.current.position.x, 1.2, 0.1);
        rightArmRef.current.position.y = THREE.MathUtils.lerp(rightArmRef.current.position.y, 0, 0.1);
        rightArmRef.current.updateMatrixWorld();
      }
      
      if (headRef.current) {
        headRef.current.rotation.y = THREE.MathUtils.lerp(headRef.current.rotation.y, 0, 0.1);
        headRef.current.updateMatrixWorld();
      }
    }
  });

  return (
    <group ref={avatarRef}>
      {/* Enhanced Head - matching uploaded character */}
      <group ref={headRef} position={[0, 2.5, 0]}>
        {/* Face with skin tone matching uploaded character */}
        <mesh>
          <sphereGeometry args={[0.35, 20, 20]} />
          <meshStandardMaterial 
            color="#F4C2A1" 
            roughness={0.6}
            metalness={0.1}
          />
        </mesh>
        
        {/* Eyes */}
        <mesh position={[-0.12, 0.08, 0.28]}>
          <sphereGeometry args={[0.04, 8, 8]} />
          <meshStandardMaterial color="#2C3E50" />
        </mesh>
        <mesh position={[0.12, 0.08, 0.28]}>
          <sphereGeometry args={[0.04, 8, 8]} />
          <meshStandardMaterial color="#2C3E50" />
        </mesh>
        
        {/* Glasses - matching the uploaded character */}
        <group position={[0, 0.08, 0.32]}>
          {/* Left lens */}
          <mesh position={[-0.12, 0, 0]}>
            <ringGeometry args={[0.08, 0.11, 16]} />
            <meshStandardMaterial color="#2C3E50" transparent opacity={0.8} />
          </mesh>
          {/* Right lens */}
          <mesh position={[0.12, 0, 0]}>
            <ringGeometry args={[0.08, 0.11, 16]} />
            <meshStandardMaterial color="#2C3E50" transparent opacity={0.8} />
          </mesh>
          {/* Bridge */}
          <mesh position={[0, 0, 0]} scale={[0.24, 0.02, 0.02]}>
            <boxGeometry />
            <meshStandardMaterial color="#2C3E50" />
          </mesh>
          {/* Left temple */}
          <mesh position={[-0.2, 0, -0.1]} rotation={[0, -0.3, 0]} scale={[0.15, 0.02, 0.02]}>
            <boxGeometry />
            <meshStandardMaterial color="#2C3E50" />
          </mesh>
          {/* Right temple */}
          <mesh position={[0.2, 0, -0.1]} rotation={[0, 0.3, 0]} scale={[0.15, 0.02, 0.02]}>
            <boxGeometry />
            <meshStandardMaterial color="#2C3E50" />
          </mesh>
        </group>
        
        {/* Hair - dark brown/black like the character */}
        <mesh position={[0, 0.15, -0.05]}>
          <sphereGeometry args={[0.38, 16, 10, 0, Math.PI * 2, 0, Math.PI * 0.7]} />
          <meshStandardMaterial color="#2C3E50" roughness={0.8} />
        </mesh>
        
        {/* Mouth */}
        <mesh position={[0, -0.1, 0.28]} rotation={[Math.PI/2, 0, 0]}>
          <cylinderGeometry args={[0.03, 0.03, 0.02, 8]} />
          <meshStandardMaterial color="#CD5C5C" />
        </mesh>
      </group>

      {/* Enhanced Body - Professional attire like uploaded character */}
      <group position={[0, 1.5, 0]}>
        {/* Torso - Light colored shirt */}
        <mesh>
          <cylinderGeometry args={[0.45, 0.55, 1.6, 12]} />
          <meshStandardMaterial 
            color="#F8F8FF" 
            roughness={0.5}
          />
        </mesh>
        
        {/* Light Blue Tie - matching the uploaded character */}
        <mesh position={[0, 0.2, 0.52]} scale={[1, 1.8, 1]}>
          <boxGeometry args={[0.12, 0.7, 0.03]} />
          <meshStandardMaterial 
            color="#87CEEB" 
            roughness={0.4}
            metalness={0.1}
          />
        </mesh>
        
        {/* Shirt Collar */}
        <group position={[0, 0.6, 0.45]}>
          <mesh position={[-0.15, 0, 0]} rotation={[0.3, 0.2, 0]}>
            <boxGeometry args={[0.25, 0.2, 0.05]} />
            <meshStandardMaterial color="#FFFFFF" roughness={0.3} />
          </mesh>
          <mesh position={[0.15, 0, 0]} rotation={[0.3, -0.2, 0]}>
            <boxGeometry args={[0.25, 0.2, 0.05]} />
            <meshStandardMaterial color="#FFFFFF" roughness={0.3} />
          </mesh>
        </group>
        
        {/* Shirt buttons */}
        <mesh position={[0, 0.3, 0.53]}>
          <cylinderGeometry args={[0.02, 0.02, 0.01, 8]} />
          <meshStandardMaterial color="#E0E0E0" />
        </mesh>
        <mesh position={[0, 0.1, 0.53]}>
          <cylinderGeometry args={[0.02, 0.02, 0.01, 8]} />
          <meshStandardMaterial color="#E0E0E0" />
        </mesh>
        <mesh position={[0, -0.1, 0.53]}>
          <cylinderGeometry args={[0.02, 0.02, 0.01, 8]} />
          <meshStandardMaterial color="#E0E0E0" />
        </mesh>
      </group>

      {/* Enhanced Left Arm - Light shirt sleeves */}
      <group ref={leftArmRef} position={[-1.2, 2, 0]}>
        {/* Upper Arm with shirt sleeve */}
        <mesh position={[0, -0.3, 0]}>
          <cylinderGeometry args={[0.09, 0.11, 0.7, 10]} />
          <meshStandardMaterial color="#F8F8FF" roughness={0.5} />
        </mesh>
        {/* Forearm - skin showing */}
        <mesh position={[0, -0.9, 0]}>
          <cylinderGeometry args={[0.07, 0.09, 0.6, 10]} />
          <meshStandardMaterial color="#F4C2A1" roughness={0.6} />
        </mesh>
        {/* Left Hand */}
        <group ref={leftHandRef} position={[0, -1.3, 0]}>
          <Hand gesture={currentGesture} side="left" />
        </group>
      </group>

      {/* Enhanced Right Arm - Light shirt sleeves */}
      <group ref={rightArmRef} position={[1.2, 2, 0]}>
        {/* Upper Arm with shirt sleeve */}
        <mesh position={[0, -0.3, 0]}>
          <cylinderGeometry args={[0.09, 0.11, 0.7, 10]} />
          <meshStandardMaterial color="#F8F8FF" roughness={0.5} />
        </mesh>
        {/* Forearm - skin showing */}
        <mesh position={[0, -0.9, 0]}>
          <cylinderGeometry args={[0.07, 0.09, 0.6, 10]} />
          <meshStandardMaterial color="#F4C2A1" roughness={0.6} />
        </mesh>
        {/* Right Hand */}
        <group ref={rightHandRef} position={[0, -1.3, 0]}>
          <Hand gesture={currentGesture} side="right" />
        </group>
      </group>

      {/* Enhanced Legs - Dark pants matching the character */}
      <group position={[0, 0.5, 0]}>
        <mesh position={[-0.22, 0, 0]}>
          <cylinderGeometry args={[0.14, 0.16, 1.2, 10]} />
          <meshStandardMaterial 
            color="#2C3E50" 
            roughness={0.7}
          />
        </mesh>
        <mesh position={[0.22, 0, 0]}>
          <cylinderGeometry args={[0.14, 0.16, 1.2, 10]} />
          <meshStandardMaterial 
            color="#2C3E50" 
            roughness={0.7}
          />
        </mesh>
      </group>

      {/* Enhanced Shoes - Professional black shoes */}
      <mesh position={[-0.22, -0.15, 0.12]}>
        <boxGeometry args={[0.18, 0.12, 0.32]} />
        <meshStandardMaterial 
          color="#1B2631" 
          roughness={0.2}
          metalness={0.3}
        />
      </mesh>
      <mesh position={[0.22, -0.15, 0.12]}>
        <boxGeometry args={[0.18, 0.12, 0.32]} />
        <meshStandardMaterial 
          color="#1B2631" 
          roughness={0.2}
          metalness={0.3}
        />
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
        <sphereGeometry args={[0.08, 8, 8]} />
        <meshStandardMaterial color="#F4C2A1" roughness={0.7} />
      </mesh>
      
      {/* Fingers based on gesture configuration */}
      {/* Thumb */}
      <mesh 
        position={side === 'left' ? [-0.06, 0.02, 0.06] : [0.06, 0.02, 0.06]} 
        rotation={[0, 0, side === 'left' ? -config.spread : config.spread]}
      >
        <cylinderGeometry args={[0.015, 0.02, 0.05, 6]} />
        <meshStandardMaterial color="#F4C2A1" roughness={0.7} />
      </mesh>
      
      {/* Index Finger */}
      <mesh 
        position={[0, 0.08, 0]} 
        rotation={[config.index ? -config.curl : -config.curl * 0.5, 0, 0]}
      >
        <cylinderGeometry args={[0.012, 0.015, 0.06, 6]} />
        <meshStandardMaterial color="#F4C2A1" roughness={0.7} />
      </mesh>
      
      {/* Middle Finger */}
      <mesh 
        position={[0.02, 0.08, 0]} 
        rotation={[config.middle ? -config.curl : -config.curl * 0.7, 0, 0]}
      >
        <cylinderGeometry args={[0.01, 0.013, 0.07, 6]} />
        <meshStandardMaterial color="#F4C2A1" roughness={0.7} />
      </mesh>
      
      {/* Ring Finger */}
      <mesh 
        position={[0.04, 0.07, 0]} 
        rotation={[config.ring ? -config.curl : -config.curl * 0.8, 0, 0]}
      >
        <cylinderGeometry args={[0.009, 0.012, 0.06, 6]} />
        <meshStandardMaterial color="#F4C2A1" roughness={0.7} />
      </mesh>
      
      {/* Pinky */}
      <mesh 
        position={[0.055, 0.05, 0]} 
        rotation={[-config.curl * 0.9, 0, 0]}
      >
        <cylinderGeometry args={[0.008, 0.01, 0.05, 6]} />
        <meshStandardMaterial color="#F4C2A1" roughness={0.7} />
      </mesh>
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