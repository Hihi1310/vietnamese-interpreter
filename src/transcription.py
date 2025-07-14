import json
import os
import speech_recognition as sr
from logger import setup_logger

class AudioTranscriber:
    def __init__(self, config_path=None, config_dict=None):
        """Initialize the transcriber with configuration for real-time speech recognition"""
        if config_dict:
            self.config = config_dict
        elif config_path:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            raise ValueError("Either config_path or config_dict must be provided")
        
        self.setup_logging()
        self.load_model()
    
    def setup_logging(self):
        """Setup logging using centralized logger"""
        log_file = os.path.join(self.config['paths']['logs_dir'], 'transcription.txt')
        self.logger = setup_logger('transcription', log_file, self.config['logging']['log_level'])
        self.logger.info("Speech recognizer init")
    
    def load_model(self):
        """Initialize speech recognition for real-time use"""
        try:
            # Initialize speech recognizer
            self.recognizer = sr.Recognizer()
            
            # Configure recognizer settings for real-time use
            self.recognizer.dynamic_energy_threshold = False
            self.recognizer.energy_threshold = 400
            
            self.logger.info("Speech recognition ready for real-time mode")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize speech recognition: {str(e)}")
            raise

if __name__ == "__main__":
    # Simple test
    transcriber = AudioTranscriber()
    print("Speech Recognition initialized successfully for real-time mode!")
    print("This module provides speech recognition setup for the Vietnamese interpreter.")
