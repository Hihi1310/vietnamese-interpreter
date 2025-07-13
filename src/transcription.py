import json
import os
import time
import logging
from datetime import datetime
import pytz
import librosa
from transformers import pipeline
import torch

class AudioTranscriber:
    def __init__(self, config_path="config.json"):
        """Initialize the transcriber with configuration"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.setup_logging()
        self.load_model()
    
    def setup_logging(self):
        """Setup logging with GMT+7 timezone"""
        gmt7 = pytz.timezone('Asia/Bangkok')
        
        # Create formatter with GMT+7 timestamp
        class GMT7Formatter(logging.Formatter):
            def formatTime(self, record, datefmt=None):
                dt = datetime.fromtimestamp(record.created, tz=gmt7)
                return dt.strftime('%Y-%m-%d %H:%M:%S GMT+7')
        
        # Setup transcription logger
        self.logger = logging.getLogger('transcription')
        self.logger.setLevel(getattr(logging, self.config['logging']['log_level']))
        
        handler = logging.FileHandler(
            os.path.join(self.config['paths']['logs_dir'], 'transcription.txt')
        )
        formatter = GMT7Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        self.logger.info("Audio transcriber initialized")
    
    def load_model(self):
        """Load Whisper model"""
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.logger.info(f"Loading Whisper model on {device}")
            
            self.whisper = pipeline(
                "automatic-speech-recognition",
                model=self.config['models']['whisper'],
                device=0 if device == "cuda" else -1
            )
            self.logger.info("Whisper model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load model: {str(e)}")
            raise
    
    def preprocess_audio(self, audio_path):
        """Basic audio preprocessing"""
        try:
            # Load audio
            audio, sr = librosa.load(audio_path, sr=self.config['audio']['sample_rate'])
            
            # Normalize if enabled
            if self.config['audio']['preprocessing']['normalize']:
                audio = librosa.util.normalize(audio)
            
            self.logger.info(f"Preprocessed audio: {len(audio)} samples at {sr} Hz")
            return audio, sr
            
        except Exception as e:
            self.logger.error(f"Audio preprocessing failed: {str(e)}")
            raise
    
    def transcribe(self, audio_path):
        """Transcribe audio file"""
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting transcription of: {audio_path}")
            
            # Check file exists and format
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            file_ext = os.path.splitext(audio_path)[1].lower()
            if file_ext not in self.config['audio']['supported_formats']:
                raise ValueError(f"Unsupported audio format: {file_ext}")
            
            # Preprocess audio
            audio, sr = self.preprocess_audio(audio_path)
            
            # Transcribe using preprocessed audio
            result = self.whisper(audio, return_timestamps=True)
            
            processing_time = time.time() - start_time
            
            # Extract information
            transcription = {
                'text': result['text'],
                'language': getattr(result, 'language', 'unknown'),
                'confidence': getattr(result, 'confidence', 0.0),
                'processing_time': processing_time,
                'file_path': audio_path,
                'timestamp': datetime.now(pytz.timezone('Asia/Bangkok')).isoformat()
            }
            
            self.logger.info(f"Transcription completed in {processing_time:.2f}s")
            self.logger.info(f"Detected language: {transcription['language']}")
            self.logger.info(f"Text length: {len(transcription['text'])} characters")
            
            return transcription
            
        except Exception as e:
            self.logger.error(f"Transcription failed: {str(e)}")
            raise
    
    def save_transcription(self, transcription, output_path=None):
        """Save transcription to file"""
        try:
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = os.path.join(
                    self.config['paths']['output_dir'], 
                    f"transcription_{timestamp}.json"
                )
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(transcription, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Transcription saved to: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to save transcription: {str(e)}")
            raise

if __name__ == "__main__":
    # Simple test
    transcriber = AudioTranscriber()
    print("Audio Transcriber initialized successfully!")
    print("Place audio files in ./data/input/ and use transcriber.transcribe(file_path)")
