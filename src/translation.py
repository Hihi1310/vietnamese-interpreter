import json
import os
import time
from datetime import datetime
import pytz
from transformers import pipeline
import torch
from logger import setup_logger

class TextTranslator:
    def __init__(self, config_path="config.json"):
        """Initialize the translator with configuration"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.setup_logging()
        self.load_model()
    
    def setup_logging(self):
        """Setup logging using centralized logger"""
        log_file = os.path.join(self.config['paths']['logs_dir'], 'translation.txt')
        self.logger = setup_logger('translation', log_file, self.config['logging']['log_level'])
        self.logger.info("Text translator initialized")
    
    def load_model(self):
        """Load translation model"""
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.logger.info(f"Loading translation model on {device}")
            
            self.translator = pipeline(
                "translation",
                model=self.config['models']['translation'],
                device=0 if device == "cuda" else -1,
                token=self.config.get('huggingface_token', "")
            )
            self.logger.info("Translation model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load translation model: {str(e)}")
            raise
    
    def translate(self, text, source_language=None):
        """Translate text between Vietnamese and English"""
        start_time = time.time()
        
        try:
            # Auto-detect language if not provided
            if source_language is None:
                vietnamese_chars = 'àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđĐ'
                source_language = 'vi' if any(char in vietnamese_chars for char in text) else 'en'
            
            # Set translation direction
            if source_language == 'vi':
                src_lang_code, tgt_lang_code = "vie_Latn", "eng_Latn"
            else:
                src_lang_code, tgt_lang_code = "eng_Latn", "vie_Latn"
            
            # Perform translation
            result = self.translator(text, src_lang=src_lang_code, tgt_lang=tgt_lang_code, max_length=512)
            
            return {
                'raw_transcript': text,
                'translated_text': result[0]['translation_text'],
                'processing_time': time.time() - start_time,
                'timestamp': datetime.now(pytz.timezone('Asia/Bangkok')).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Translation failed: {str(e)}")
            raise
    
    def save_translation(self, translation_result, output_path=None):
        """Save translation to file"""
        try:
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = os.path.join(
                    self.config['paths']['output_dir'], 
                    f"translation_{timestamp}.json"
                )
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(translation_result, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Translation saved to: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to save translation: {str(e)}")
            raise

if __name__ == "__main__":
    translator = TextTranslator()
    
    # Test both directions
    vi_result = translator.translate("Xin chào")
    en_result = translator.translate("Hello")
    
    print(f"Vietnamese: {vi_result['raw_transcript']} -> {vi_result['translated_text']}")
    print(f"English: {en_result['raw_transcript']} -> {en_result['translated_text']}")
