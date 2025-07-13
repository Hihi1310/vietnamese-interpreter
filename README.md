# Vietnamese Interpreter POC

A proof-of-concept bilingual interpreter for Vietnamese and English using OpenAI Whisper for transcription and Google Gemini Flash 2.0 for translation.

## 🚀 Key Features

- **High-Speed Translation**: Powered by Gemini Flash 2.0 for fast, accurate translation
- **Bilingual Support**: Vietnamese ↔ English with manual language selection
- **Mixed Language Handling**: Handles code-switching and technical terms naturally
- **Centralized Logging**: Clean, organized logging system with GMT+7 timestamps
- **User-Controlled Language**: No auto-detection - users specify source language explicitly

## 📁 Project Structure

```
vietnamese-interpreter/
├── data/
│   ├── input/          # Place audio files here for testing
│   └── output/         # Processed results saved here
├── models/             # Downloaded model cache
├── logs/               # Centralized logging with separate files
│   ├── transcription.txt  # Audio processing logs
│   ├── translation.txt    # Translation logs
│   └── system.txt         # Main system logs
├── src/
│   ├── transcription.py   # Whisper transcription module
│   ├── translation.py     # Gemini translation module
│   ├── logger.py          # Centralized logging setup
│   └── main.py           # Main application
├── config.json          # Configuration with API keys
└── requirements.txt     # Python dependencies
```

## ⚡ Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
pip install google-generativeai  # For Gemini support
```

### 2. Configure API Keys

Edit `config.json` and add your API keys:

```json
{
  "models": {
    "whisper": "openai/whisper-large-v3-turbo",
    "gemini": "gemini-2.0-flash-exp"
  },
  "huggingface_token": "hf_your_token_here",
  "gemini_api_key": "AIzaSyC-your_gemini_api_key_here"
}
```

**Get API Keys:**
- **Gemini API**: [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Hugging Face**: [HF Settings](https://huggingface.co/settings/tokens) (optional, for gated models)

### 3. Place Audio Files

Copy your audio files (WAV, MP3, M4A) to the `data/input/` directory.

### 4. Run the Interpreter

```bash
cd src
python main.py <audio_file> [source_language]
```

## 📖 Usage Examples

### Basic Usage (Auto-detect from transcription)
```bash
python main.py ../data/input/speech.wav
```

### Explicit Language Selection (Recommended)
```bash
# Vietnamese audio
python main.py ../data/input/vietnamese_speech.wav vi

# English audio
python main.py ../data/input/english_speech.wav en

# Mixed language (Vietnamese with English tech terms)
python main.py ../data/input/mixed_speech.wav vi
```

## 🔧 Translation API

The translation module supports explicit language selection:

```python
from translation import TextTranslator

translator = TextTranslator()

# Method 1: Direct calls
result = translator.translate("Xin chào", "vi")  # Vietnamese to English
result = translator.translate("Hello", "en")     # English to Vietnamese

# Method 2: Helper methods
vi_result = translator.translate_vietnamese_to_english("Tôi học programming")
en_result = translator.translate_english_to_vietnamese("I love phở")
```

## 📊 Output Format

Results are saved to `data/output/interpreter_result_TIMESTAMP.json`:

```json
{
  "input_file": "path/to/audio.wav",
  "transcription": {
    "text": "Transcribed text here",
    "language": "vi",
    "processing_time": 1.23,
    "timestamp": "2025-01-13T10:30:00+07:00"
  },
  "translation": {
    "raw_transcript": "Original text",
    "translated_text": "Translated text",
    "source_language": "vi",
    "target_language": "en",
    "processing_time": 0.85,
    "timestamp": "2025-01-13T10:30:01+07:00"
  },
  "total_processing_time": 2.08
}
```

## ⚙️ Configuration

### Key Settings in `config.json`:

```json
{
  "models": {
    "whisper": "openai/whisper-large-v3-turbo",
    "gemini": "gemini-2.0-flash-exp"
  },
  "huggingface_token": "",
  "gemini_api_key": "",
  "audio": {
    "sample_rate": 16000,
    "supported_formats": [".wav", ".mp3", ".m4a"]
  },
  "logging": {
    "log_level": "INFO"
  }
}
```

## 🏗️ Architecture Changes

### From Previous Version:
- ❌ **Removed**: Hugging Face NLLB translation model
- ❌ **Removed**: Auto language detection (error-prone)
- ❌ **Removed**: Duplicate logging code across modules

### New Implementation:
- ✅ **Added**: Google Gemini Flash 2.0 for translation
- ✅ **Added**: Mandatory source language selection
- ✅ **Added**: Centralized logging system (`logger.py`)
- ✅ **Added**: Mixed language handling support
- ✅ **Added**: Command-line language selection

## 🎯 Benefits

1. **Faster Translation**: Gemini Flash 2.0 optimized for speed
2. **Better Quality**: Natural handling of mixed languages and cultural terms
3. **User Control**: Explicit language selection prevents auto-detection errors
4. **Cleaner Code**: Centralized logging, no code duplication
5. **Cost Effective**: API-based, no local GPU requirements for translation

## 📋 System Requirements

- **Python**: 3.8+
- **Internet**: Required for Gemini API calls
- **Memory**: 4GB+ RAM
- **GPU**: Optional for Whisper (CPU fallback available)

## 🔧 Troubleshooting

### Common Issues:

1. **Missing API Key**: Add `gemini_api_key` to `config.json`
2. **Invalid Language**: Use only `'vi'` or `'en'` for source language
3. **Audio Format**: Convert unsupported formats to WAV
4. **Network Issues**: Check internet connection for Gemini API

### Debug Information:
- Check logs in `./logs/` directory
- Use `INFO` log level for detailed processing info
- Translation errors are logged in `translation.txt`

## 🎪 Example Mixed Language Scenarios

```bash
# Vietnamese with English programming terms
python main.py tech_talk.wav vi

# English with Vietnamese cultural terms  
python main.py food_review.wav en

# Business meeting with code-switching
python main.py meeting.wav vi  # Primary language is Vietnamese
```

The system now handles these scenarios naturally without making incorrect language assumptions!
