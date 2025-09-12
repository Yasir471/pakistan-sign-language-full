#!/usr/bin/env python3
"""
Pakistani Story Integration for Sign Language App
Interactive storytelling with 3D character demonstrations
"""

import json
import time
import threading
from pathlib import Path

class PakistaniStoryTeller:
    def __init__(self, labels_path="labels.json"):
        """Initialize story teller with gesture database"""
        # Load gesture labels
        try:
            with open(labels_path, 'r', encoding='utf-8') as f:
                self.labels = json.load(f)
        except Exception as e:
            print(f"❌ Error loading labels: {e}")
            self.labels = {}
        
        # Create reverse mapping for story words to gestures
        self.create_story_mappings()
        
        # Load the complete Pakistani story
        self.load_pakistani_story()
    
    def create_story_mappings(self):
        """Create mappings from story words to available gestures"""
        self.story_to_gesture = {}
        
        # Map story-relevant words to available gestures
        story_mappings = {
            # Animals and characters
            'fox': 'dost',  # Use 'friend' as closest match
            'لومڑی': 'dost',
            'ګیدړه': 'dost',
            
            # Food and objects
            'grapes': 'angoor',
            'انگور': 'angoor',
            'انګور': 'angoor',
            'food': 'khana',
            'کھانے': 'khana',
            'خواړه': 'khana',
            'eat': 'eating',
            'کھا': 'eating',
            'وخورم': 'eating',
            
            # Actions
            'jump': 'running',  # Closest action available
            'چھلانگ': 'running',
            'ټوپ': 'running',
            'walk': 'walking',
            'گھوم': 'walking',
            'ګرځېده': 'walking',
            'go': 'walking',
            'گئی': 'walking',
            'ولاړه': 'walking',
            
            # Emotions and states
            'hungry': 'gham',  # Use sadness for hunger
            'بھوکی': 'gham',
            'وږې': 'gham',
            'tired': 'gham',
            'تھک': 'gham',
            'ستړې': 'gham',
            'think': 'thinking',
            'سوچا': 'thinking',
            'سوچ': 'thinking',
            
            # Numbers and quantities
            'many': 'paanch',  # Use 'five' for 'many'
            'بہت': 'paanch',
            'ډېر': 'paanch',
            'several': 'teen',  # Use 'three' for 'several'
            'کئی': 'teen',
            'څو': 'teen',
            
            # Nature elements
            'tree': 'darakht',
            'تاک': 'darakht',
            'vine': 'darakht',
            'high': 'pahad',  # Use 'mountain' for 'high'
            'اونچے': 'pahad',
            'لوړ': 'pahad',
            
            # Speech and communication
            'say': 'speaking',
            'بولی': 'speaking',
            'وویل': 'speaking',
            
            # Moral concepts
            'truth': 'accha',  # Use 'good' for truth
            'حقیقت': 'accha',
            'lie': 'bura',  # Use 'bad' for lie
            'جھوٹ': 'bura',
            'failure': 'gham',
            'ناکامی': 'gham',
            'ناکامي': 'gham',
            
            # Time concepts
            'day': 'din',
            'دن': 'din',
            'ورځ': 'din',
            'time': 'waqt',
            'وقت': 'waqt',
            'وخت': 'waqt',
        }
        
        # Add mappings to our dictionary
        for word, gesture_name in story_mappings.items():
            if any(info['name'] == gesture_name for info in self.labels.values()):
                # Find the gesture info
                for info in self.labels.values():
                    if info['name'] == gesture_name:
                        self.story_to_gesture[word.lower()] = info
                        break
    
    def load_pakistani_story(self):
        """Load the complete Pakistani story in three languages"""
        self.story = {
            'title': {
                'urdu': 'انگور تو کھٹے ہیں',
                'pashto': 'انګور خو تروې دي',
                'english': 'The Sour Grapes'
            },
            'content': {
                'urdu': [
                    "ایک دن ایک لومڑی بہت بھوکی تھی۔",
                    "وہ کھانے کی تلاش میں ادھر ادھر گھوم رہی تھی۔",
                    "چلتے چلتے اس کی نظر ایک تاک پر پڑی، جس پر بہت سے انگور لگے ہوئے تھے۔",
                    "لومڑی نے سوچا، یہ انگور کھا لوں گی، میری بھوک مٹ جائے گی۔",
                    "وہ تاک کے پاس گئی اور انگور توڑنے کی کوشش کی،",
                    "مگر انگور بہت اونچے تھے۔",
                    "اس نے کئی بار چھلانگ لگائی، لیکن ہر بار ناکام رہی۔",
                    "آخر کار وہ تھک گئی۔",
                    "چلتے وقت وہ بولی، یہ انگور تو کھٹے ہیں۔ مجھے ویسے بھی نہیں کھانے تھے!",
                    "اور وہ وہاں سے چلی گئی۔"
                ],
                'pashto': [
                    "یوه ورځ یوه ګیدړه ډېره وږې وه.",
                    "هغې خواړه لټول او هر خوا ته ګرځېده.",
                    "په ګرځېدو کې یې یوه تاک ولیده چې پرې ډېر انګور لګېدلي وو.",
                    "ګیدړې سوچ وکړ، که دا انګور وخورم، نو وږې نه پاتې کېږم.",
                    "هغې تاک ته ورنژدې شوه او هڅه یې وکړه چې انګور راواخلي.",
                    "خو انګور ډېر لوړ وو.",
                    "هغې څو ځله ټوپ وواهه، خو بریالۍ نه شوه.",
                    "ورو ورو ستړې شوه.",
                    "د تللو پر وخت یې وویل: دا انګور خو تروې دي، ما ته خو یې خوړل هیڅ نه وو.",
                    "او له هغه ځایه ولاړه."
                ],
                'english': [
                    "One day a fox was very hungry.",
                    "She was wandering around looking for food.",
                    "While walking, she saw a vine with many grapes hanging on it.",
                    "The fox thought, 'I will eat these grapes and satisfy my hunger.'",
                    "She went near the vine and tried to pluck the grapes,",
                    "but the grapes were very high.",
                    "She jumped several times, but failed every time.",
                    "Finally, she got tired.",
                    "While leaving, she said, 'These grapes are sour anyway. I didn't want to eat them!'",
                    "And she left from there."
                ]
            },
            'moral': {
                'urdu': 'اخلاقی سبق: ناکامی کو چھپانے کے لیے جھوٹ نہ بولیں',
                'pashto': 'اخلاقي سبق: ناکامي مه پټوئ، حقیقت ومنئ',
                'english': 'Moral Lesson: Do not lie to hide failure, accept the truth'
            }
        }
    
    def find_gesture_for_sentence(self, sentence):
        """Find the most relevant gesture for a sentence"""
        sentence = sentence.lower()
        words = sentence.split()
        
        # Look for direct matches first
        for word in words:
            if word in self.story_to_gesture:
                return self.story_to_gesture[word]
        
        # Look for partial matches
        for word, gesture_info in self.story_to_gesture.items():
            if word in sentence:
                return gesture_info
        
        # Default gesture for narration
        return self.story_to_gesture.get('speaking', None)
    
    def tell_story_with_character(self, language='urdu'):
        """Tell the story with 3D character demonstrations"""
        try:
            from character_3d import SignLanguageCharacter
        except ImportError:
            print("❌ 3D Character system not available")
            self.tell_story_text_only(language)
            return
        
        print("🎭 Starting Pakistani Story with 3D Character...")
        print("=" * 80)
        print(f"📚 Title: {self.story['title'][language]}")
        print("=" * 80)
        
        try:
            character = SignLanguageCharacter(width=1000, height=700)
            
            # Tell each sentence with character demonstration
            sentences = self.story['content'][language]
            
            for i, sentence in enumerate(sentences, 1):
                print(f"\n📖 Sentence {i}: {sentence}")
                
                # Find relevant gesture
                gesture_info = self.find_gesture_for_sentence(sentence)
                
                if gesture_info:
                    print(f"🤟 Demonstrating gesture: {gesture_info['name']} ({gesture_info['english']})")
                    
                    # Animate the gesture
                    if not character.run_animation_loop(gesture_info['name'], duration=4.0):
                        print("⚠️ Animation interrupted by user")
                        break
                else:
                    print("📝 No specific gesture for this sentence, using default pose")
                    if not character.run_animation_loop('default', duration=2.0):
                        break
                
                time.sleep(0.5)  # Brief pause between sentences
            
            # Show the moral lesson
            print("\n" + "=" * 80)
            print(f"💡 {self.story['moral'][language]}")
            print("=" * 80)
            
            # Final gesture for the moral
            moral_gesture = self.story_to_gesture.get('truth', self.story_to_gesture.get('accha', None))
            if moral_gesture:
                print(f"🤟 Final gesture for moral lesson: {moral_gesture['name']}")
                character.run_animation_loop(moral_gesture['name'], duration=3.0)
            
            character.cleanup()
            print("✅ Story completed successfully!")
            
        except Exception as e:
            print(f"❌ Error with 3D character: {e}")
            self.tell_story_text_only(language)
    
    def tell_story_text_only(self, language='urdu'):
        """Tell the story in text format only"""
        print("📚 Pakistani Story (Text Only)")
        print("=" * 80)
        print(f"📖 Title: {self.story['title'][language]}")
        print("=" * 80)
        
        sentences = self.story['content'][language]
        
        for i, sentence in enumerate(sentences, 1):
            print(f"\n{i:2d}. {sentence}")
            
            # Find and mention relevant gesture
            gesture_info = self.find_gesture_for_sentence(sentence)
            if gesture_info:
                print(f"    🤟 Related gesture: {gesture_info['name']} ({gesture_info['english']})")
            
            time.sleep(1.5)  # Pause for reading
        
        print("\n" + "=" * 80)
        print(f"💡 {self.story['moral'][language]}")
        print("=" * 80)
    
    def interactive_story_mode(self):
        """Interactive story mode with user choices"""
        print("🎯 Interactive Pakistani Story Mode")
        print("📚 Story: The Sour Grapes (انگور تو کھٹے ہیں)")
        print("=" * 80)
        
        while True:
            print("\n🌐 Choose language / زبان منتخب کریں:")
            print("1. 🇵🇰 Urdu (اردو)")
            print("2. 🇦🇫 Pashto (پښتو)")
            print("3. 🏴󠁧󠁢󠁥󠁮󠁧󠁿 English")
            print("4. 🎭 All Languages with 3D Character")
            print("5. 🔙 Back to Main Menu")
            
            choice = input("\n👉 Enter choice (1-5): ").strip()
            
            if choice == '1':
                self.tell_story_with_character('urdu')
            elif choice == '2':
                self.tell_story_with_character('pashto')
            elif choice == '3':
                self.tell_story_with_character('english')
            elif choice == '4':
                self.tell_all_languages_story()
            elif choice == '5':
                break
            else:
                print("❌ Invalid choice. Please enter 1-5.")
    
    def tell_all_languages_story(self):
        """Tell story in all three languages"""
        languages = ['urdu', 'pashto', 'english']
        language_names = ['🇵🇰 Urdu', '🇦🇫 Pashto', '🏴󠁧󠁢󠁥󠁮󠁧󠁿 English']
        
        for lang, lang_name in zip(languages, language_names):
            print(f"\n🎭 Now telling story in {lang_name}")
            print("⏰ Press Ctrl+C to skip to next language or ESC to exit")
            
            try:
                self.tell_story_with_character(lang)
                print(f"✅ {lang_name} version completed!")
                time.sleep(2)
            except KeyboardInterrupt:
                print(f"\n⏭️ Skipping to next language...")
                continue
        
        print("\n🎉 All language versions completed!")
    
    def practice_story_gestures(self):
        """Practice gestures related to the story"""
        print("🤟 Practice Story-Related Gestures")
        print("=" * 60)
        
        # Key story gestures to practice
        story_gestures = [
            'angoor',    # grapes
            'khana',     # food/eating  
            'thinking',  # fox thinking
            'running',   # jumping
            'walking',   # going away
            'speaking',  # fox speaking
            'gham',      # sadness/tiredness
            'accha',     # good (truth)
            'bura'       # bad (lie)
        ]
        
        available_gestures = []
        for gesture_name in story_gestures:
            for info in self.labels.values():
                if info['name'] == gesture_name:
                    available_gestures.append(info)
                    break
        
        if not available_gestures:
            print("❌ No story-related gestures available")
            return
        
        print(f"📚 Found {len(available_gestures)} story-related gestures to practice:")
        
        try:
            from character_3d import SignLanguageCharacter
            character = SignLanguageCharacter(width=900, height=700)
            
            for i, gesture_info in enumerate(available_gestures, 1):
                print(f"\n🤟 {i}/{len(available_gestures)}: {gesture_info['name'].upper()}")
                print(f"🏴󠁧󠁢󠁥󠁮󠁧󠁿 English: {gesture_info['english']}")
                print(f"🇵🇰 Urdu: {gesture_info['urdu']}")
                print(f"🇦🇫 Pashto: {gesture_info['pashto']}")
                print("🎭 Watch the character demonstrate this gesture...")
                
                if not character.run_animation_loop(gesture_info['name'], duration=4.0):
                    print("⚠️ Practice session interrupted")
                    break
                
                time.sleep(1)
            
            character.cleanup()
            print("\n✅ Story gesture practice completed!")
            
        except ImportError:
            print("⚠️ 3D Character not available, showing text only:")
            for gesture_info in available_gestures:
                print(f"🤟 {gesture_info['name']}: {gesture_info['english']} | {gesture_info['urdu']} | {gesture_info['pashto']}")

def main():
    """Main story teller interface"""
    story_teller = PakistaniStoryTeller()
    
    print("📚 PAKISTANI STORYTELLING WITH SIGN LANGUAGE")
    print("=" * 80)
    print("🦊 Featured Story: The Sour Grapes (انگور تو کھٹے ہیں)")
    print("🎭 Interactive 3D Character Demonstrations")
    print("🌐 Trilingual Support: Urdu, Pashto, English")
    print("=" * 80)
    
    while True:
        print("\n🎯 Choose an option:")
        print("1. 🎭 Tell Story with 3D Character")
        print("2. 📖 Read Story (Text Only)")
        print("3. 🤟 Practice Story Gestures")
        print("4. 🌐 Interactive Story Mode")
        print("5. ❌ Exit")
        
        choice = input("\n👉 Enter choice (1-5): ").strip()
        
        if choice == '1':
            story_teller.tell_story_with_character('urdu')
        elif choice == '2':
            story_teller.tell_story_text_only('urdu')
        elif choice == '3':
            story_teller.practice_story_gestures()
        elif choice == '4':
            story_teller.interactive_story_mode()
        elif choice == '5':
            print("👋 Thank you for using Pakistani Storytelling!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    main()