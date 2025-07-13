import json
import os
import time
import logging
from datetime import datetime
import pytz
from transformers import pipeline
import torch

class TextTranslator:
    def __init__(self, config_path="config.json"):
        """Initialize the translator with configuration"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.setup_logging()
        self.load_model()
    
    def setup_logging(self):
        """Setup logging with GMT+7 timezone"""
        gmt7 = pytz.timezone('Asia/Bangkok')
        
        class GMT7Formatter(logging.Formatter):
            def formatTime(self, record, datefmt=None):
                dt = datetime.fromtimestamp(record.created, tz=gmt7)
                return dt.strftime('%Y-%m-%d %H:%M:%S GMT+7')
        
        self.logger = logging.getLogger('translation')
        self.logger.setLevel(getattr(logging, self.config['logging']['log_level']))
        
        handler = logging.FileHandler(
            os.path.join(self.config['paths']['logs_dir'], 'translation.txt')
        )
        formatter = GMT7Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        self.logger.info("Text translator initialized")
    
    def load_model(self):
        """Load translation model"""
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.logger.info(f"Loading translation model on {device}")
            
            self.translator = pipeline(
                "translation",
                model=self.config['models']['translation'],
                device=0 if device == "cuda" else -1
            )
            self.logger.info("Translation model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load translation model: {str(e)}")
            raise
    
    def translate(self, text, source_lang=None, target_lang=None):
        """Translate text between Vietnamese and English"""
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting translation of text: {text[:50]}...")
            
            # Source language should be provided from Whisper transcription
            if source_lang is None:
                self.logger.warning("No source language provided, defaulting to English")
                source_lang = "en"
            
            # Determine target language
            if target_lang is None:
                target_lang = "en" if source_lang == "vi" else "vi"
            
            # Skip translation if source and target are the same
            if source_lang == target_lang:
                self.logger.warning(f"Source and target languages are the same: {source_lang}")
                return {
                    'original_text': text,
                    'translated_text': text,
                    'source_language': source_lang,
                    'target_language': target_lang,
                    'confidence': 1.0,
                    'processing_time': 0.0,
                    'timestamp': datetime.now(pytz.timezone('Asia/Bangkok')).isoformat()
                }
            
            # Prepare input for NLLB model
            if source_lang == "vi" and target_lang == "en":
                src_lang_code = "vie_Latn"
                tgt_lang_code = "eng_Latn"
            elif source_lang == "en" and target_lang == "vi":
                src_lang_code = "eng_Latn"
                tgt_lang_code = "vie_Latn"
            else:
                raise ValueError(f"Unsupported language pair: {source_lang} -> {target_lang}")
            
            # Perform translation
            result = self.translator(
                text,
                src_lang=src_lang_code,
                tgt_lang=tgt_lang_code,
                max_length=512
            )
            
            processing_time = time.time() - start_time
            
            translation_result = {
                'original_text': text,
                'translated_text': result[0]['translation_text'],
                'source_language': source_lang,
                'target_language': target_lang,
                'confidence': getattr(result[0], 'score', 0.8),  # Default confidence
                'processing_time': processing_time,
                'timestamp': datetime.now(pytz.timezone('Asia/Bangkok')).isoformat()
            }
            
            self.logger.info(f"Translation completed in {processing_time:.2f}s")
            self.logger.info(f"Translation: {source_lang} -> {target_lang}")
            
            return translation_result
            
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
    # Simple test
    translator = TextTranslator()
    print("Text Translator initialized successfully!")
    
    # Test translation
    test_text = "Hello, how are you?"
    result = translator.translate(test_text)
    print(f"Original: {result['original_text']}")
    print(f"Translated: {result['translated_text']}")
    print(f"Language: {result['source_language']} -> {result['target_language']}")
