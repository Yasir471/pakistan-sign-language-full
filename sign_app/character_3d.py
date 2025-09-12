#!/usr/bin/env python3
"""
3D Animated Character for Pakistani Sign Language
Creates a 3D avatar that performs sign language gestures
"""

import pygame
import numpy as np
import mediapipe as mp
import cv2
import json
import time
import threading
from OpenGL.GL import *
from OpenGL.GLU import *
from pathlib import Path
import math

class SignLanguageCharacter3D:
    def __init__(self, width=800, height=600):
        """Initialize 3D character for sign language animation"""
        self.width = width
        self.height = height
        self.current_gesture = None
        self.animation_progress = 0.0
        self.animation_speed = 2.0
        
        # Initialize Pygame and OpenGL
        pygame.init()
        pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)
        pygame.display.set_caption("Pakistani Sign Language 3D Character")
        
        # Initialize OpenGL
        self.init_opengl()
        
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Character properties
        self.character_pos = [0, 0, -5]  # Character position
        self.head_pos = [0, 1.5, 0]     # Head position relative to character
        self.body_height = 2.0
        self.arm_length = 1.2
        self.hand_size = 0.3
        
        # Load gesture mappings
        self.load_gesture_poses()
        
        # Animation state
        self.is_animating = False
        self.target_left_hand = [0, 0, 0]
        self.target_right_hand = [0, 0, 0]
        self.current_left_hand = [-1.0, 0.5, 0]
        self.current_right_hand = [1.0, 0.5, 0]
        
    def init_opengl(self):
        """Initialize OpenGL settings"""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        
        # Set up perspective projection
        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, (self.width/self.height), 0.1, 50.0)
        
        # Set up lighting
        glLight(GL_LIGHT0, GL_POSITION, [2, 3, 3, 1])
        glLight(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1])
        glLight(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1])
        
        # Material properties
        glMaterial(GL_FRONT, GL_AMBIENT, [0.2, 0.2, 0.2, 1])
        glMaterial(GL_FRONT, GL_DIFFUSE, [0.8, 0.6, 0.4, 1])  # Skin color
        glMaterial(GL_FRONT, GL_SPECULAR, [0.1, 0.1, 0.1, 1])
        glMaterial(GL_FRONT, GL_SHININESS, 10)
        
    def load_gesture_poses(self):
        """Load gesture-to-3D-pose mappings for Pakistani sign language"""
        self.gesture_poses = {
            # Numbers
            'ek': {
                'left_hand': [-0.5, 1.0, 0], 'right_hand': [0.5, 1.0, 0],
                'left_fingers': 'index_up', 'right_fingers': 'fist'
            },
            'do': {
                'left_hand': [-0.5, 1.0, 0], 'right_hand': [0.5, 1.0, 0],
                'left_fingers': 'two_fingers', 'right_fingers': 'fist'
            },
            'teen': {
                'left_hand': [-0.5, 1.0, 0], 'right_hand': [0.5, 1.0, 0],
                'left_fingers': 'three_fingers', 'right_fingers': 'fist'
            },
            'chaar': {
                'left_hand': [-0.5, 1.0, 0], 'right_hand': [0.5, 1.0, 0],
                'left_fingers': 'four_fingers', 'right_fingers': 'fist'
            },
            'paanch': {
                'left_hand': [-0.5, 1.0, 0], 'right_hand': [0.5, 1.0, 0],
                'left_fingers': 'open_hand', 'right_fingers': 'fist'
            },
            
            # Greetings
            'salam': {
                'left_hand': [-0.3, 1.2, 0], 'right_hand': [0.3, 1.2, 0],
                'left_fingers': 'open_hand', 'right_fingers': 'open_hand',
                'wave': True
            },
            'khuda_hafiz': {
                'left_hand': [-0.4, 1.3, 0], 'right_hand': [0.4, 1.3, 0],
                'left_fingers': 'open_hand', 'right_fingers': 'open_hand',
                'wave': True
            },
            'shukriya': {
                'left_hand': [-0.2, 0.8, 0], 'right_hand': [0.2, 0.8, 0],
                'left_fingers': 'open_hand', 'right_fingers': 'open_hand'
            },
            
            # Family
            'ammi': {
                'left_hand': [-0.3, 1.1, 0], 'right_hand': [0.3, 1.1, 0],
                'left_fingers': 'pointing', 'right_fingers': 'heart_shape'
            },
            'abbu': {
                'left_hand': [-0.3, 1.1, 0], 'right_hand': [0.3, 1.1, 0],
                'left_fingers': 'thumbs_up', 'right_fingers': 'pointing'
            },
            'bhai': {
                'left_hand': [-0.4, 1.0, 0], 'right_hand': [0.4, 1.0, 0],
                'left_fingers': 'fist', 'right_fingers': 'fist',
                'gesture_type': 'brotherhood'
            },
            'behn': {
                'left_hand': [-0.3, 1.2, 0], 'right_hand': [0.3, 1.2, 0],
                'left_fingers': 'gentle_wave', 'right_fingers': 'gentle_wave'
            },
            
            # Basic needs
            'paani': {
                'left_hand': [-0.2, 0.9, 0], 'right_hand': [0.2, 0.9, 0],
                'left_fingers': 'cup_shape', 'right_fingers': 'pouring',
                'gesture_type': 'drinking'
            },
            'khana': {
                'left_hand': [-0.2, 0.8, 0], 'right_hand': [0.2, 0.8, 0],
                'left_fingers': 'open_hand', 'right_fingers': 'eating_motion',
                'gesture_type': 'eating'
            },
            'madad': {
                'left_hand': [-0.5, 1.2, 0], 'right_hand': [0.5, 1.2, 0],
                'left_fingers': 'open_hand', 'right_fingers': 'open_hand',
                'gesture_type': 'help_needed'
            },
            
            # Actions
            'reading': {
                'left_hand': [-0.3, 0.9, 0], 'right_hand': [0.3, 0.9, 0],
                'left_fingers': 'book_hold', 'right_fingers': 'page_turn'
            },
            'writing': {
                'left_hand': [-0.2, 0.8, 0], 'right_hand': [0.2, 0.8, 0],
                'left_fingers': 'paper_hold', 'right_fingers': 'pen_grip'
            },
            'listening': {
                'left_hand': [-0.7, 1.1, 0], 'right_hand': [0.7, 1.1, 0],
                'left_fingers': 'cupped_ear', 'right_fingers': 'cupped_ear'
            },
            'speaking': {
                'left_hand': [-0.3, 1.0, 0], 'right_hand': [0.2, 1.0, 0],
                'left_fingers': 'open_hand', 'right_fingers': 'near_mouth'
            },
            
            # Default pose
            'default': {
                'left_hand': [-1.0, 0.5, 0], 'right_hand': [1.0, 0.5, 0],
                'left_fingers': 'relaxed', 'right_fingers': 'relaxed'
            }
        }
        
        # Add all remaining gestures with appropriate poses
        remaining_gestures = [
            'ghar', 'kitab', 'qalam', 'che', 'saat', 'aath', 'nau', 'das',
            'teacher', 'student', 'hospital', 'masjid', 'bazaar', 'dukaan',
            'paise', 'kaam', 'waqt', 'din', 'raat', 'subah', 'shaam',
            'haan', 'nahin', 'accha', 'bura', 'bara', 'chota', 'thanda', 'garam',
            'khushi', 'gham', 'dost', 'dushman', 'mohabbat', 'nafrat',
            'aam', 'kela', 'seb', 'santra', 'angoor', 'doodh', 'chai', 'kahwa',
            'roti', 'chawal', 'gosht', 'machli', 'anda', 'sabzi',
            'gaadi', 'bus', 'train', 'jahaaz', 'cycle', 'rickshaw',
            'sadak', 'pool', 'darya', 'samandar', 'pahad', 'jungle', 'baagh',
            'phool', 'darakht', 'patta', 'suraj', 'chaand', 'sitara',
            'badal', 'baarish', 'hawa', 'aag', 'dhuaan', 'kaagaz', 'pencil',
            'bag', 'table', 'kursi', 'bistar', 'kamra', 'darwaza', 'khidki',
            'deewar', 'chhat', 'zameen', 'seerah', 'lift', 'phone', 'mobile',
            'computer', 'tv', 'radio', 'camera', 'photo', 'video', 'music',
            'game', 'sport', 'football', 'cricket', 'running', 'walking',
            'sitting', 'standing', 'sleeping', 'eating', 'drinking',
            'looking', 'thinking', 'laughing', 'crying', 'school', 'doctor'
        ]
        
        # Assign default or contextual poses to remaining gestures
        for gesture in remaining_gestures:
            if gesture not in self.gesture_poses:
                self.gesture_poses[gesture] = self.gesture_poses['default'].copy()
        
    def animate_to_gesture(self, gesture_name):
        """Start animation to perform a specific gesture"""
        if gesture_name in self.gesture_poses:
            self.current_gesture = gesture_name
            pose = self.gesture_poses[gesture_name]
            
            # Set target positions
            self.target_left_hand = pose['left_hand'].copy()
            self.target_right_hand = pose['right_hand'].copy()
            
            # Start animation
            self.is_animating = True
            self.animation_progress = 0.0
            
            print(f"🎭 Starting animation for gesture: {gesture_name}")
            
    def update_animation(self, dt):
        """Update character animation"""
        if self.is_animating:
            self.animation_progress += dt * self.animation_speed
            
            if self.animation_progress >= 1.0:
                self.animation_progress = 1.0
                self.is_animating = False
                
            # Interpolate hand positions
            t = self.smooth_step(self.animation_progress)
            
            self.current_left_hand = [
                self.lerp(self.current_left_hand[i], self.target_left_hand[i], t)
                for i in range(3)
            ]
            self.current_right_hand = [
                self.lerp(self.current_right_hand[i], self.target_right_hand[i], t)
                for i in range(3)
            ]
            
    def smooth_step(self, t):
        """Smooth step interpolation for natural animation"""
        return t * t * (3.0 - 2.0 * t)
        
    def lerp(self, a, b, t):
        """Linear interpolation"""
        return a + (b - a) * t
        
    def draw_character(self):
        """Draw the 3D character"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Position camera
        gluLookAt(0, 1, 8, 0, 1, 0, 0, 1, 0)
        
        # Apply character transformation
        glTranslatef(*self.character_pos)
        
        # Draw head
        self.draw_head()
        
        # Draw body
        self.draw_body()
        
        # Draw arms and hands
        self.draw_arm_and_hand('left', self.current_left_hand)
        self.draw_arm_and_hand('right', self.current_right_hand)
        
        # Draw legs
        self.draw_legs()
        
        # Add gesture info text
        self.draw_gesture_info()
        
        pygame.display.flip()
        
    def draw_head(self):
        """Draw character head"""
        glPushMatrix()
        glTranslatef(*self.head_pos)
        
        # Head
        glColor3f(0.9, 0.7, 0.5)  # Skin color
        glutSolidSphere(0.25, 20, 20)
        
        # Eyes
        glColor3f(0.0, 0.0, 0.0)
        glPushMatrix()
        glTranslatef(-0.08, 0.05, 0.2)
        glutSolidSphere(0.03, 10, 10)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0.08, 0.05, 0.2)
        glutSolidSphere(0.03, 10, 10)
        glPopMatrix()
        
        # Mouth
        glPushMatrix()
        glTranslatef(0, -0.08, 0.18)
        glScalef(0.08, 0.02, 0.02)
        glutSolidCube(1)
        glPopMatrix()
        
        glPopMatrix()
        
    def draw_body(self):
        """Draw character body"""
        glColor3f(0.2, 0.4, 0.8)  # Shirt color
        glPushMatrix()
        glTranslatef(0, 0.7, 0)
        glScalef(0.6, 1.2, 0.3)
        glutSolidCube(1)
        glPopMatrix()
        
    def draw_arm_and_hand(self, side, hand_pos):
        """Draw arm and hand"""
        sign = -1 if side == 'left' else 1
        
        # Arm
        glColor3f(0.9, 0.7, 0.5)  # Skin color
        glPushMatrix()
        
        shoulder_pos = [sign * 0.4, 1.2, 0]
        glTranslatef(*shoulder_pos)
        
        # Upper arm
        upper_arm_dir = np.array(hand_pos) - np.array(shoulder_pos)
        upper_arm_length = np.linalg.norm(upper_arm_dir) * 0.6
        
        glPushMatrix()
        glRotatef(np.degrees(np.arctan2(upper_arm_dir[1], upper_arm_dir[0])), 0, 0, 1)
        glTranslatef(upper_arm_length/2, 0, 0)
        glScalef(upper_arm_length, 0.08, 0.08)
        glutSolidCube(1)
        glPopMatrix()
        
        # Hand
        glPushMatrix()
        glTranslatef(*(np.array(hand_pos) - np.array(shoulder_pos)))
        self.draw_hand(side)
        glPopMatrix()
        
        glPopMatrix()
        
    def draw_hand(self, side):
        """Draw hand with finger positions"""
        glColor3f(0.9, 0.7, 0.5)
        
        # Palm
        glPushMatrix()
        glScalef(0.15, 0.2, 0.05)
        glutSolidCube(1)
        glPopMatrix()
        
        # Fingers (simplified)
        finger_positions = [
            [-0.06, 0.12, 0], [-0.02, 0.15, 0], [0.02, 0.15, 0], 
            [0.06, 0.12, 0], [0.1, 0.05, 0]  # Thumb
        ]
        
        for i, pos in enumerate(finger_positions):
            glPushMatrix()
            glTranslatef(*pos)
            glScalef(0.02, 0.08, 0.02)
            glutSolidCube(1)
            glPopMatrix()
            
    def draw_legs(self):
        """Draw character legs"""
        glColor3f(0.1, 0.1, 0.4)  # Pants color
        
        # Left leg
        glPushMatrix()
        glTranslatef(-0.2, -0.5, 0)
        glScalef(0.2, 1.5, 0.2)
        glutSolidCube(1)
        glPopMatrix()
        
        # Right leg
        glPushMatrix()
        glTranslatef(0.2, -0.5, 0)
        glScalef(0.2, 1.5, 0.2)
        glutSolidCube(1)
        glPopMatrix()
        
    def draw_gesture_info(self):
        """Draw gesture information"""
        if self.current_gesture:
            # This would typically use text rendering
            # For now, we'll indicate the current gesture with color changes
            pass
            
    def run_animation_loop(self, gesture_name, duration=3.0):
        """Run the animation loop for a specific gesture"""
        self.animate_to_gesture(gesture_name)
        
        clock = pygame.time.Clock()
        start_time = time.time()
        
        while time.time() - start_time < duration:
            dt = clock.tick(60) / 1000.0  # Delta time in seconds
            
            # Handle pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                    
            # Update animation
            self.update_animation(dt)
            
            # Draw character
            self.draw_character()
            
        # Hold the final pose briefly
        time.sleep(0.5)
        
        # Return to default pose
        self.animate_to_gesture('default')
        for _ in range(30):  # 0.5 seconds at 60 FPS
            dt = clock.tick(60) / 1000.0
            self.update_animation(dt)
            self.draw_character()
            
    def cleanup(self):
        """Clean up resources"""
        pygame.quit()

def demo_character():
    """Demo function to test the 3D character"""
    character = SignLanguageCharacter3D()
    
    # Demo gestures
    demo_gestures = [
        'salam', 'shukriya', 'khuda_hafiz', 
        'ek', 'do', 'teen', 'chaar', 'paanch',
        'paani', 'khana', 'madad'
    ]
    
    try:
        for gesture in demo_gestures:
            print(f"🎭 Demonstrating: {gesture}")
            character.run_animation_loop(gesture, 2.0)
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped by user")
    finally:
        character.cleanup()

if __name__ == "__main__":
    print("🎭 Starting 3D Character Demo...")
    print("📱 This will show various Pakistani sign language gestures")
    print("❌ Press Ctrl+C to exit")
    demo_character()