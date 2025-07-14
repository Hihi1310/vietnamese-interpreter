import json
import os
import time
from datetime import datetime
import pytz
import google.generativeai as genai
from logger import setup_logger

class TextTranslator:
    def __init__(self, config_path=None, config_dict=None):
        """Initialize the translator with configuration"""
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
        log_file = os.path.join(self.config['paths']['logs_dir'], 'translation.txt')
        self.logger = setup_logger('translation', log_file, self.config['logging']['log_level'])
        self.logger.info("Translator init")
    
    def load_model(self):
        """Load Gemini model"""
        try:
            # Configure Gemini with API key
            api_key = self.config.get('gemini_api_key', "")
            if not api_key:
                raise ValueError("Gemini API key not found in config. Please add 'gemini_api_key' to your config.json")
            
            genai.configure(api_key=api_key)
            
            # Initialize the model
            model_name = self.config.get('models', {}).get('gemini', 'gemini-pro')
            self.model = genai.GenerativeModel(model_name)
            
            self.logger.info(f"Gemini '{model_name}' ready")
            
        except Exception as e:
            self.logger.error(f"Failed to load Gemini model: {str(e)}")
            raise
    
    def translate(self, text, source_language):
        """Translate text between Vietnamese and English using Gemini
        
        Args:
            text (str): Text to translate
            source_language (str): 'vi' or 'en' - REQUIRED, no auto-detection
        """
        start_time = time.time()
        
        try:
            # Validate source language
            if source_language not in ['vi', 'en']:
                raise ValueError("source_language must be 'vi' or 'en'. Auto-detection has been removed.")
            
            self.logger.info(f"Translating: {source_language} → {'en' if source_language == 'vi' else 'vi'}")
            
            # Set translation direction and create prompt
            if source_language == 'vi':
                target_language = 'en'
                prompt = f"Translate the following Vietnamese text to English. Handle any mixed English words naturally. Only provide the translation, no explanations:\n\n{text}"
            else:
                target_language = 'vi'
                prompt = f"Translate the following English text to Vietnamese. Handle any mixed Vietnamese words naturally. Only provide the translation, no explanations:\n\n{text}"
            
            # Generate translation using Gemini
            response = self.model.generate_content(prompt)
            translated_text = response.text.strip()
            
            processing_time = time.time() - start_time
            self.logger.info(f"Done: {processing_time:.2f}s")
            
            return {
                'raw_transcript': text,
                'translated_text': translated_text,
                'source_language': source_language,
                'target_language': target_language,
                'processing_time': processing_time,
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
            
            self.logger.info(f"Saved: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to save translation: {str(e)}")
            raise
    
    def translate_vietnamese_to_english(self, text):
        """Explicitly translate Vietnamese text to English"""
        return self.translate(text, source_language='vi')
    
    def translate_english_to_vietnamese(self, text):
        """Explicitly translate English text to Vietnamese"""
        return self.translate(text, source_language='en')

if __name__ == "__main__":
    translator = TextTranslator()
    
    # Test mixed language scenarios with explicit source language selection
    mixed_vi_text = "Tôi đang học programming và artificial intelligence"
    mixed_en_text = "I love Vietnamese phở and bánh mì"
    
    print("=== EXPLICIT LANGUAGE SELECTION ===")
    vi_to_en = translator.translate_vietnamese_to_english(mixed_vi_text)
    en_to_vi = translator.translate_english_to_vietnamese(mixed_en_text)
    
    print(f"VI->EN: {vi_to_en['raw_transcript']}")
    print(f"       -> {vi_to_en['translated_text']}")
    print(f"EN->VI: {en_to_vi['raw_transcript']}")
    print(f"       -> {en_to_vi['translated_text']}")
    
    print(f"\nProcessing times: VI->EN {vi_to_en['processing_time']:.2f}s, EN->VI {en_to_vi['processing_time']:.2f}s")
    
    # Direct method calls
    print("\n=== DIRECT METHOD CALLS ===")
    direct_vi = translator.translate(mixed_vi_text, 'vi')
    direct_en = translator.translate(mixed_en_text, 'en')
    print(f"Direct VI->EN: {direct_vi['translated_text']}")
    print(f"Direct EN->VI: {direct_en['translated_text']}")
