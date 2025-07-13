import os
import sys
import json
import argparse
from datetime import datetime
import pytz

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from transcription import AudioTranscriber
from translation import TextTranslator
from logger import setup_logger

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
        self.logger.info("Vietnamese Interpreter system initialized")
    
    def setup_components(self):
        """Initialize transcriber and translator components"""
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
            
            self.transcriber = AudioTranscriber(config_path)
            self.translator = TextTranslator(config_path)
            
            self.logger.info("Components initialized")
            
        except Exception as e:
            self.logger.error(f"Component initialization failed: {str(e)}")
            raise
    
    def process_audio_file(self, audio_file_path, source_language=None, save_results=True):
        """Complete workflow: transcribe audio and translate text"""
        try:
            self.logger.info(f"Processing: {audio_file_path}")
            
            # Transcribe audio
            transcription = self.transcriber.transcribe(audio_file_path)
            
            # Get source language for translation
            if source_language is None:
                # Use detected language from transcription, default to 'vi' if not available
                source_language = transcription.get('language', 'vi')
            
            # Translate text
            translation = self.translator.translate(transcription['text'], source_language)
            
            # Combine results
            final_result = {
                'input_file': audio_file_path,
                'transcription': transcription,
                'translation': translation,
                'processing_timestamp': datetime.now(pytz.timezone('Asia/Bangkok')).isoformat(),
                'total_processing_time': transcription['processing_time'] + translation['processing_time']
            }
            
            # Save results
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
            
            self.logger.info("Processing completed")
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
        print(f"Text: {result['transcription']['text']}")
        
        print(f"\n--- TRANSLATION ---")
        print(f"Translated Text: {result['translation']['translated_text']}")
        
        print("\n" + "="*60)

def main():
    """Command-line interface for the Vietnamese Interpreter"""
    parser = argparse.ArgumentParser(
        description='Vietnamese-English Interpreter using Whisper and Gemini',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --file audio.wav --source vi
  python main.py -f audio.wav --source en
  python main.py -f audio.wav -s vi --no-save
  python main.py -f audio.wav -s en --verbose
        """
    )
    
    # Required flags
    parser.add_argument('-f', '--file', 
                       dest='audio_file',
                       required=True,
                       help='Path to the audio file (.wav, .mp3, .m4a)')
    
    parser.add_argument('-s', '--source', 
                       choices=['vi', 'en'], 
                       required=True,
                       help='Source language: vi (Vietnamese) or en (English)')
    
    # Optional flags
    parser.add_argument('--no-save', 
                       action='store_true',
                       help='Skip saving results to file')
    
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='Enable verbose output')
    
    # Parse arguments
    try:
        args = parser.parse_args()
    except SystemExit:
        return
    
    print("Vietnamese Interpreter POC")
    print("=" * 30)
    
    # Check if file exists
    if not os.path.exists(args.audio_file):
        print(f"Error: File not found - {args.audio_file}")
        return
    
    try:
        # Initialize interpreter
        if args.verbose:
            print("Initializing Vietnamese Interpreter...")
        interpreter = VietnameseInterpreter()
        
        # Process audio file
        print(f"Processing: {args.audio_file} (Source: {args.source})")
        
        # Process with save setting
        save_results = not args.no_save
        result = interpreter.process_audio_file(args.audio_file, args.source, save_results)
        
        # Display results
        interpreter.print_results(result)
        
        if args.verbose:
            print(f"\nProcessing details:")
            print(f"  Transcription time: {result['transcription']['processing_time']:.2f}s")
            print(f"  Translation time: {result['translation']['processing_time']:.2f}s")
            print(f"  Total time: {result['total_processing_time']:.2f}s")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        print("Check the log files in ./logs/ for detailed error information.")

if __name__ == "__main__":
    main()
