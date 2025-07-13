import json
import os
import time
from datetime import datetime
import pytz
import librosa
from transformers import pipeline
import torch
from logger import setup_logger

class AudioTranscriber:
    def __init__(self, config_path="config.json"):
        """Initialize the transcriber with configuration"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.setup_logging()
        self.load_model()
    
    def setup_logging(self):
        """Setup logging using centralized logger"""
        log_file = os.path.join(self.config['paths']['logs_dir'], 'transcription.txt')
        self.logger = setup_logger('transcription', log_file, self.config['logging']['log_level'])
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
            
            # Transcribe with return_timestamps and language detection
            result = self.whisper(audio_path, return_timestamps=True, generate_kwargs={"language": None})
            
            processing_time = time.time() - start_time
            
            # Try to detect language from the result or use manual detection
            detected_language = 'unknown'
            if 'chunks' in result and result['chunks']:
                # Check if language info is in chunks
                first_chunk = result['chunks'][0]
                if 'language' in first_chunk:
                    detected_language = first_chunk['language']
            
            # If still unknown, try to infer from text content or set default
            if detected_language == 'unknown':
                text = result.get('text', '').strip()
                if text:
                    # Simple heuristic: if text contains Vietnamese characters, assume Vietnamese
                    vietnamese_chars = 'àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđĐ'
                    if any(char in vietnamese_chars for char in text):
                        detected_language = 'vi'
                    else:
                        # Default to English for bilingual Vietnamese-English setting
                        detected_language = 'en'
                else:
                    detected_language = 'en'  # Default assumption
            
            # Extract information for evaluation
            transcription = {
                'text': result['text'],
                'language': detected_language,
                'processing_time': processing_time,
                'file_path': audio_path,
                'timestamp': datetime.now(pytz.timezone('Asia/Bangkok')).isoformat()
            }
            
            self.logger.info(f"Transcription completed in {processing_time:.2f}s")
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
