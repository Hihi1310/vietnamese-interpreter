import os
import sys
import json
import argparse
from datetime import datetime
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
from pygame import mixer
import threading
import msvcrt  # For Windows keyboard input

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from transcription import AudioTranscriber
from translation import TextTranslator
from logger import setup_logger

# Initialize pygame mixer for audio playback
mixer.init()

class VietnameseInterpreter:
    def __init__(self, config_path="config.json"):
        """Initialize the Vietnamese Interpreter system"""
        # Load configuration
        config_dir = os.path.dirname(os.path.abspath(__file__))
        if not os.path.isabs(config_path):
            config_path = os.path.join(os.path.dirname(config_dir), config_path)
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.setup_logging()
        self.setup_components()
    
    def setup_logging(self):
        """Setup minimal system logging for debugging"""
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        log_file = os.path.join(logs_dir, 'system.txt')
        self.logger = setup_logger('system', log_file, self.config['logging']['log_level'])
        self.logger.info("System init")
    
    def setup_components(self):
        """Initialize transcriber and translator components"""
        try:
            # Get the project root directory (parent of src)
            project_root = os.path.dirname(os.path.dirname(__file__))
            
            # Ensure logs directory exists with absolute path
            logs_dir = os.path.join(project_root, 'logs')
            os.makedirs(logs_dir, exist_ok=True)
            
            # Update config with absolute paths before passing to components
            if 'paths' not in self.config:
                self.config['paths'] = {}
            self.config['paths']['logs_dir'] = logs_dir
            
            # Pass the updated config directly to components
            self.transcriber = AudioTranscriber(config_dict=self.config)
            self.translator = TextTranslator(config_dict=self.config)
            
        except Exception as e:
            self.logger.error(f"Component initialization failed: {str(e)}")
            raise
    
    def speak_text(self, text, language='en'):
        """Convert text to speech and play it"""
        try:
            mp3audio = BytesIO()
            
            # Set language for TTS based on text content
            if language == 'vi':
                tts = gTTS(text, lang='vi', tld='com')
            else:
                tts = gTTS(text, lang='en', tld='us')
            
            tts.write_to_fp(mp3audio)
            mp3audio.seek(0)
            
            mixer.music.load(mp3audio, "mp3")
            mixer.music.play()
            
            while mixer.music.get_busy():
                pass
            
            mp3audio.close()
            self.logger.info(f"TTS played: {language}")
            
        except Exception as e:
            self.logger.error(f"TTS failed: {str(e)}")
    
    def save_conversation(self, text):
        """Save conversation to daily log file in configured conversations folder"""
        try:
            # Create conversations directory from config
            conversations_dir = self.config['paths']['conversations_dir']
            
            # Convert relative path to absolute path from project root
            if not os.path.isabs(conversations_dir):
                project_root = os.path.dirname(os.path.dirname(__file__))
                conversations_dir = os.path.join(project_root, conversations_dir.lstrip('./'))
            
            os.makedirs(conversations_dir, exist_ok=True)
            
            # Format: conversation-yy-mm-dd-timestamp.txt
            now = datetime.now()
            date_str = now.strftime("%y-%m-%d")
            timestamp_str = now.strftime("%H%M%S")
            filename = f"conversation-{date_str}-{timestamp_str}.txt"
            
            # Use the same file for the entire day by checking if today's file exists
            today_pattern = f"conversation-{date_str}-"
            existing_files = [f for f in os.listdir(conversations_dir) if f.startswith(today_pattern)]
            
            if existing_files:
                # Use the first existing file for today
                log_path = os.path.join(conversations_dir, existing_files[0])
            else:
                # Create new file with current timestamp
                log_path = os.path.join(conversations_dir, filename)
            
            with open(log_path, "a", encoding='utf-8') as f:
                timestamp = now.strftime("%H:%M:%S")
                f.write(f"[{timestamp}] {text}\n")
                
        except Exception as e:
            self.logger.error(f"Failed to save conversation: {str(e)}")
    
    def real_time_interpreter(self, source_language):
        """Real-time microphone interpretation"""
        try:
            self.logger.info("Starting real-time mode")
            
            # Setup microphone
            recognizer = sr.Recognizer()
            microphone = sr.Microphone()
            recognizer.dynamic_energy_threshold = False
            recognizer.energy_threshold = 400
            
            target_language = 'en' if source_language == 'vi' else 'vi'
            
            # Flag to control the main loop
            self.should_exit = False
            
            def keyboard_listener():
                """Listen for keyboard input in a separate thread"""
                while not self.should_exit:
                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode('utf-8').lower()
                        if key == 'q':
                            print("\n[Keyboard] Quitting...")
                            self.should_exit = True
                            break
            
            # Start keyboard listener in a separate thread
            keyboard_thread = threading.Thread(target=keyboard_listener, daemon=True)
            keyboard_thread.start()
            
            print(f"\nREAL-TIME INTERPRETER MODE")
            print(f"Source: {source_language.upper()} -> Target: {target_language.upper()}")
            print("Press 'q' on keyboard to quit")
            
            while not self.should_exit:
                with microphone as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    print("Listening... (press 'q' to quit)")
                    
                    try:
                        # Listen for audio with shorter timeout to check exit flag more frequently
                        audio = recognizer.listen(source, timeout=3, phrase_time_limit=15)
                        
                        if self.should_exit:
                            break
                            
                        # Transcribe
                        print("Transcribing...")
                        if source_language == 'vi':
                            text = recognizer.recognize_google(audio, language='vi-VN')
                        else:
                            text = recognizer.recognize_google(audio, language='en-US')
                        
                        if len(text) < 1 or self.should_exit:
                            continue
                        
                        print(f"You said ({source_language}): {text}")
                        self.save_conversation(f"User ({source_language}): {text}")
                        
                        if self.should_exit:
                            break
                            
                        # Translate
                        print("Translating...")
                        translation_result = self.translator.translate(text, source_language)
                        translated_text = translation_result['translated_text']
                        
                        if self.should_exit:
                            break
                            
                        print(f"Translation ({target_language}): {translated_text}")
                        self.save_conversation(f"Interpreter ({target_language}): {translated_text}")
                        
                        # Speak translation
                        if not self.should_exit:
                            self.speak_text(translated_text, target_language)
                        print("-" * 50)
                        
                    except sr.WaitTimeoutError:
                        if not self.should_exit:
                            print("Timeout - say something... (or press 'q' to quit)")
                        continue
                    except sr.UnknownValueError:
                        if not self.should_exit:
                            print("Could not understand audio")
                        continue
                    except sr.RequestError as e:
                        if not self.should_exit:
                            print(f"Speech recognition error: {e}")
                        continue
                    except Exception as e:
                        if not self.should_exit:
                            print(f"Error: {e}")
                        continue
                        
        except Exception as e:
            self.logger.error(f"Real-time mode failed: {str(e)}")
            raise

def main():
    """Command-line interface for the Vietnamese Interpreter"""
    parser = argparse.ArgumentParser(
        description='Vietnamese-English Real-time Interpreter using Speech Recognition and Gemini',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Real-time mode
  python main.py --source vi
  python main.py -s en
        """
    )
    
    # Required argument
    parser.add_argument('-s', '--source', 
                       choices=['vi', 'en'], 
                       required=True,
                       help='Source language: vi (Vietnamese) or en (English)')
    
    # Optional flags
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='Enable verbose output')
    
    # Parse arguments
    try:
        args = parser.parse_args()
    except SystemExit:
        return
    
    print("Vietnamese Real-time Interpreter")
    print("=" * 35)
    
    try:
        # Initialize interpreter
        if args.verbose:
            print("Initializing Vietnamese Interpreter...")
        interpreter = VietnameseInterpreter()
        
        # Real-time mode only
        print("Starting real-time interpreter...")
        interpreter.real_time_interpreter(args.source)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        print("Check the log files in ./logs/ for detailed error information.")

if __name__ == "__main__":
    main()
