import os
import sys
import json
import logging
from datetime import datetime
import pytz

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from transcription import AudioTranscriber
from translation import TextTranslator

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
        """Setup main system logging"""
        gmt7 = pytz.timezone('Asia/Bangkok')
        
        class GMT7Formatter(logging.Formatter):
            def formatTime(self, record, datefmt=None):
                dt = datetime.fromtimestamp(record.created, tz=gmt7)
                return dt.strftime('%Y-%m-%d %H:%M:%S GMT+7')
        
        self.logger = logging.getLogger('system')
        self.logger.setLevel(getattr(logging, self.config['logging']['log_level']))
        
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        handler = logging.FileHandler(os.path.join(logs_dir, 'system.txt'))
        formatter = GMT7Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        self.logger.info("Vietnamese Interpreter system initialized")
    
    def setup_components(self):
        """Initialize transcriber and translator components"""
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
            
            self.logger.info("Initializing transcriber...")
            self.transcriber = AudioTranscriber(config_path)
            
            self.logger.info("Initializing translator...")
            self.translator = TextTranslator(config_path)
            
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {str(e)}")
            raise
    
    def process_audio_file(self, audio_file_path, save_results=True):
        """Complete workflow: transcribe audio and translate text"""
        try:
            self.logger.info(f"Starting processing of: {audio_file_path}")
            
            # Step 1: Transcribe audio
            self.logger.info("Step 1: Transcribing audio...")
            transcription = self.transcriber.transcribe(audio_file_path)
            
            # Step 2: Translate text
            self.logger.info("Step 2: Translating text...")
            translation = self.translator.translate(
                transcription['text'], 
                source_lang=transcription['language']
            )
            
            # Combine results
            final_result = {
                'input_file': audio_file_path,
                'transcription': transcription,
                'translation': translation,
                'processing_timestamp': datetime.now(pytz.timezone('Asia/Bangkok')).isoformat(),
                'total_processing_time': transcription['processing_time'] + translation['processing_time']
            }
            
            # Save results if requested
            if save_results:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    'data', 'output',
                    f"interpreter_result_{timestamp}.json"
                )
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(final_result, f, ensure_ascii=False, indent=2)
                
                self.logger.info(f"Results saved to: {output_path}")
            
            self.logger.info(f"Processing completed successfully")
            return final_result
            
        except Exception as e:
            self.logger.error(f"Processing failed: {str(e)}")
            raise
    
    def print_results(self, result):
        """Print results in a user-friendly format"""
        print("\n" + "="*60)
        print("VIETNAMESE INTERPRETER RESULTS")
        print("="*60)
        
        print(f"\nInput File: {result['input_file']}")
        print(f"Processing Time: {result['total_processing_time']:.2f} seconds")
        print(f"Timestamp: {result['processing_timestamp']}")
        
        print(f"\n--- TRANSCRIPTION ---")
        print(f"Detected Language: {result['transcription']['language']}")
        print(f"Confidence: {result['transcription']['confidence']:.3f}")
        print(f"Text: {result['transcription']['text']}")
        
        print(f"\n--- TRANSLATION ---")
        print(f"Language Direction: {result['translation']['source_language']} -> {result['translation']['target_language']}")
        print(f"Confidence: {result['translation']['confidence']:.3f}")
        print(f"Translated Text: {result['translation']['translated_text']}")
        
        print("\n" + "="*60)

def main():
    """Command-line interface for the Vietnamese Interpreter"""
    print("Vietnamese Interpreter POC")
    print("=" * 30)
    
    # Check if audio file is provided
    if len(sys.argv) < 2:
        print("Usage: python main.py <audio_file_path>")
        print("\nExample:")
        print("  python main.py ./data/input/sample.wav")
        print("\nSupported formats: .wav, .mp3, .m4a")
        return
    
    audio_file = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(audio_file):
        print(f"Error: File not found - {audio_file}")
        return
    
    try:
        # Initialize interpreter
        print("Initializing Vietnamese Interpreter...")
        interpreter = VietnameseInterpreter()
        
        # Process audio file
        print(f"Processing: {audio_file}")
        result = interpreter.process_audio_file(audio_file)
        
        # Display results
        interpreter.print_results(result)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Check the log files in ./logs/ for detailed error information.")

if __name__ == "__main__":
    main()
