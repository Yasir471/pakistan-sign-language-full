#!/usr/bin/env python3
"""
3D-Style Animated Character for Pakistani Sign Language
Creates an animated avatar that performs sign language gestures using 2D graphics with 3D effects
"""

import pygame
import numpy as np
import cv2
import json
import time
import threading
import math
from pathlib import Path

class SignLanguageCharacter:
    def __init__(self, width=800, height=600):
        """Initialize animated character for sign language"""
        self.width = width
        self.height = height
        self.current_gesture = None
        self.animation_progress = 0.0
        self.animation_speed = 2.0
        
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Pakistani Sign Language Character")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Character properties
        self.character_pos = [width // 2, height // 2]
        self.head_radius = 60
        self.body_height = 200
        self.arm_length = 120
        self.hand_size = 25
        
        # Colors
        self.skin_color = (220, 180, 130)
        self.shirt_color = (70, 130, 200)
        self.pants_color = (50, 50, 100)
        self.hair_color = (60, 40, 20)
        
        # Load gesture mappings
        self.load_gesture_poses()
        
        # Animation state
        self.is_animating = False
        self.target_left_hand = [0, 0]
        self.target_right_hand = [0, 0]
        self.current_left_hand = [-80, 20]
        self.current_right_hand = [80, 20]
        self.current_left_fingers = "relaxed"
        self.current_right_fingers = "relaxed"
        self.target_left_fingers = "relaxed"
        self.target_right_fingers = "relaxed"
        
    def load_gesture_poses(self):
        """Load gesture-to-pose mappings for Pakistani sign language"""
        self.gesture_poses = {
            # Numbers
            'ek': {
                'left_hand': [-60, -40], 'right_hand': [60, -40],
                'left_fingers': 'index_up', 'right_fingers': 'fist'
            },
            'do': {
                'left_hand': [-60, -40], 'right_hand': [60, -40],
                'left_fingers': 'two_fingers', 'right_fingers': 'fist'
            },
            'teen': {
                'left_hand': [-60, -40], 'right_hand': [60, -40],
                'left_fingers': 'three_fingers', 'right_fingers': 'fist'
            },
            'chaar': {
                'left_hand': [-60, -40], 'right_hand': [60, -40],
                'left_fingers': 'four_fingers', 'right_fingers': 'fist'
            },
            'paanch': {
                'left_hand': [-60, -40], 'right_hand': [60, -40],
                'left_fingers': 'open_hand', 'right_fingers': 'fist'
            },
            
            # Greetings
            'salam': {
                'left_hand': [-40, -60], 'right_hand': [40, -60],
                'left_fingers': 'open_hand', 'right_fingers': 'open_hand',
                'wave': True
            },
            'khuda_hafiz': {
                'left_hand': [-50, -70], 'right_hand': [50, -70],
                'left_fingers': 'open_hand', 'right_fingers': 'open_hand',
                'wave': True
            },
            'shukriya': {
                'left_hand': [-30, -30], 'right_hand': [30, -30],
                'left_fingers': 'open_hand', 'right_fingers': 'open_hand'
            },
            
            # Family
            'ammi': {
                'left_hand': [-40, -50], 'right_hand': [40, -50],
                'left_fingers': 'pointing_up', 'right_fingers': 'heart_shape'
            },
            'abbu': {
                'left_hand': [-40, -50], 'right_hand': [40, -50],
                'left_fingers': 'thumbs_up', 'right_fingers': 'pointing_up'
            },
            'bhai': {
                'left_hand': [-60, -20], 'right_hand': [60, -20],
                'left_fingers': 'fist', 'right_fingers': 'fist'
            },
            'behn': {
                'left_hand': [-40, -60], 'right_hand': [40, -60],
                'left_fingers': 'gentle_wave', 'right_fingers': 'gentle_wave'
            },
            
            # Basic needs
            'paani': {
                'left_hand': [-30, -10], 'right_hand': [30, -10],
                'left_fingers': 'cup_shape', 'right_fingers': 'pouring'
            },
            'khana': {
                'left_hand': [-30, 0], 'right_hand': [30, 0],
                'left_fingers': 'open_hand', 'right_fingers': 'eating_motion'
            },
            'madad': {
                'left_hand': [-70, -60], 'right_hand': [70, -60],
                'left_fingers': 'open_hand', 'right_fingers': 'open_hand'
            },
            
            # Actions
            'reading': {
                'left_hand': [-40, -10], 'right_hand': [40, -10],
                'left_fingers': 'book_hold', 'right_fingers': 'page_turn'
            },
            'writing': {
                'left_hand': [-30, 0], 'right_hand': [30, 0],
                'left_fingers': 'paper_hold', 'right_fingers': 'pen_grip'
            },
            'listening': {
                'left_hand': [-90, -50], 'right_hand': [90, -50],
                'left_fingers': 'cupped_ear', 'right_fingers': 'cupped_ear'
            },
            'speaking': {
                'left_hand': [-40, -30], 'right_hand': [20, -40],
                'left_fingers': 'open_hand', 'right_fingers': 'near_mouth'
            },
            
            # Default pose
            'default': {
                'left_hand': [-80, 20], 'right_hand': [80, 20],
                'left_fingers': 'relaxed', 'right_fingers': 'relaxed'
            }
        }
        
        # Add contextual poses for all other gestures
        context_mappings = {
            # Objects
            'kitab': 'reading', 'qalam': 'writing', 'phone': 'speaking',
            'mobile': 'speaking', 'computer': 'writing',
            
            # Numbers 6-10
            'che': 'ek', 'saat': 'do', 'aath': 'teen', 'nau': 'chaar', 'das': 'paanch',
            
            # People
            'teacher': 'speaking', 'student': 'reading', 'doctor': 'madad',
            
            # Places
            'ghar': 'default', 'school': 'reading', 'hospital': 'madad',
            'masjid': 'shukriya', 'bazaar': 'default',
            
            # Emotions
            'khushi': 'salam', 'gham': 'default', 'mohabbat': 'shukriya',
            
            # Food
            'aam': 'khana', 'kela': 'khana', 'seb': 'khana', 'doodh': 'paani',
            'chai': 'paani', 'roti': 'khana', 'chawal': 'khana',
            
            # Vehicles
            'gaadi': 'default', 'bus': 'default', 'train': 'default',
            
            # Nature
            'suraj': 'salam', 'chaand': 'salam', 'phool': 'shukriya',
        }
        
        # Apply context mappings
        for gesture, reference in context_mappings.items():
            if gesture not in self.gesture_poses:
                self.gesture_poses[gesture] = self.gesture_poses[reference].copy()
        
        # Set default for any remaining gestures
        all_gestures = [
            'che', 'saat', 'aath', 'nau', 'das', 'teacher', 'student', 'hospital',
            'masjid', 'bazaar', 'dukaan', 'paise', 'kaam', 'waqt', 'din', 'raat',
            'subah', 'shaam', 'haan', 'nahin', 'accha', 'bura', 'bara', 'chota',
            'thanda', 'garam', 'khushi', 'gham', 'dost', 'dushman', 'mohabbat',
            'nafrat', 'aam', 'kela', 'seb', 'santra', 'angoor', 'doodh', 'chai',
            'kahwa', 'roti', 'chawal', 'gosht', 'machli', 'anda', 'sabzi',
            'gaadi', 'bus', 'train', 'jahaaz', 'cycle', 'rickshaw', 'sadak',
            'pool', 'darya', 'samandar', 'pahad', 'jungle', 'baagh', 'phool',
            'darakht', 'patta', 'suraj', 'chaand', 'sitara', 'badal', 'baarish',
            'hawa', 'aag', 'dhuaan', 'kaagaz', 'pencil', 'bag', 'table', 'kursi',
            'bistar', 'kamra', 'darwaza', 'khidki', 'deewar', 'chhat', 'zameen',
            'seerah', 'lift', 'phone', 'mobile', 'computer', 'tv', 'radio',
            'camera', 'photo', 'video', 'music', 'game', 'sport', 'football',
            'cricket', 'running', 'walking', 'sitting', 'standing', 'sleeping',
            'eating', 'drinking', 'looking', 'thinking', 'laughing', 'crying'
        ]
        
        for gesture in all_gestures:
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
            self.target_left_fingers = pose.get('left_fingers', 'relaxed')
            self.target_right_fingers = pose.get('right_fingers', 'relaxed')
            
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
                
            # Interpolate hand positions with smooth easing
            t = self.smooth_step(self.animation_progress)
            
            self.current_left_hand = [
                self.lerp(self.current_left_hand[i], self.target_left_hand[i], t)
                for i in range(2)
            ]
            self.current_right_hand = [
                self.lerp(self.current_right_hand[i], self.target_right_hand[i], t)
                for i in range(2)
            ]
            
            # Update finger positions
            if self.animation_progress > 0.3:  # Start finger animation later
                self.current_left_fingers = self.target_left_fingers
                self.current_right_fingers = self.target_right_fingers
                
    def smooth_step(self, t):
        """Smooth step interpolation for natural animation"""
        return t * t * (3.0 - 2.0 * t)
        
    def lerp(self, a, b, t):
        """Linear interpolation"""
        return a + (b - a) * t
        
    def draw_character(self):
        """Draw the animated character"""
        self.screen.fill((240, 240, 255))  # Light blue background
        
        center_x, center_y = self.character_pos
        
        # Draw shadow
        pygame.draw.ellipse(self.screen, (200, 200, 200), 
                          [center_x - 80, center_y + 180, 160, 30])
        
        # Draw head
        self.draw_head(center_x, center_y - 100)
        
        # Draw body
        self.draw_body(center_x, center_y)
        
        # Draw arms and hands
        self.draw_arm_and_hand('left', center_x + self.current_left_hand[0], 
                              center_y + self.current_left_hand[1], self.current_left_fingers)
        self.draw_arm_and_hand('right', center_x + self.current_right_hand[0], 
                              center_y + self.current_right_hand[1], self.current_right_fingers)
        
        # Draw legs
        self.draw_legs(center_x, center_y + 100)
        
        # Draw gesture information
        self.draw_gesture_info()
        
        # Add decorative elements
        self.draw_decorations()
        
        pygame.display.flip()
        
    def draw_head(self, x, y):
        """Draw character head with facial features"""
        # Head
        pygame.draw.circle(self.screen, self.skin_color, (x, y), self.head_radius)
        pygame.draw.circle(self.screen, (180, 140, 100), (x, y), self.head_radius, 3)
        
        # Hair
        pygame.draw.arc(self.screen, self.hair_color, 
                       [x - self.head_radius, y - self.head_radius, 
                        self.head_radius * 2, self.head_radius * 2], 
                       0, math.pi, 15)
        
        # Eyes
        pygame.draw.circle(self.screen, (255, 255, 255), (x - 20, y - 10), 8)
        pygame.draw.circle(self.screen, (255, 255, 255), (x + 20, y - 10), 8)
        pygame.draw.circle(self.screen, (50, 50, 50), (x - 20, y - 10), 4)
        pygame.draw.circle(self.screen, (50, 50, 50), (x + 20, y - 10), 4)
        
        # Nose
        pygame.draw.polygon(self.screen, (200, 160, 120), 
                          [(x, y + 5), (x - 3, y + 15), (x + 3, y + 15)])
        
        # Mouth - smile for positive gestures
        if self.current_gesture in ['salam', 'shukriya', 'khushi']:
            pygame.draw.arc(self.screen, (100, 50, 50), 
                           [x - 15, y + 10, 30, 20], 0, math.pi, 3)
        else:
            pygame.draw.line(self.screen, (100, 50, 50), (x - 10, y + 20), (x + 10, y + 20), 3)
            
    def draw_body(self, x, y):
        """Draw character body"""
        # Shirt
        pygame.draw.rect(self.screen, self.shirt_color, 
                        [x - 50, y - 50, 100, 150])
        pygame.draw.rect(self.screen, (50, 100, 160), 
                        [x - 50, y - 50, 100, 150], 3)
        
        # Collar
        pygame.draw.polygon(self.screen, (40, 90, 150),
                          [(x - 20, y - 50), (x, y - 30), (x + 20, y - 50)])
                          
    def draw_arm_and_hand(self, side, hand_x, hand_y, finger_style):
        """Draw arm and hand with specific finger position"""
        center_x, center_y = self.character_pos
        sign = -1 if side == 'left' else 1
        
        # Shoulder position
        shoulder_x = center_x + sign * 40
        shoulder_y = center_y - 30
        
        # Upper arm
        pygame.draw.line(self.screen, self.skin_color, 
                        (shoulder_x, shoulder_y), 
                        (shoulder_x + sign * 30, shoulder_y + 40), 12)
        
        # Forearm
        pygame.draw.line(self.screen, self.skin_color,
                        (shoulder_x + sign * 30, shoulder_y + 40),
                        (hand_x, hand_y), 10)
        
        # Hand
        self.draw_hand(hand_x, hand_y, finger_style, side)
        
    def draw_hand(self, x, y, finger_style, side):
        """Draw hand with specific finger configuration"""
        # Palm
        pygame.draw.circle(self.screen, self.skin_color, (x, y), self.hand_size)
        pygame.draw.circle(self.screen, (180, 140, 100), (x, y), self.hand_size, 2)
        
        # Fingers based on style
        if finger_style == 'open_hand':
            self.draw_open_fingers(x, y)
        elif finger_style == 'fist':
            self.draw_fist(x, y)
        elif finger_style == 'index_up':
            self.draw_index_finger(x, y)
        elif finger_style == 'two_fingers':
            self.draw_two_fingers(x, y)
        elif finger_style == 'three_fingers':
            self.draw_three_fingers(x, y)
        elif finger_style == 'four_fingers':
            self.draw_four_fingers(x, y)
        elif finger_style == 'thumbs_up':
            self.draw_thumbs_up(x, y)
        elif finger_style == 'pointing_up':
            self.draw_pointing_up(x, y)
        elif finger_style == 'cupped_ear':
            self.draw_cupped_hand(x, y)
        else:  # relaxed or other
            self.draw_relaxed_fingers(x, y)
            
    def draw_open_fingers(self, x, y):
        """Draw open hand with all fingers extended"""
        finger_positions = [
            (x - 20, y - 30), (x - 10, y - 35), (x, y - 35), 
            (x + 10, y - 35), (x + 20, y - 20)  # Thumb
        ]
        for fx, fy in finger_positions:
            pygame.draw.line(self.screen, self.skin_color, (x, y), (fx, fy), 4)
            pygame.draw.circle(self.screen, self.skin_color, (fx, fy), 3)
            
    def draw_fist(self, x, y):
        """Draw closed fist"""
        pygame.draw.circle(self.screen, self.skin_color, (x, y), self.hand_size - 5)
        pygame.draw.circle(self.screen, (160, 120, 80), (x, y), self.hand_size - 5, 2)
        
    def draw_index_finger(self, x, y):
        """Draw hand with index finger up"""
        pygame.draw.line(self.screen, self.skin_color, (x, y), (x, y - 30), 4)
        pygame.draw.circle(self.screen, self.skin_color, (x, y - 30), 3)
        
    def draw_two_fingers(self, x, y):
        """Draw hand with two fingers up"""
        pygame.draw.line(self.screen, self.skin_color, (x - 5, y), (x - 5, y - 30), 4)
        pygame.draw.line(self.screen, self.skin_color, (x + 5, y), (x + 5, y - 30), 4)
        pygame.draw.circle(self.screen, self.skin_color, (x - 5, y - 30), 3)
        pygame.draw.circle(self.screen, self.skin_color, (x + 5, y - 30), 3)
        
    def draw_three_fingers(self, x, y):
        """Draw hand with three fingers up"""
        for i, offset in enumerate([-8, 0, 8]):
            pygame.draw.line(self.screen, self.skin_color, (x + offset, y), (x + offset, y - 30), 4)
            pygame.draw.circle(self.screen, self.skin_color, (x + offset, y - 30), 3)
            
    def draw_four_fingers(self, x, y):
        """Draw hand with four fingers up"""
        for i, offset in enumerate([-12, -4, 4, 12]):
            pygame.draw.line(self.screen, self.skin_color, (x + offset, y), (x + offset, y - 30), 4)
            pygame.draw.circle(self.screen, self.skin_color, (x + offset, y - 30), 3)
            
    def draw_thumbs_up(self, x, y):
        """Draw thumbs up gesture"""
        pygame.draw.line(self.screen, self.skin_color, (x, y), (x - 10, y - 25), 4)
        pygame.draw.circle(self.screen, self.skin_color, (x - 10, y - 25), 4)
        
    def draw_pointing_up(self, x, y):
        """Draw pointing up gesture"""
        pygame.draw.line(self.screen, self.skin_color, (x, y), (x, y - 35), 5)
        pygame.draw.circle(self.screen, self.skin_color, (x, y - 35), 4)
        
    def draw_cupped_hand(self, x, y):
        """Draw cupped hand for listening"""
        pygame.draw.arc(self.screen, self.skin_color, [x - 15, y - 15, 30, 30], 
                       -math.pi/2, math.pi/2, 6)
        
    def draw_relaxed_fingers(self, x, y):
        """Draw relaxed hand position"""
        finger_positions = [
            (x - 15, y - 20), (x - 5, y - 25), (x + 5, y - 25), 
            (x + 15, y - 20), (x + 18, y - 5)  # Thumb
        ]
        for fx, fy in finger_positions:
            pygame.draw.line(self.screen, self.skin_color, (x, y), (fx, fy), 3)
            pygame.draw.circle(self.screen, self.skin_color, (fx, fy), 2)
            
    def draw_legs(self, x, y):
        """Draw character legs"""
        # Pants
        pygame.draw.rect(self.screen, self.pants_color, [x - 40, y, 80, 120])
        pygame.draw.rect(self.screen, (30, 30, 80), [x - 40, y, 80, 120], 3)
        
        # Feet
        pygame.draw.ellipse(self.screen, (40, 40, 40), [x - 50, y + 110, 40, 20])
        pygame.draw.ellipse(self.screen, (40, 40, 40), [x + 10, y + 110, 40, 20])
        
    def draw_gesture_info(self):
        """Draw current gesture information"""
        if self.current_gesture:
            # Gesture name
            text = self.font.render(f"Gesture: {self.current_gesture.upper()}", True, (50, 50, 50))
            self.screen.blit(text, (20, 20))
            
            # Load gesture translations
            try:
                with open('labels.json', 'r', encoding='utf-8') as f:
                    labels = json.load(f)
                    
                # Find the gesture in labels
                for key, value in labels.items():
                    if value['name'] == self.current_gesture:
                        urdu_text = self.small_font.render(f"Urdu: {value['urdu']}", True, (0, 100, 0))
                        pashto_text = self.small_font.render(f"Pashto: {value['pashto']}", True, (0, 0, 150))
                        english_text = self.small_font.render(f"English: {value['english']}", True, (150, 0, 0))
                        
                        self.screen.blit(urdu_text, (20, 60))
                        self.screen.blit(pashto_text, (20, 85))
                        self.screen.blit(english_text, (20, 110))
                        break
            except:
                pass
                
    def draw_decorations(self):
        """Draw decorative Pakistani elements"""
        # Pakistani flag colors in corner
        pygame.draw.rect(self.screen, (0, 100, 0), [self.width - 80, 20, 60, 40])  # Green
        pygame.draw.rect(self.screen, (255, 255, 255), [self.width - 80, 20, 15, 40])  # White stripe
        
        # Star and crescent (simplified)
        pygame.draw.circle(self.screen, (255, 255, 255), (self.width - 40, 40), 8, 2)
        
    def run_animation_loop(self, gesture_name, duration=3.0):
        """Run the animation loop for a specific gesture"""
        self.animate_to_gesture(gesture_name)
        
        start_time = time.time()
        
        while time.time() - start_time < duration:
            dt = self.clock.tick(60) / 1000.0  # Delta time in seconds
            
            # Handle pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return False
                        
            # Update animation
            self.update_animation(dt)
            
            # Draw character
            self.draw_character()
            
        # Hold the final pose briefly
        for _ in range(30):  # 0.5 seconds at 60 FPS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
            self.draw_character()
            self.clock.tick(60)
            
        # Return to default pose
        self.animate_to_gesture('default')
        for _ in range(60):  # 1 second transition
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
            self.update_animation(dt)
            self.draw_character()
            
        return True
        
    def cleanup(self):
        """Clean up resources"""
        pygame.quit()

def demo_character():
    """Demo function to test the animated character"""
    character = SignLanguageCharacter()
    
    # Demo gestures
    demo_gestures = [
        'salam', 'shukriya', 'khuda_hafiz', 
        'ek', 'do', 'teen', 'chaar', 'paanch',
        'paani', 'khana', 'madad', 'ammi', 'abbu',
        'reading', 'writing', 'listening', 'speaking'
    ]
    
    try:
        print("🎭 3D Character Demo Started!")
        print("🎮 Press ESC to exit, or close window")
        
        for gesture in demo_gestures:
            print(f"🤟 Demonstrating: {gesture}")
            if not character.run_animation_loop(gesture, 2.5):
                break
            time.sleep(0.3)
            
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped by user")
    finally:
        character.cleanup()

if __name__ == "__main__":
    print("🎭 Starting Animated Character Demo...")
    print("📱 This will show various Pakistani sign language gestures")
    print("❌ Press ESC or close window to exit")
    demo_character()